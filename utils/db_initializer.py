import sqlite3
from utils.config import DB_FILE

def initialize_database():
    """
    Initializes the database with required tables if they do not already exist.
    """
    table_schemas = {
        "user_selection": '''
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
            )
        ''',
        "weekly_summary": '''
            CREATE TABLE IF NOT EXISTS weekly_summary (
                muscle_group TEXT PRIMARY KEY,
                total_sets INTEGER NOT NULL,
                total_reps INTEGER NOT NULL,
                total_weight REAL NOT NULL
            )
        ''',
        "exercises": '''
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
        '''
    }

    try:
        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()

            # Iterate through schemas and execute table creation
            for table_name, schema in table_schemas.items():
                cursor.execute(schema)
                print(f"DEBUG: Table '{table_name}' ensured.")

            print("DEBUG: Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"ERROR: Database initialization failed - {e}")
