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
            created_by TEXT,
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
            end_date DATE,

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
    """Check if user credentials are valid (case-insensitive username and password)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE LOWER(first_name) = LOWER(?)', (first_name,))
    user = cursor.fetchone()
    conn.close()

    if user and user['password'].lower() == password.lower():
        return True
    return False

def get_ordinal(n):
    """Convert number to ordinal string (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def normalize_task_title(title):
    """Normalize task title to sentence case, preserving mid-sentence all-caps words"""
    if not title:
        return title

    # Check if entire title is all caps (only considering letters)
    letters = [c for c in title if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        # All caps - convert to pure sentence case
        return title[0].upper() + title[1:].lower()

    # Not all caps - preserve mid-sentence all-caps words
    words = title.split()
    if not words:
        return title

    result = []
    for i, word in enumerate(words):
        if i == 0:
            # First word - sentence case
            if len(word) > 0:
                result.append(word[0].upper() + word[1:].lower())
            else:
                result.append(word)
        else:
            # Mid-sentence word
            word_letters = [c for c in word if c.isalpha()]
            if word_letters and all(c.isupper() for c in word_letters):
                # All caps word - preserve it
                result.append(word)
            else:
                # Not all caps - lowercase it
                result.append(word.lower())

    return ' '.join(result)

def get_all_users():
    """Get all users"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY first_name')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    """Get a user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_password(user_id, new_password):
    """Update a user's password"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
    conn.commit()
    conn.close()

def create_task(title, description, for_everyone, user_ids=None, created_by=None):
    """Create a new task"""
    title = normalize_task_title(title)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, for_everyone, created_by) VALUES (?, ?, ?, ?)',
        (title, description, for_everyone, created_by)
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
    title = normalize_task_title(title)
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
        desc = f"every {schedule['interval']} days"
        if schedule['end_date']:
            desc += f" (until {schedule['end_date']})"
        return desc
    elif st == 'interval_weeks':
        desc = f"every {schedule['interval']} weeks"
        if schedule['end_date']:
            desc += f" (until {schedule['end_date']})"
        return desc
    elif st == 'interval_months':
        desc = f"every {schedule['interval']} months"
        if schedule['end_date']:
            desc += f" (until {schedule['end_date']})"
        return desc
    elif st == 'weekly':
        return f"weekly on {schedule['day_of_week']}"
    elif st == 'ordinal_monthly':
        return f"{schedule['ordinal']} {schedule['day_of_week']} of each month"
    elif st == 'ordinal_bimonthly':
        return f"{schedule['ordinal']} {schedule['day_of_week']} of {schedule['even_odd_months']} months"
    elif st == 'monthly_date':
        return f"monthly on the {get_ordinal(schedule['day_of_month'])}"
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
        # Check end_date if specified
        if schedule['end_date']:
            end = datetime.strptime(schedule['end_date'], '%Y-%m-%d').date()
            if next_occ > end:
                return None
        return next_occ

    elif st == 'interval_weeks':
        start = datetime.strptime(schedule['start_date'], '%Y-%m-%d').date()
        days_diff = (from_date - start).days
        if days_diff < 0:
            return start
        interval = schedule['interval']
        weeks = (days_diff // 7) // interval + 1
        next_occ = start + timedelta(weeks=weeks * interval)
        # Check end_date if specified
        if schedule['end_date']:
            end = datetime.strptime(schedule['end_date'], '%Y-%m-%d').date()
            if next_occ > end:
                return None
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
        # Check end_date if specified
        if schedule['end_date']:
            end = datetime.strptime(schedule['end_date'], '%Y-%m-%d').date()
            if next_occ > end:
                return None
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
