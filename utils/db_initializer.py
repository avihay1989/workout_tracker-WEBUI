# db_initializer.py
import sqlite3
from utils.config import DB_FILE

def initialize_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_selection (
            routine TEXT,
            exercise TEXT,
            sets INTEGER,
            min_rep_range INTEGER,
            max_rep_range INTEGER,
            rir INTEGER,
            weight REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_summary (
            muscle_group TEXT PRIMARY KEY,
            total_sets INTEGER,
            total_reps INTEGER,
            total_weight REAL
        )
    ''')
    connection.commit()
    connection.close()
