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

        # Apply filters dynamically based on the provided dictionary
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

        # Finalize the query by appending conditions
        if query_conditions:
            base_query += " AND " + " AND ".join(query_conditions)

        # Execute the query using the database handler
        with DatabaseHandler() as db:
            try:
                results = db.fetch_all(base_query, params)
                return [row[0] for row in results]  # Extract exercise names
            except Exception as e:
                print(f"Error fetching exercises: {e}")
                return []

    @staticmethod
    def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
        """
        Add a new exercise entry to the user_selection table.
        :param routine: The workout routine (e.g., "A1").
        :param exercise: The name of the exercise (e.g., "Barbell Bench Press").
        :param sets: Number of sets for the exercise.
        :param min_rep_range: Minimum repetitions for each set.
        :param max_rep_range: Maximum repetitions for each set.
        :param rir: Reps in reserve (optional).
        :param weight: The weight used for the exercise.
        """
        query = """
        INSERT INTO user_selection 
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with DatabaseHandler() as db:
            try:
                # Execute the insertion query
                db.execute_query(query, (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
            except Exception as e:
                print(f"Error adding exercise: {e}")

    @staticmethod
    def delete_exercise(exercise_id):
        """
        Delete an exercise from the user_selection table using its unique ID.
        :param exercise_id: The unique ID of the exercise to delete.
        """
        query = "DELETE FROM user_selection WHERE id = ?"
        with DatabaseHandler() as db:
            try:
                # Execute the deletion query
                db.execute_query(query, (exercise_id,))
            except Exception as e:
                print(f"Error deleting exercise: {e}")

    @staticmethod
    def fetch_unique_values(table, column):
        """
        Fetch unique values from a specific column in a table.
        :param table: The table to query (e.g., "exercises").
        :param column: The column to fetch unique values from.
        :return: A list of unique values from the column.
        """
        query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
        with DatabaseHandler() as db:
            try:
                # Fetch results from the database
                results = db.fetch_all(query)
                return [row[0] for row in results]
            except Exception as e:
                print(f"Error fetching unique values: {e}")
                return []

# Publicly expose key functions for easier imports
# These aliases allow external modules to directly use the methods
get_exercises = ExerciseManager.get_exercises
add_exercise = ExerciseManager.add_exercise
delete_exercise = ExerciseManager.delete_exercise
fetch_unique_values = ExerciseManager.fetch_unique_values
