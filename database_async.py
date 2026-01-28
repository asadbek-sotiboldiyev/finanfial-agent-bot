from datetime import datetime

import aiosqlite

DBNAME = "my_database.db"


# Database setup
async def init_database():
    """Initialize database tables"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()

        # Create users table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                firstname TEXT,
                original_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create messages table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                tg_message_id INTEGER,
                raw_message TEXT,
                sent_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create extracted_data table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_data (
                id INTEGER PRIMARY KEY,
                raw_message_id INTEGER,
                json_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create transactions table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                extracted_data_id INTEGER,
                amount REAL,
                description TEXT,
                type TEXT,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await conn.commit()


# Database functions
async def is_user_exists(user_id):
    """Check if user exists in database"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT firstname, original_name FROM users WHERE user_id = ?", (user_id,)
        )
        exists = await cursor.fetchone()
        return exists


async def save_user(user_id, firstname, original_name, username):
    """Save new user to database"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "INSERT INTO users (user_id, firstname, original_name, username) VALUES (?, ?, ?, ?)",
            (user_id, firstname, original_name, username),
        )
        await conn.commit()


async def update_user(user_id, firstname):
    """Update user's firstname"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "UPDATE users SET firstname = ? WHERE user_id = ?",
            (firstname, user_id),
        )
        await conn.commit()


async def save_message(user_id, tg_message_id, message, sent_time):
    """Save raw_message"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "INSERT INTO raw_messages (tg_message_id, user_id, raw_message, sent_time) VALUES (?, ?, ?, ?)",
            (tg_message_id, user_id, message, sent_time),
        )
        raw_message_id = cursor.lastrowid
        await conn.commit()
        return raw_message_id


async def save_extracted_data(raw_message_id, json_transactions):
    """Insert result of raw_message from AI"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "INSERT INTO extracted_data (raw_message_id, json_data) VALUES (?, ?)",
            (raw_message_id, json_transactions),
        )
        row_id = cursor.lastrowid
        await conn.commit()
        return row_id


async def save_transactions(transactions, user_id, extracted_data_id, date=None):
    """Insert transactions"""
    async with aiosqlite.connect(DBNAME) as conn:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        transactions_list = []
        for transaction in transactions:
            transactions_list.append(
                (
                    user_id,
                    extracted_data_id,
                    transaction["amount"],
                    transaction["description"],
                    transaction["type"],
                    date,
                )
            )

        cursor = await conn.cursor()
        await cursor.executemany(
            "INSERT INTO transactions (user_id, extracted_data_id, amount, description, type, date) VALUES (?, ?, ?, ?, ?, ?)",
            transactions_list,
        )
        await conn.commit()


async def get_transactions(user_id, date):
    """Get transactions"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        # Note: aiosqlite doesn't support set_trace_callback
        # You can use logging instead for debugging
        await cursor.execute(
            "SELECT amount, type FROM transactions WHERE date = ? AND user_id = ?",
            (
                date,
                user_id,
            ),
        )
        transactions = await cursor.fetchall()
        return transactions


async def get_raw_message_by_id(raw_message_id):
    """Get raw message by id"""
    async with aiosqlite.connect(DBNAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT user_id, raw_message FROM raw_messages WHERE id = ?",
            (raw_message_id,),
        )
        raw_message = await cursor.fetchone()
        return raw_message
