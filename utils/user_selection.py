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
    try:
        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        if not results:
            print("DEBUG: No user selection data found.")  # Debugging log

        # Format results into a list of dictionaries for easier handling
        user_selection = [
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
        print("DEBUG: User selection data retrieved successfully.")  # Debugging log
        return user_selection

    except sqlite3.OperationalError as oe:
        print(f"Operational error in database: {oe}")
        return []
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return []
