import sqlite3
from utils.config import DB_FILE


def get_user_selection():
    """
    Fetches user selection data along with muscle group information
    from the exercises table.
    :return: List of dictionaries containing user selection and muscle groups.
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
    try:
        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        # Format results into a list of dictionaries for easier handling
        user_selection = [
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
        print("DEBUG: User selection data:", user_selection)  # Debugging log
        return user_selection
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
