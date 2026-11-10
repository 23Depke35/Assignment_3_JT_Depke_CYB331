db_file = "app_database.db"
user = get_user_by_username(db_file, "johndoe")

if user:
    # Access values by column name or positional index
    print(f"User ID: {user['id']}")
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    
    # Or convert to a standard dictionary
    user_dict = dict(user)
    print(user_dict)
else:
    print("User not found.")