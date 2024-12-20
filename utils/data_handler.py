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
            us.id,
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
                    "id": row[0],
                    "routine": row[1],
                    "exercise": row[2],
                    "sets": row[3],
                    "min_rep_range": row[4],
                    "max_rep_range": row[5],
                    "rir": row[6],
                    "weight": row[7],
                    "primary_muscle_group": row[8],
                    "secondary_muscle_group": row[9],
                    "tertiary_muscle_group": row[10],
                }
                for row in results
            ]

    @staticmethod
    def add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight):
        """
        Add a new exercise entry to the user_selection table and return the new exercise ID.
        """
        query = """
        INSERT INTO user_selection 
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with DatabaseHandler() as db:
            try:
                db.cursor.execute(query, (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight))
                db.connection.commit()
                new_id = db.cursor.lastrowid  # Fetch the ID of the last inserted row
                return new_id  # Return the ID for reference
            except Exception as e:
                print(f"Error adding exercise: {e}")
                return None

    @staticmethod
    def remove_exercise(exercise_id):
        """
        Remove an exercise from the user_selection table.
        """
        query = "DELETE FROM user_selection WHERE id = ?"
        with DatabaseHandler() as db:
            db.execute_query(query, (exercise_id,))

    @staticmethod
    def fetch_unique_values(table, column):
        """
        Fetch unique values for a given column in a table.
        """
        query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column} ASC"
        with DatabaseHandler() as db:
            return [row[0] for row in db.fetch_all(query)]
