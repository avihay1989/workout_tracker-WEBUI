import sqlite3
from utils.config import DB_FILE


class DataHandler:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """
        Execute a query with optional parameters.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            print("execute")
            print(query)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query, params=None):
        """
        Fetch all rows for a query with optional parameters.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            print("fetch all")
            print(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_unique_values(self, table, column):
        """
        Fetch distinct values from a specific column in a table, ordered alphabetically.
        """
        try:
            query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
            self.cursor.execute(query)
            print("fetch unique values")
            print(query)
            results = self.cursor.fetchall()
            return [row[0] for row in results]
        except Exception as e:
            print(f"Error fetching unique values: {e}")
            return []

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()
