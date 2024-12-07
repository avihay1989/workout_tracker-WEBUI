import sqlite3
from utils.config import DB_FILE


class MuscleGroupHandler:
    def __init__(self):
        pass  # No persistent connection to avoid thread issues

    def get_exercise_names(self):
        """
        Fetch all unique exercise names from the database.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT exercise_name FROM exercises")
            rows = cursor.fetchall()
            print("DEBUG: Retrieved Exercises ->", rows)  # Debugging
        return [row[0] for row in rows]  # Extract exercise names from tuples

    def get_muscle_groups(self, exercise_name):
        """
        Fetch the main and secondary muscle groups for a specific exercise.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            query = "SELECT main_muscle_group, sub_muscle_group FROM exercises WHERE exercise_name = ?"
            cursor.execute(query, (exercise_name,))
            row = cursor.fetchone()
        if row:
            main_muscle, secondary_muscle = row
            return main_muscle, secondary_muscle
        return None, None
