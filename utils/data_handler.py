from utils.database import DatabaseHandler


class DataHandler:
    """
    Application-facing data operations using the DatabaseHandler.
    """

    @staticmethod
    def fetch_user_selection():
        """
        Fetch user selection data joined with muscle group info.
        """
        query = """
        SELECT
            us.routine,
            us.exercise,
            us.sets,
            us.min_rep_range,
            us.max_rep_range,
            us.rir,
            us.weight,
            e.primary_muscle_group,
            e.secondary_muscle_group,
            e.tertiary_muscle_group
        FROM user_selection us
        JOIN exercises e ON us.exercise = e.exercise_name;
        """
        with DatabaseHandler() as db:
            results = db.fetch_all(query)
            return [
                {
                    "routine": row[0],
                    "exercise": row[1],
                    "sets": row[2],
                    "min_rep_range": row[3],
                    "max_rep_range": row[4],
                    "rir": row[5],
                    "weight": row[6],
                    "primary_muscle_group": row[7],
                    "secondary_muscle_group": row[8],
                    "tertiary_muscle_group": row[9],
                }
                for row in results
            ]

    @staticmethod
    def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
        """
        Add a new exercise entry into the user_selection table.
        """
        query = """
        INSERT INTO user_selection
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with DatabaseHandler() as db:
            db.execute_query(query, (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))

    @staticmethod
    def remove_exercise(routine, exercise):
        """
        Remove an exercise from the user_selection table.
        """
        query = "DELETE FROM user_selection WHERE routine = ? AND exercise = ?"
        with DatabaseHandler() as db:
            db.execute_query(query, (routine, exercise))

    @staticmethod
    def fetch_unique_values(table, column):
        """
        Fetch unique values for a given column in a table.
        """
        query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
        with DatabaseHandler() as db:
            return [row[0] for row in db.fetch_all(query)]
