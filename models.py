import sqlite3
from datetime import datetime, timedelta
from calendar import monthrange
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

def get_all_users():
    """Get all users"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY first_name')
    users = cursor.fetchall()
    conn.close()
    return users

def create_task(title, description, for_everyone, user_ids=None):
    """Create a new task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, for_everyone) VALUES (?, ?, ?)',
        (title, description, for_everyone)
    )
    task_id = cursor.lastrowid

    if not for_everyone and user_ids:
        for user_id in user_ids:
            cursor.execute(
                'INSERT INTO task_assignments (task_id, user_id) VALUES (?, ?)',
                (task_id, user_id)
            )

    conn.commit()
    conn.close()
    return task_id

def update_task(task_id, title, description, for_everyone, user_ids=None):
    """Update an existing task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET title = ?, description = ?, for_everyone = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, description, for_everyone, task_id)
    )

    # Remove old assignments
    cursor.execute('DELETE FROM task_assignments WHERE task_id = ?', (task_id,))

    # Add new assignments
    if not for_everyone and user_ids:
        for user_id in user_ids:
            cursor.execute(
                'INSERT INTO task_assignments (task_id, user_id) VALUES (?, ?)',
                (task_id, user_id)
            )

    conn.commit()
    conn.close()

def get_task(task_id):
    """Get a task by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def get_task_assignments(task_id):
    """Get user IDs assigned to a task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM task_assignments WHERE task_id = ?', (task_id,))
    assignments = [row['user_id'] for row in cursor.fetchall()]
    conn.close()
    return assignments

def delete_task(task_id):
    """Delete a task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def add_schedule(task_id, schedule_type, **kwargs):
    """Add a schedule to a task"""
    conn = get_db()
    cursor = conn.cursor()

    fields = ['task_id', 'schedule_type']
    values = [task_id, schedule_type]

    for key, value in kwargs.items():
        if value is not None:
            fields.append(key)
            values.append(value)

    placeholders = ', '.join(['?'] * len(values))
    field_names = ', '.join(fields)

    cursor.execute(
        f'INSERT INTO schedules ({field_names}) VALUES ({placeholders})',
        values
    )

    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

def get_schedules(task_id):
    """Get all schedules for a task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schedules WHERE task_id = ?', (task_id,))
    schedules = cursor.fetchall()
    conn.close()
    return schedules

def delete_schedule(schedule_id):
    """Delete a schedule"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
    conn.commit()
    conn.close()

def get_schedule_description(schedule):
    """Generate a human-readable description of a schedule"""
    st = schedule['schedule_type']

    if st == 'interval_days':
        return f"every {schedule['interval']} days"
    elif st == 'interval_weeks':
        return f"every {schedule['interval']} weeks"
    elif st == 'interval_months':
        return f"every {schedule['interval']} months"
    elif st == 'weekly':
        return f"weekly on {schedule['day_of_week']}"
    elif st == 'ordinal_monthly':
        return f"{schedule['ordinal']} {schedule['day_of_week']} of each month"
    elif st == 'ordinal_bimonthly':
        return f"{schedule['ordinal']} {schedule['day_of_week']} of {schedule['even_odd_months']} months"
    elif st == 'monthly_date':
        return f"monthly on the {schedule['day_of_month']}th"
    elif st == 'first_of_month':
        return "first day of each month"
    elif st == 'last_of_month':
        return "last day of each month"
    elif st == 'first_last_interval_months':
        return f"{schedule['first_or_last']} day of every {schedule['interval']} months"
    elif st == 'times_per_month':
        return f"{schedule['times_count']} times per month"
    elif st == 'yearly_week':
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        return f"yearly in week {schedule['week_of_year']} of {months[schedule['month']]}"
    elif st == 'yearly_date':
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        return f"yearly on {months[schedule['month']]} {schedule['day_of_month']}"
    elif st == 'seasonal':
        return f"seasonal ({schedule['season']})"
    elif st == 'one_time':
        return f"one time on {schedule['specific_date']}"
    else:
        return "unknown schedule"

