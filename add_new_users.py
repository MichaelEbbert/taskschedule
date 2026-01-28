from models import add_user

# Add new users with password 'claude101'
new_users = [
    'anthony', 'brennen', 'brett', 'daniel', 'john',
    'kyle', 'rita', 'sam', 'tracy', 'mike',
    'kasey', 'wesley', 'deidra'
]

for name in new_users:
    # Capitalize first letter for storage
    capitalized_name = name.capitalize()
    add_user(capitalized_name, 'claude101')

print(f"\nAdded {len(new_users)} users successfully!")
