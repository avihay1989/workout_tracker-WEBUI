import sqlite3
from utils.config import DB_FILE


class MuscleGroupHandler:
    """
    Handles operations related to muscle groups in the exercises database.
    """

    def __init__(self):
        pass  # No persistent connection to avoid thread issues

    def get_exercise_names(self):
        """
        Fetch all unique exercise names from the database.
        :return: List of unique exercise names.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT exercise_name FROM exercises"
            cursor.execute(query)
            rows = cursor.fetchall()
            print("DEBUG: Retrieved Exercises ->", rows)  # Debugging
        return [row[0] for row in rows]  # Extract exercise names from tuples

    def get_muscle_groups(self, exercise_name):
        """
        Fetch the primary, secondary, and tertiary muscle groups for a specific exercise.
        :param exercise_name: Name of the exercise.
        :return: Tuple containing primary, secondary, and tertiary muscle groups.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            query = """
                SELECT primary_muscle_group, secondary_muscle_group, tertiary_muscle_group 
                FROM exercises 
                WHERE exercise_name = ?
            """
            cursor.execute(query, (exercise_name,))
            row = cursor.fetchone()
        if row:
            return row[0], row[1], row[2]
        return None, None, None

    def fetch_muscle_groups_summary(self):
        """
        Fetch a summary of exercises grouped by their primary muscle group.
        :return: List of dictionaries containing muscle groups and exercise counts.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            query = """
                SELECT primary_muscle_group, COUNT(*) AS exercise_count
                FROM exercises
                WHERE primary_muscle_group IS NOT NULL
                GROUP BY primary_muscle_group
                ORDER BY exercise_count DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
        return [{"muscle_group": row[0], "exercise_count": row[1]} for row in results]
