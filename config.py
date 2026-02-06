import os

class Config:
    # Database
    DATABASE = 'data/database.db'

    # Security (for local network only)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    PASSWORD = 'your_password_here'  # Simple password for access

    # Flask
    DEBUG = True
