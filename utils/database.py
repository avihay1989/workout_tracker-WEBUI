from utils.config import DB_FILE
import sqlite3

class DatabaseHandler:
    """
    Handles low-level database operations with context management.
    """

    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.connection = sqlite3.connect(DB_FILE)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        """
        Executes a query with optional parameters.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e

    def fetch_all(self, query, params=None):
        """
        Fetch all rows for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: List of all rows fetched.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            raise e

    def fetch_one(self, query, params=None):
        """
        Fetch a single row for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: Single row fetched.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            raise e

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()

    def __enter__(self):
        """
        Context management entry.
        :return: The instance itself for use in `with` statements.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context management exit.
        Automatically closes the database connection.
        """
        self.close()
