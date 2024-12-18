from utils.database import DatabaseHandler


class ExerciseFilter:
    def __init__(self):
        self.db = DatabaseHandler()

    def filter_exercises(self, filters):
        """
        Filter exercises based on the provided filters.

        :param filters: Dictionary containing filter criteria.
        :return: List of exercise names matching the criteria.
        """
        base_query = "SELECT exercise_name FROM exercises WHERE 1=1"
        query_conditions = []
        params = []

        # Dynamically build query based on provided filters
        for field, value in filters.items():
            if value:
                query_conditions.append(f"{field} = ?")
                params.append(value)

        if query_conditions:
            base_query += " AND " + " AND ".join(query_conditions)

        try:
            results = self.db.fetch_all(base_query, params)
            return [row[0] for row in results]  # Extract exercise names from results
        except Exception as e:
            print(f"Error filtering exercises: {e}")
            return []
        finally:
            self.db.close()
