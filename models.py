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

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            for_everyone BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Task assignments (only used when for_everyone is false)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(task_id, user_id)
        )
    ''')

    # Schedules table - supports all frequency patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            schedule_type TEXT NOT NULL,

            -- For interval-based schedules (every X days/weeks/months)
            interval INTEGER,
            start_date DATE,

            -- For day-of-week based schedules
            day_of_week TEXT,

            -- For ordinal schedules (first/last Monday of month)
            ordinal TEXT,
            even_odd_months TEXT,

            -- For monthly date schedules (15th of each month)
            day_of_month INTEGER,

            -- For first/last day of interval months
            first_or_last TEXT,

            -- For "X times per month"
            times_count INTEGER,

            -- For yearly schedules
            week_of_year INTEGER,
            month INTEGER,
            specific_date DATE,

            -- For seasonal schedules
            season TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

def add_user(first_name, password):
    """Add a new user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (first_name, password) VALUES (?, ?)', (first_name, password))
    conn.commit()
    conn.close()
    print(f"User '{first_name}' added successfully")

def authenticate_user(first_name, password):
    """Check if user credentials are valid"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE first_name = ? AND password = ?', (first_name, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

if __name__ == '__main__':
    init_db()
