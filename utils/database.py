from utils.config import DB_FILE
import sqlite3


class DatabaseHandler:
    """
    Handles database operations with a context manager.
    """
    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database query error: {e}")
            raise e

    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            raise e

    def fetch_unique_values(self, table, column):
        """
        Fetch unique values for a given column in a table.
        """
        query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
        return [row[0] for row in self.fetch_all(query)]

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
