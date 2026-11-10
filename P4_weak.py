import sqlite3
import hashlib
import os

def initialize_database():
    """Creates the SQLite database and users table if they don't exist."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a secure salt."""
    if salt is None:
        salt = os.urandom(16)  # Generate a random 16-byte salt
    
    # Hash the password with 100,000 iterations of PBKDF2
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000
    )
    
    # Return hex representations for easy database storage
    return pwd_hash.hex(), salt.hex()

def register_user(username: str, password: str) -> bool:
    """Registers a new user and saves them to the database."""
    initialize_database()
    
    pwd_hash, salt = hash_password(password)
    
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, pwd_hash, salt)
        )
        conn.commit()
        print(f"Success: User '{username}' registered successfully!")
        return True
        
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists.")
        return False
        
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    """Verifies user login credentials."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("Error: User not found.")
        return False
        
    stored_hash, stored_salt_hex = result
    stored_salt = bytes.fromhex(stored_salt_hex)
    
    # Hash the input password using the stored user's salt
    new_hash, _ = hash_password(password, stored_salt)
    
    # Compare hashes securely
    if new_hash == stored_hash:
        print(f"Success: Welcome back, {username}!")
        return True
    else:
        print("Error: Incorrect password.")
        return False

# --- Example Usage ---
if __name__ == "__main__":
    # Test Registration
    register_user("alice_dev", "SuperSecretPassword123!")
    
    # Test Login Verification
    print("\n--- Testing Login ---")
    verify_user("alice_dev", "SuperSecretPassword123!") # Should succeed
    verify_user("alice_dev", "WrongPassword")           # Should fail