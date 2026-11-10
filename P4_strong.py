import hashlib
import os
import sqlite3

def register_user(db_path: str, username: str, password: str) -> None:
    """
    Registers a new user securely in an SQLite database.
    
    Mitigates:
    - CWE-256: Plaintext Storage of a Password (by hashing the password).
    - CWE-916: Use of Password Hash With Insufficient Computational Effort (by using scrypt with a unique salt).
    - SQL Injection (by using parameterized queries).
    """
    if not username or not password:
        raise ValueError("Username and password must not be empty.")

    # Generate a cryptographically secure random salt (16 bytes)
    salt = os.urandom(16)
    
    # Derive a secure password hash using scrypt (memory-hard, resistant to GPU cracking)
    # Parameters: n=16384 (CPU/memory cost), r=8 (block size), p=1 (parallelization)
    password_hash = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32
    )

    try:
        # Using a context manager guarantees the connection is properly closed,
        # and automatically commits transactions (or rolls back on error).
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Ensure the users table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL
                )
            """)
            
            # Insert the user using parameterized statements (?) to prevent SQL Injection
            cursor.execute(
                "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                (username, salt, password_hash)
            )
            conn.commit()
            
    except sqlite3.IntegrityError as e:
        raise ValueError(f"User '{username}' already exists.") from e
    except sqlite3.Error as e:
        raise RuntimeError(f"A database error occurred: {e}") from e

if __name__ == "__main__":
    # Example usage:
    db_file = "secure_app.db"
    try:
        register_user(db_file, "alice_smith", "SuperSecretPassword123!")
        print("User registered successfully!")
    except (ValueError, RuntimeError) as err:
        print(f"Registration failed: {err}")