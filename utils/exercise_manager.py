from utils.database import DatabaseHandler
import sqlite3

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
        base_query = "SELECT DISTINCT exercise_name FROM exercises WHERE exercise_name IS NOT NULL"
        valid_fields = [
            "primary_muscle_group", "secondary_muscle_group",
            "tertiary_muscle_group", "force",
            "equipment", "mechanic", "difficulty"
        ]
        query, params = ExerciseManager.build_query(base_query, filters, valid_fields)

        with DatabaseHandler() as db:
            try:
                results = db.fetch_all(query, params)
                print(f"DEBUG: Query executed - {query} with params {params}")
                # Ensure only valid and non-empty exercise names are returned
                return [row["exercise_name"] for row in results if row["exercise_name"] and row["exercise_name"].strip()]
            except sqlite3.OperationalError as oe:
                print(f"Operational error fetching exercises: {oe}")
                return []
            except Exception as e:
                print(f"Unexpected error in get_exercises: {e}")
                return []

    @staticmethod
    def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
        """
        Add a new exercise entry to the user_selection table.
        Ensures duplicate entries are not allowed.
        """
        if not all([routine, exercise, sets, min_rep_range, max_rep_range, weight]):
            print("Error: Missing required fields for adding an exercise.")
            return "Error: Missing required fields."

        duplicate_check_query = """
        SELECT COUNT(*) FROM user_selection
        WHERE routine = ? AND exercise = ? AND sets = ? AND min_rep_range = ? 
        AND max_rep_range = ? AND rir = ? AND weight = ?
        """
        insert_query = """
        INSERT INTO user_selection 
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with DatabaseHandler() as db:
            try:
                existing_count = db.fetch_one(duplicate_check_query, 
                                              (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))["COUNT(*)"]
                if existing_count > 0:
                    print(f"Duplicate exercise found: {routine}, {exercise}")
                    return "Duplicate entry: Exercise already exists."
                db.execute_query(insert_query, (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
                print(f"DEBUG: Exercise added - {exercise} in routine {routine}")
                return "Exercise added successfully."
            except sqlite3.OperationalError as oe:
                print(f"Operational error adding exercise: {oe}")
                return f"Operational error: {oe}"
            except Exception as e:
                print(f"Error adding exercise: {e}")
                return f"Error: {e}"

    @staticmethod
    def delete_exercise(exercise_id):
        """
        Delete an exercise from the user_selection table using its unique ID.
        """
        query = "DELETE FROM user_selection WHERE id = ?"
        with DatabaseHandler() as db:
            try:
                db.execute_query(query, (exercise_id,))
                print(f"DEBUG: Exercise with ID {exercise_id} deleted.")
            except sqlite3.Error as e:
                print(f"Error deleting exercise: {e}")

    @staticmethod
    def fetch_unique_values(table, column):
        """
        Fetch unique values from a specific column in a table.
        """
        query = f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column} ASC"
        with DatabaseHandler() as db:
            try:
                results = db.fetch_all(query)
                print(f"DEBUG: Unique values fetched for {column} in {table}")
                return [row[column] for row in results]
            except Exception as e:
                print(f"Error fetching unique values: {e}")
                return []

    @staticmethod
    def build_query(base_query, filters, valid_fields):
        """
        Dynamically build a SQL query with conditions based on filters.
        """
        query_conditions = []
        params = []
        for field, value in (filters or {}).items():
            if field in valid_fields and value:
                query_conditions.append(f"{field} = ?")
                params.append(value)
        if query_conditions:
            base_query += " AND " + " AND ".join(query_conditions)
        print(f"DEBUG: Built query - {base_query} with params {params}")
        return base_query, params

# Publicly expose key functions
get_exercises = ExerciseManager.get_exercises
add_exercise = ExerciseManager.add_exercise
delete_exercise = ExerciseManager.delete_exercise
fetch_unique_values = ExerciseManager.fetch_unique_values
