import sqlite3
from datetime import datetime

DBNAME = "my_database.db"


# Database setup
def init_database():
    """Initialize database tables"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                firstname TEXT,
                original_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    # Create messages table
    cursor.execute("""
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY,
            raw_message_id INTEGER,
            json_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create transactions table
    cursor.execute("""
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

    conn.commit()
    conn.close()


# Database functions
def is_user_exists(user_id):
    """Check if user exists in database"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "SELECT firstname, original_name FROM users WHERE user_id = ?", (user_id,)
    )
    exists = cursor.fetchone()
    conn.close()
    return exists


def save_user(user_id, firstname, original_name, username):
    """Save new user to database"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, firstname, original_name, username) VALUES (?, ?, ?, ?)",
        (user_id, firstname, original_name, username),
    )
    conn.commit()
    conn.close()


def update_user(user_id, firstname):
    """Update user's firstname"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET firstname = ? WHERE user_id = ?",
        (firstname, user_id),
    )
    conn.commit()
    conn.close()


def save_message(user_id, tg_message_id, message, sent_time):
    """Save raw_message"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO raw_messages (tg_message_id, user_id, raw_message, sent_time) VALUES (?, ?, ?, ?)",
        (tg_message_id, user_id, message, sent_time),
    )
    raw_message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return raw_message_id


def save_extracted_data(raw_message_id, json_transactions):
    """Insert result of raw_message from AI"""
    conn = sqlite3.connect(DBNAME)

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO extracted_data (raw_message_id, json_data) VALUES (?, ?)",
        (raw_message_id, json_transactions),
    )
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_transactions(transactions, user_id, extracted_data_id, date=None):
    """Insert transactions"""
    conn = sqlite3.connect(DBNAME)
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

    # Create a cursor object
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO transactions (user_id, extracted_data_id, amount, description, type, date) VALUES (?, ?, ?, ?, ?, ?)",
        transactions_list,
    )
    conn.commit()
    conn.close()


def get_transactions(user_id, date):
    """Get transactions"""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    conn.set_trace_callback(lambda query: print(f"Executing query: {query}"))
    cursor.execute(
        "SELECT amount, type FROM transactions WHERE date = ? AND user_id = ?",
        (
            date,
            user_id,
        ),
    )
    transactions = cursor.fetchall()
    conn.close()
    return transactions
