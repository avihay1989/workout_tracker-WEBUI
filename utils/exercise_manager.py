# exercise_manager.py
import sqlite3
from utils.config import DB_FILE

def get_exercises(filters=None):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    base_query = "SELECT exercise_name FROM exercises WHERE 1=1"
    query_conditions = []
    params = []

    # Apply filters if provided
    if filters:
        for field, value in filters.items():
            if value:
                # Use column names directly in SQL only if they're valid
                if field in ["primary_muscle_group", "secondary_muscle_group", "tertiary_muscle_group", "force", "equipment", "mechanic", "difficulty"]:
                    query_conditions.append(f"{field} = ?")
                    params.append(value)

    # Construct final query
    if query_conditions:
        base_query += " AND " + " AND ".join(query_conditions)

    try:
        cursor.execute(base_query, params)
        exercises = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        exercises = []
    finally:
        connection.close()

    return [exercise[0] for exercise in exercises]


def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_selection (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error adding exercise: {e}")
    finally:
        connection.close()
