import sqlite3

def get_user_by_username(db_path: str, username: str) -> dict | None:
    """
    Retrieves a user's id, username, and email by their username.
    Prevents SQL injection using parameterized queries.
    """
    if not db_path or not isinstance(db_path, str):
        raise ValueError("A valid database path string must be provided.")
    if not username or not isinstance(username, str):
        raise ValueError("A valid username string must be provided.")

    try:
        # Using a context manager ensures the connection and cursor are safely closed
        with sqlite3.connect(db_path) as conn:
            # Configure row factory to access columns by name and convert to dict easily
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Static query string with '?' placeholder to prevent CWE-89 SQL Injection
            query = "SELECT id, username, email FROM users WHERE username = ?"
            
            cursor.execute(query, (username,))
            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    except sqlite3.Error as e:
        # Wrap database-specific errors and raise
        raise RuntimeError(f"An error occurred while accessing the database: {e}") from e