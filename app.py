from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from datetime import datetime, timedelta
import os
from models import (
    authenticate_user, get_all_users, create_task, update_task, get_task,
    get_task_assignments, delete_task, add_schedule, get_schedules, delete_schedule,
    get_schedule_description, get_all_tasks_alphabetical, get_tasks_for_date_range,
    calculate_next_occurrence, get_ordinal, get_user_by_id, update_user_password
)

app = Flask(__name__)
app.secret_key = 'change-this-to-something-random'  # For session management

# Simple auth decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin auth decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        if session.get('first_name', '').lower() != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        password = request.form.get('password')

        if authenticate_user(first_name, password):
            session['logged_in'] = True
            session['first_name'] = first_name
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('first_name', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # Get tasks for next 7 days
    today = datetime.now().date()
    end_date = today + timedelta(days=6)

    occurrences = get_tasks_for_date_range(today, end_date)

    # Group by date
    days = {}
    for i in range(7):
        date = today + timedelta(days=i)
        days[date] = {
            'day_name': date.strftime('%A'),
            'date_str': date.strftime('%m/%d/%Y'),
            'tasks': []
        }

    for occ in occurrences:
        if occ['date'] in days:
            days[occ['date']]['tasks'].append(occ)

    days_list = [{'date': k, 'data': v} for k, v in sorted(days.items())]

    return render_template('index.html', days=days_list)

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task_route():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        for_everyone = request.form.get('for_everyone') == '1'

        user_ids = []
        if not for_everyone:
            user_ids = request.form.getlist('user_ids')

        created_by = session.get('first_name')
        task_id = create_task(title, description, for_everyone, user_ids, created_by)

        # Handle schedules (we'll add UI for this later, for now just redirect)
        return redirect(url_for('edit_task_route', task_id=task_id))

    users = get_all_users()
    return render_template('create_task.html', users=users)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task_route(task_id):
    task = get_task(task_id)
    if not task:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'delete_task' in request.form:
            delete_task(task_id)
            return redirect(url_for('all_tasks'))

        if 'delete_schedule' in request.form:
            schedule_id = request.form.get('delete_schedule')
            delete_schedule(schedule_id)
            return redirect(url_for('edit_task_route', task_id=task_id))

        if 'add_schedule' in request.form:
            schedule_type = request.form.get('schedule_type')
            kwargs = {}

            if schedule_type in ['interval_days', 'interval_weeks', 'interval_months']:
                kwargs['interval'] = int(request.form.get('interval'))
                kwargs['start_date'] = request.form.get('start_date')

            elif schedule_type == 'weekly':
                kwargs['day_of_week'] = request.form.get('day_of_week')

            elif schedule_type == 'ordinal_monthly':
                kwargs['ordinal'] = request.form.get('ordinal')
                kwargs['day_of_week'] = request.form.get('day_of_week')

            elif schedule_type == 'ordinal_bimonthly':
                kwargs['ordinal'] = request.form.get('ordinal')
                kwargs['day_of_week'] = request.form.get('day_of_week')
                kwargs['even_odd_months'] = request.form.get('even_odd_months')

            elif schedule_type == 'monthly_date':
                kwargs['day_of_month'] = int(request.form.get('day_of_month'))

            elif schedule_type == 'first_last_interval_months':
                kwargs['first_or_last'] = request.form.get('first_or_last')
                kwargs['interval'] = int(request.form.get('interval'))
                kwargs['start_date'] = request.form.get('start_date')

            elif schedule_type == 'times_per_month':
                kwargs['times_count'] = int(request.form.get('times_count'))

            elif schedule_type == 'yearly_week':
                kwargs['week_of_year'] = int(request.form.get('week_of_year'))
                kwargs['month'] = int(request.form.get('month'))

            elif schedule_type == 'yearly_date':
                kwargs['month'] = int(request.form.get('month'))
                kwargs['day_of_month'] = int(request.form.get('day_of_month'))

            elif schedule_type == 'seasonal':
                kwargs['season'] = request.form.get('season')

            elif schedule_type == 'one_time':
                kwargs['specific_date'] = request.form.get('specific_date')

            add_schedule(task_id, schedule_type, **kwargs)
            return redirect(url_for('edit_task_route', task_id=task_id))

        else:
            title = request.form.get('title')
            description = request.form.get('description', '')
            for_everyone = request.form.get('for_everyone') == '1'

            user_ids = []
            if not for_everyone:
                user_ids = request.form.getlist('user_ids')

            update_task(task_id, title, description, for_everyone, user_ids)
            return redirect(url_for('edit_task_route', task_id=task_id))

    users = get_all_users()
    assigned_users = get_task_assignments(task_id)
    schedules = get_schedules(task_id)

    schedule_list = []
    for s in schedules:
        schedule_list.append({
            'id': s['id'],
            'description': get_schedule_description(s)
        })

    return render_template('edit_task.html', task=task, users=users,
                          assigned_users=assigned_users, schedules=schedule_list)

@app.route('/tasks/all')
@login_required
def all_tasks():
    view = request.args.get('view', 'alphabetical')
    page = int(request.args.get('page', 1))
    show_all = request.args.get('show_all', '0') == '1'

    if view == 'alphabetical':
        tasks = get_all_tasks_alphabetical()
    else:
        # Chronological view - get all tasks with occurrences for next 6 months
        today = datetime.now().date()
        end_date = today + timedelta(days=180)
        occurrences = get_tasks_for_date_range(today, end_date)

        tasks = []
        for occ in occurrences:
            tasks.append({
                'id': occ['task_id'],
                'title': occ['task_title'],
                'date': occ['date'].strftime('%m/%d/%Y')
            })

    total_tasks = len(tasks)
    per_page = 50

    if show_all:
        paginated_tasks = tasks
        total_pages = 1
    else:
        start = (page - 1) * per_page
        end = start + per_page
        paginated_tasks = tasks[start:end]
        total_pages = (total_tasks + per_page - 1) // per_page

    return render_template('all_tasks.html', tasks=paginated_tasks, view=view,
                          page=page, total_pages=total_pages, show_all=show_all,
                          total_tasks=total_tasks)

@app.route('/tasks/view')
@login_required
def view_tasks():
    # Get date range from query params
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    month_str = request.args.get('month')

    if month_str:
        # Month format: YYYY-MM
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    elif start_str and end_str:
        start_date = datetime.strptime(start_str, '%m%d%Y').date()
        end_date = datetime.strptime(end_str, '%m%d%Y').date()
    else:
        # Default to current month
        today = datetime.now().date()
        start_date = datetime(today.year, today.month, 1).date()
        if today.month == 12:
            end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)

    occurrences = get_tasks_for_date_range(start_date, end_date)

    # Format for print view
    print_lines = []
    for occ in occurrences:
        date_str = occ['date'].strftime('%m/%d/%Y')
        day_str = occ['date'].strftime('%a').upper()
        print_lines.append(f"{date_str} {day_str} {occ['task_title']}")

    return render_template('view_tasks.html', print_lines=print_lines,
                          start_date=start_date, end_date=end_date)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    users = get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        if new_password:
            update_user_password(user_id, new_password)
            return redirect(url_for('admin_users'))

    return render_template('edit_user.html', user=user)

@app.context_processor
def utility_processor():
    """Make utility functions available to all templates"""
    return dict(get_ordinal=get_ordinal)

if __name__ == '__main__':
    # Run on all network interfaces so other devices can access
    app.run(host='0.0.0.0', port=5000, debug=True)
