import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Tuple

import asyncpg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool (will be initialized on startup)
pool: Optional[asyncpg.Pool] = None


async def init_pool():
    """Initialize connection pool"""
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL, min_size=1, max_size=10, command_timeout=60
    )
    print("Database pool created")


async def close_pool():
    """Close connection pool"""
    global pool
    if pool:
        await pool.close()
        print("Database pool closed")


@asynccontextmanager
async def get_connection():
    """Get a connection from the pool"""
    async with pool.acquire() as connection:
        yield connection


# Database setup
async def init_database():
    """Initialize database tables"""
    async with pool.acquire() as conn:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                firstname TEXT,
                original_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create raw_messages table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                tg_message_id BIGINT,
                raw_message TEXT,
                sent_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create extracted_data table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS extracted_data (
                id SERIAL PRIMARY KEY,
                raw_message_id INTEGER,
                json_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create transactions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                extracted_data_id INTEGER,
                amount REAL,
                description TEXT,
                type TEXT,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        print("Database tables created successfully")


# Database functions
async def is_user_exists(user_id: int) -> Optional[Tuple[str, str]]:
    """Check if user exists in database"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT firstname, original_name FROM users WHERE user_id = $1", user_id
        )
        if row:
            return (row["firstname"], row["original_name"])
        return None


async def save_user(user_id: int, firstname: str, original_name: str, username: str):
    """Save new user to database"""
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, firstname, original_name, username) VALUES ($1, $2, $3, $4)",
            user_id,
            firstname,
            original_name,
            username,
        )


async def update_user(user_id: int, firstname: str):
    """Update user's firstname"""
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET firstname = $1 WHERE user_id = $2", firstname, user_id
        )


async def save_message(
    user_id: int, tg_message_id: int, message: str, sent_time: str
) -> int:
    """Save raw_message"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO raw_messages (tg_message_id, user_id, raw_message, sent_time) VALUES ($1, $2, $3, $4) RETURNING id",
            tg_message_id,
            user_id,
            message,
            sent_time,
        )
        return row["id"]


async def save_extracted_data(raw_message_id: int, json_transactions: str) -> int:
    """Insert result of raw_message from AI"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO extracted_data (raw_message_id, json_data) VALUES ($1, $2) RETURNING id",
            raw_message_id,
            json_transactions,
        )
        return row["id"]


async def save_transactions(
    transactions: List[dict],
    user_id: int,
    extracted_data_id: int,
    date: Optional[str] = None,
):
    """Insert transactions"""
    async with pool.acquire() as conn:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Prepare data for batch insert
        transactions_list = [
            (
                user_id,
                extracted_data_id,
                transaction["amount"],
                transaction["description"],
                transaction["type"],
                date,
            )
            for transaction in transactions
        ]

        # Use executemany for batch insert
        await conn.executemany(
            "INSERT INTO transactions (user_id, extracted_data_id, amount, description, type, date) VALUES ($1, $2, $3, $4, $5, $6)",
            transactions_list,
        )


async def get_transactions(user_id: int, date: str) -> List[Tuple]:
    """Get transactions"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT amount, type FROM transactions WHERE date = $1 AND user_id = $2",
            date,
            user_id,
        )
        return [(row["amount"], row["type"]) for row in rows]


async def get_raw_message_by_id(raw_message_id: int) -> Optional[Tuple[int, str]]:
    """Get raw message by id"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id, raw_message FROM raw_messages WHERE id = $1",
            raw_message_id,
        )
        if row:
            return (row["user_id"], row["raw_message"])
        return None


async def get_basic_stats() -> Tuple[int, int, int]:
    """Get basic stats"""
    async with pool.acquire() as conn:
        user_count = await conn.fetchval("SELECT count(user_id) FROM users")
        raw_message_count = await conn.fetchval("SELECT count(id) FROM raw_messages")
        transaction_count = await conn.fetchval("SELECT count(id) FROM transactions")
        return (user_count, raw_message_count, transaction_count)


async def get_users_ids() -> List[int]:
    """Get all users ids"""
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
        return [row["user_id"] for row in rows]
