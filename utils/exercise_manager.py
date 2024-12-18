from utils.database import DatabaseHandler


class ExerciseManager:
    """
    Handles operations for fetching and managing exercises.
    """

    @staticmethod
    def get_exercises(filters=None):
        """
        Fetch exercises with optional filters.
        :param filters: Dictionary containing filter criteria.
        :return: List of exercise names matching the filters.
        """
        base_query = "SELECT DISTINCT exercise_name FROM exercises WHERE 1=1"
        query_conditions = []
        params = []

        # Apply filters dynamically
        if filters:
            for field, value in filters.items():
                if value and field in [
                    "primary_muscle_group",
                    "secondary_muscle_group",
                    "tertiary_muscle_group",
                    "force",
                    "equipment",
                    "mechanic",
                    "difficulty",
                ]:
                    query_conditions.append(f"{field} = ?")
                    params.append(value)

        # Finalize query
        if query_conditions:
            base_query += " AND " + " AND ".join(query_conditions)

        with DatabaseHandler() as db:
            try:
                results = db.fetch_all(base_query, params)
                return [row[0] for row in results]
            except Exception as e:
                print(f"Error fetching exercises: {e}")
                return []

    @staticmethod
    def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
        """
        Add a new exercise entry to the user_selection table.
        """
        query = """
        INSERT INTO user_selection 
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with DatabaseHandler() as db:
            try:
                db.execute_query(query, (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
            except Exception as e:
                print(f"Error adding exercise: {e}")

    @staticmethod
    def delete_exercise(routine, exercise):
        """
        Delete an exercise from the user_selection table.
        """
        query = "DELETE FROM user_selection WHERE routine = ? AND exercise = ?"
        with DatabaseHandler() as db:
            try:
                db.execute_query(query, (routine, exercise))
            except Exception as e:
                print(f"Error deleting exercise: {e}")

    @staticmethod
    def fetch_unique_values(table, column):
        """
        Fetch unique values from a specific column in a table.
        """
        query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
        with DatabaseHandler() as db:
            try:
                results = db.fetch_all(query)
                return [row[0] for row in results]
            except Exception as e:
                print(f"Error fetching unique values: {e}")
                return []


# Publicly expose key functions for easier imports
get_exercises = ExerciseManager.get_exercises
add_exercise = ExerciseManager.add_exercise
delete_exercise = ExerciseManager.delete_exercise
fetch_unique_values = ExerciseManager.fetch_unique_values
