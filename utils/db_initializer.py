import sqlite3
from utils.config import DB_FILE

def initialize_database():
    """
    Initializes the database with required tables if they do not already exist.
    """
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        # Create user_selection table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_selection (
                routine TEXT NOT NULL,
                exercise TEXT NOT NULL,
                sets INTEGER NOT NULL,
                min_rep_range INTEGER NOT NULL,
                max_rep_range INTEGER NOT NULL,
                rir INTEGER NOT NULL,
                weight REAL NOT NULL
            )
        ''')

        # Create weekly_summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_summary (
                muscle_group TEXT PRIMARY KEY,
                total_sets INTEGER NOT NULL,
                total_reps INTEGER NOT NULL,
                total_weight REAL NOT NULL
            )
        ''')

        # Create exercises table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                exercise_name TEXT PRIMARY KEY,
                primary_muscle_group TEXT,
                secondary_muscle_group TEXT,
                tertiary_muscle_group TEXT,
                force TEXT,
                equipment TEXT,
                mechanic TEXT,
                difficulty TEXT
            )
        ''')

        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if connection:
            connection.commit()
            connection.close()
