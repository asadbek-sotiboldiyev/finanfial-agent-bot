import sqlite3


# Database setup
def init_database():
    """Initialize database tables"""
    conn = sqlite3.connect("my_database.db")

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
            tg_message_id INTEGER,
            raw_message TEXT,
            sent_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create extracted_transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_transactions (
            id INTEGER PRIMARY KEY,
            raw_message_id INTEGER,
            extracted_datas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            extracted_transation_id INTEGER,
            amount REAL,
            description TEXT,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES users(chat_id)
        )
    """)

    conn.commit()
    conn.close()


# Database functions
def is_user_exists(user_id):
    """Check if user exists in database"""
    conn = sqlite3.connect("my_database.db")

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, original_name FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    print(exists)
    conn.close()
    return not (exists is None)


def save_user(user_id, firstname, original_name, username):
    """Save new user to database"""
    conn = sqlite3.connect("my_database.db")

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, firstname, original_name, username) VALUES (?, ?, ?, ?)",
        (user_id, firstname, original_name, username),
    )
    conn.commit()
    conn.close()

def uopdate_user(user_id, firstname):
    """Update user's firstname"""
    conn = sqlite3.connect("my_database.db")

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET firstname = ? WHERE user_id = ?",
        (firstname, user_id),
    )
    conn.commit()
    conn.close()

def save_message(user_id, message):
    return
