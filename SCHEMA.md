# Database Schema Documentation

## Tables Overview

### users
- `id` - Primary key
- `first_name` - User's first name
- `password` - User's password (currently plain text)
- `created_at` - Timestamp

### tasks
- `id` - Primary key
- `title` - Task name
- `description` - Task details
- `for_everyone` - Boolean (1 = all users, 0 = specific users only)
- `created_at` - Timestamp
- `updated_at` - Timestamp

### task_assignments
Only populated when `tasks.for_everyone = 0`
- `id` - Primary key
- `task_id` - Foreign key to tasks
- `user_id` - Foreign key to users
- `created_at` - Timestamp

### schedules
Each task can have multiple schedules. Fields used depend on `schedule_type`.

## Schedule Types and Fields

### 1. Interval-Based Schedules

**interval_days** - Every X days starting on [date]
- Fields: `interval`, `start_date`
- Example: Every 5 days starting on 01/15/2026

**interval_weeks** - Every X weeks starting on [date]
- Fields: `interval`, `start_date`
- Example: Every 2 weeks starting on 01/15/2026

**interval_months** - Every X months starting on [date]
- Fields: `interval`, `start_date`
- Example: Every 3 months starting on 01/15/2026

### 2. Day-of-Week Based

**weekly** - Weekly on [specific day]
- Fields: `day_of_week`
- Values: 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
- Example: Weekly on Tuesday

### 3. Ordinal Day-of-Month

**ordinal_monthly** - [Ordinal] [day of week] of each month
- Fields: `ordinal`, `day_of_week`
- Ordinal values: 'first', 'second', 'third', 'fourth', 'last'
- Example: First Saturday of each month

**ordinal_bimonthly** - [Ordinal] [day of week] of [even/odd] months
- Fields: `ordinal`, `day_of_week`, `even_odd_months`
- Even_odd values: 'even', 'odd'
- Example: First Saturday of even numbered months

### 4. Fixed Day of Month

**monthly_date** - Monthly on the [X]th day
- Fields: `day_of_month`
- Example: Monthly on the 15th

**first_of_month** - First day of each month
- Fields: None (implicit)

**last_of_month** - Last day of each month
- Fields: None (implicit)

**first_last_interval_months** - First/Last day of every X months
- Fields: `first_or_last`, `interval`, `start_date`
- First_or_last values: 'first', 'last'
- Example: Last day of every 2 months starting on 01/15/2026

### 5. Fixed Count per Period

**times_per_month** - X times per month
- Fields: `times_count`
- Example: Twice a month (times_count = 2)

### 6. Yearly Schedules

**yearly_week** - Yearly in [ordinal week] of [month]
- Fields: `week_of_year`, `month`
- Example: 1st week of March (week_of_year = 9, month = 3)

**yearly_date** - Yearly on [specific date]
- Fields: `month`, `day_of_month`
- Example: March 15 every year (month = 3, day_of_month = 15)

### 7. Seasonal

**seasonal** - Seasonal tasks
- Fields: `season`
- Season values: 'Spring', 'Summer', 'Fall', 'Winter'
- Example: Spring

### 8. One-Time

**one_time** - One-time on [specific date]
- Fields: `specific_date`
- Example: One-time on 03/15/2026

## Examples

### Task for Everyone with Weekly Schedule
```sql
-- Task
INSERT INTO tasks (title, description, for_everyone)
VALUES ('Take out trash', 'Weekly trash pickup', 1);

-- Schedule
INSERT INTO schedules (task_id, schedule_type, day_of_week)
VALUES (1, 'weekly', 'Tuesday');
```

### Task for Specific Users with Multiple Schedules
```sql
-- Task
INSERT INTO tasks (title, description, for_everyone)
VALUES ('Clean bathroom', 'Deep clean bathroom', 0);

-- Assignments
INSERT INTO task_assignments (task_id, user_id) VALUES (2, 1); -- Michael
INSERT INTO task_assignments (task_id, user_id) VALUES (2, 2); -- De

-- Schedule 1: First Saturday of each month
INSERT INTO schedules (task_id, schedule_type, ordinal, day_of_week)
VALUES (2, 'ordinal_monthly', 'first', 'Saturday');

-- Schedule 2: Third Saturday of each month
INSERT INTO schedules (task_id, schedule_type, ordinal, day_of_week)
VALUES (2, 'ordinal_monthly', 'third', 'Saturday');
```
