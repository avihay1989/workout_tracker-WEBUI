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
        self.connection.row_factory = sqlite3.Row  # Return results as dictionaries
        self.cursor = self.connection.cursor()
        self.connection.execute("PRAGMA journal_mode=WAL;")  # Enable Write-Ahead Logging (WAL) mode

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
            print(f"Query executed successfully: {query} | Params: {params}")
        except sqlite3.Error as e:
            print(f"Database error during query execution: {e}")
            raise e

    def fetch_all(self, query, params=None):
        """
        Fetch all rows for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: List of all rows fetched as dictionaries.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            print(f"Fetch all successful: {query} | Params: {params}")
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            raise e

    def fetch_one(self, query, params=None):
        """
        Fetch a single row for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: Single row fetched as a dictionary.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            print(f"Fetch one successful: {query} | Params: {params}")
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            raise e

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
        print("Database connection closed.")

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


def initialize_database():
    """
    Initialize the database with necessary tables and constraints.
    Ensures the schema is properly created if it doesn't exist.
    """
    schema_queries = [
        """
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT UNIQUE NOT NULL,
            primary_muscle_group TEXT,
            secondary_muscle_group TEXT,
            tertiary_muscle_group TEXT,
            force TEXT,
            equipment TEXT,
            mechanic TEXT,
            difficulty TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_selection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            routine TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            min_rep_range INTEGER NOT NULL,
            max_rep_range INTEGER NOT NULL,
            rir INTEGER,
            weight REAL NOT NULL,
            UNIQUE (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        );
        """
    ]

    with DatabaseHandler() as db_handler:
        for query in schema_queries:
            try:
                db_handler.execute_query(query)
                print(f"Schema ensured for query: {query}")
            except sqlite3.Error as e:
                print(f"Error ensuring schema: {e}")
                raise e
