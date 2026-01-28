"""
Migration script to add end_date column to schedules table
"""
import sqlite3
from config import Config

def migrate():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(schedules)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'end_date' not in columns:
        print("Adding end_date column to schedules table...")
        cursor.execute("ALTER TABLE schedules ADD COLUMN end_date TEXT")
        conn.commit()
        print("Migration completed successfully!")
    else:
        print("end_date column already exists, no migration needed.")

    conn.close()

if __name__ == '__main__':
    migrate()
