import sqlite3
from utils.config import DB_FILE

def initialize_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Exercises table (Ensure schema matches your requirements)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_name TEXT PRIMARY KEY,
            primary_muscle_group TEXT NOT NULL,
            secondary_muscle_group TEXT,
            tertiary_muscle_group TEXT,
            force TEXT,
            equipment TEXT,
            mechanic TEXT,
            grips TEXT,
            difficulty TEXT
        )
    ''')

    # Weekly summary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            muscle_group TEXT NOT NULL,
            total_sets INTEGER NOT NULL,
            total_reps INTEGER NOT NULL,
            total_weight REAL NOT NULL
        )
    ''')

    # User selection table
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

    connection.commit()
    connection.close()

def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO user_selection (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
    connection.commit()
    connection.close()

def get_exercises(filters=None):
    """
    Fetch exercises based on optional filters.

    :param filters: Dictionary of filter parameters.
    :return: List of filtered exercises.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    base_query = 'SELECT exercise_name FROM exercises'
    conditions = []
    parameters = []

    if filters:
        for column, value in filters.items():
            if value:  # Only include filters with values
                conditions.append(f"{column} = ?")
                parameters.append(value)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY exercise_name ASC"

    cursor.execute(base_query, parameters)
    exercises = cursor.fetchall()
    connection.close()
    return [row[0] for row in exercises]


def get_user_selection():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user_selection')
    user_selection = cursor.fetchall()
    connection.close()
    return user_selection

def calculate_weekly_summary(method="Total"):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    if method == "Total":
        query = '''
            SELECT e.primary_muscle_group AS muscle_group,
                   SUM(us.sets) AS total_sets,
                   SUM(us.max_rep_range * us.sets) AS total_reps,
                   SUM(us.weight * us.sets) AS total_weight
            FROM user_selection us
            JOIN exercises e ON us.exercise = e.exercise_name
            GROUP BY e.primary_muscle_group
        '''
    elif method == "Fractional":
        query = '''
            SELECT e.primary_muscle_group AS muscle_group,
                   SUM(us.sets) + SUM(us.sets * 0.5) AS total_sets,
                   SUM(us.max_rep_range * us.sets) AS total_reps,
                   SUM(us.weight * us.sets) AS total_weight
            FROM user_selection us
            JOIN exercises e ON us.exercise = e.exercise_name
            GROUP BY e.primary_muscle_group
        '''
    elif method == "Direct":
        query = '''
            SELECT e.primary_muscle_group AS muscle_group,
                   SUM(us.sets) AS total_sets,
                   SUM(us.max_rep_range * us.sets) AS total_reps,
                   SUM(us.weight * us.sets) AS total_weight
            FROM user_selection us
            JOIN exercises e ON us.exercise = e.exercise_name
            WHERE e.primary_muscle_group IS NOT NULL
            GROUP BY e.primary_muscle_group
        '''
    else:
        raise ValueError("Invalid calculation method")

    cursor.execute(query)
    summary = cursor.fetchall()

    # Clear the `weekly_summary` table before inserting new data
    cursor.execute('DELETE FROM weekly_summary')

    cursor.executemany('''
        INSERT INTO weekly_summary (week, muscle_group, total_sets, total_reps, total_weight)
        VALUES (strftime('%W', 'now'), ?, ?, ?, ?)
    ''', summary)

    connection.commit()
    connection.close()

def get_weekly_summary():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('SELECT muscle_group, total_sets, total_reps, total_weight FROM weekly_summary')
    summary = cursor.fetchall()
    connection.close()
    return summary

def calculate_total_sets(muscle_group):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets) FROM exercises WHERE primary_muscle_group = ?
    ''', (muscle_group,))
    total_sets = cursor.fetchone()[0] or 0
    connection.close()
    return total_sets

def calculate_fractional_sets(muscle_group):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets * weight / (SELECT SUM(weight) FROM exercises WHERE primary_muscle_group = ?))
        FROM exercises
        WHERE primary_muscle_group = ?
    ''', (muscle_group, muscle_group))
    fractional_sets = cursor.fetchone()[0] or 0
    connection.close()
    return fractional_sets

def calculate_direct_sets(muscle_group):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets) FROM exercises WHERE primary_muscle_group = ?
    ''', (muscle_group,))
    direct_sets = cursor.fetchone()[0] or 0
    connection.close()
    return direct_sets
