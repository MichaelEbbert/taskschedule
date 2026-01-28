from models import add_user, update_user_password, get_db

# Add admin user
try:
    add_user('Admin', 'taskschedule.26Hair')
    print("Admin user created successfully")
except Exception as e:
    print(f"Note: {e}")

# Update passwords for Michael and Mike
conn = get_db()
cursor = conn.cursor()

# Update Michael's password
cursor.execute("SELECT id, first_name FROM users WHERE LOWER(first_name) = 'michael'")
michael = cursor.fetchone()
if michael:
    update_user_password(michael['id'], 'michael')
    print(f"Updated password for {michael['first_name']}")
else:
    print("Michael not found")

# Update Mike's password
cursor.execute("SELECT id, first_name FROM users WHERE LOWER(first_name) = 'mike'")
mike = cursor.fetchone()
if mike:
    update_user_password(mike['id'], 'percy')
    print(f"Updated password for {mike['first_name']}")
else:
    print("Mike not found")

conn.close()
print("\nAll updates complete!")
