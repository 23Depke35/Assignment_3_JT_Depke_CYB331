import sqlite3
from typing import Optional

def get_user_by_username(db_path: str, username: str) -> Optional[sqlite3.Row]:
    """
    Retrieves a user row from the SQLite database by username.

    :param db_path: Path to the SQLite database file.
    :param username: Username to look up.
    :return: A sqlite3.Row object if found, or None if no user exists.
    """
    query = "SELECT * FROM users WHERE username = ?"
    
    with sqlite3.connect(db_path) as conn:
        # Enables accessing columns by column name (e.g., row["email"])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, (username,))
        return cursor.fetchone()