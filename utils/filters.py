from utils.database import DatabaseHandler


class ExerciseFilter:
    def __init__(self):
        self.db = DatabaseHandler()

    def filter_exercises(self, filters):
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
            return [row[0] for row in results]
        finally:
            self.db.close()