def get_all_tasks_alphabetical():
    """Get all tasks alphabetically"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY title')
    tasks = cursor.fetchall()

    task_list = []
    for task in tasks:
        schedules = get_schedules(task['id'])
        schedule_desc = ', '.join([get_schedule_description(s) for s in schedules])
        task_list.append({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'schedule_desc': schedule_desc
        })

    conn.close()
    return task_list

def calculate_next_occurrence(schedule, from_date):
    """Calculate the next occurrence of a schedule from a given date"""
    st = schedule['schedule_type']

    if st == 'interval_days':
        start = datetime.strptime(schedule['start_date'], '%Y-%m-%d').date()
        days_diff = (from_date - start).days
        if days_diff < 0:
            return start
        interval = schedule['interval']
        next_occ = start + timedelta(days=((days_diff // interval) + 1) * interval)
        return next_occ

    elif st == 'interval_weeks':
        start = datetime.strptime(schedule['start_date'], '%Y-%m-%d').date()
        days_diff = (from_date - start).days
        if days_diff < 0:
            return start
        interval = schedule['interval']
        weeks = (days_diff // 7) // interval + 1
        next_occ = start + timedelta(weeks=weeks * interval)
        return next_occ

    elif st == 'interval_months':
        start = datetime.strptime(schedule['start_date'], '%Y-%m-%d').date()
        if from_date < start:
            return start
        interval = schedule['interval']
        months_diff = (from_date.year - start.year) * 12 + from_date.month - start.month
        next_month_count = (months_diff // interval + 1) * interval
        next_year = start.year + (start.month + next_month_count - 1) // 12
        next_month = (start.month + next_month_count - 1) % 12 + 1
        next_occ = datetime(next_year, next_month, start.day).date()
        return next_occ

    elif st == 'weekly':
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        target_day = days.index(schedule['day_of_week'])
        current_day = from_date.weekday()
        days_ahead = (target_day - current_day) % 7
        if days_ahead == 0:
            days_ahead = 7
        return from_date + timedelta(days=days_ahead)

    elif st == 'monthly_date':
        day = schedule['day_of_month']
        if from_date.day < day:
            return datetime(from_date.year, from_date.month, day).date()
        else:
            next_month = from_date.month + 1
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            return datetime(next_year, next_month, day).date()

    elif st == 'first_of_month':
        if from_date.day == 1:
            next_month = from_date.month + 1
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            return datetime(next_year, next_month, 1).date()
        else:
            next_month = from_date.month + 1
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            return datetime(next_year, next_month, 1).date()

    elif st == 'last_of_month':
        _, last_day = monthrange(from_date.year, from_date.month)
        if from_date.day < last_day:
            return datetime(from_date.year, from_date.month, last_day).date()
        else:
            next_month = from_date.month + 1
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            _, last_day = monthrange(next_year, next_month)
            return datetime(next_year, next_month, last_day).date()

    elif st == 'one_time':
        return datetime.strptime(schedule['specific_date'], '%Y-%m-%d').date()

    return None

def get_tasks_for_date_range(start_date, end_date):
    """Get all task occurrences within a date range"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY title')
    tasks = cursor.fetchall()

    occurrences = []

    for task in tasks:
        schedules = get_schedules(task['id'])
        for schedule in schedules:
            current_date = start_date
            while current_date <= end_date:
                next_occ = calculate_next_occurrence(schedule, current_date)
                if next_occ and next_occ <= end_date:
                    occurrences.append({
                        'date': next_occ,
                        'task_id': task['id'],
                        'task_title': task['title']
                    })
                    current_date = next_occ + timedelta(days=1)
                else:
                    break

    conn.close()
    occurrences.sort(key=lambda x: x['date'])
    return occurrences

if __name__ == '__main__':
    init_db()
