import sqlite3
from config import Config

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Example table - modify as needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == '__main__':
    init_db()
