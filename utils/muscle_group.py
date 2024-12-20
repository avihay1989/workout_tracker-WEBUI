from utils.database import DatabaseHandler


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
        query = "SELECT DISTINCT exercise_name FROM exercises"
        try:
            with DatabaseHandler() as db:
                results = db.fetch_all(query)
                print(f"DEBUG: Retrieved Exercises -> {results}")  # Debugging
                return [row[0] for row in results if isinstance(row, tuple)]
        except Exception as e:
            print(f"Error fetching exercise names: {e}")
            return []

    def get_muscle_groups(self, exercise_name):
        """
        Fetch the primary, secondary, and tertiary muscle groups for a specific exercise.
        :param exercise_name: Name of the exercise.
        :return: Tuple containing primary, secondary, and tertiary muscle groups.
        """
        query = """
            SELECT primary_muscle_group, secondary_muscle_group, tertiary_muscle_group 
            FROM exercises 
            WHERE exercise_name = ?
        """
        try:
            with DatabaseHandler() as db:
                result = db.fetch_one(query, (exercise_name,))
                print(f"DEBUG: Muscle groups for {exercise_name} -> {result}")  # Debugging
                if result:
                    return result[0], result[1], result[2]
                return None, None, None
        except Exception as e:
            print(f"Error fetching muscle groups for exercise '{exercise_name}': {e}")
            return None, None, None

    def fetch_muscle_groups_summary(self):
        """
        Fetch a summary of exercises grouped by their primary muscle group.
        :return: List of dictionaries containing muscle groups and exercise counts.
        """
        query = """
            SELECT primary_muscle_group, COUNT(*) AS exercise_count
            FROM exercises
            WHERE primary_muscle_group IS NOT NULL
            GROUP BY primary_muscle_group
            ORDER BY exercise_count DESC
        """
        try:
            with DatabaseHandler() as db:
                results = db.fetch_all(query)
                print(f"DEBUG: Muscle group summary -> {results}")  # Debugging
                return [{"muscle_group": row[0], "exercise_count": row[1]} for row in results if isinstance(row, tuple)]
        except Exception as e:
            print(f"Error fetching muscle group summary: {e}")
            return []

