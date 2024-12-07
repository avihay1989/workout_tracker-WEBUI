from utils.database import DatabaseHandler

from utils.database import DatabaseHandler

def calculate_weekly_summary(method="Total"):
    """
    Calculate the weekly summary based on the selected method.
    Consolidates results across primary, secondary, and tertiary muscle groups.
    """
    with DatabaseHandler() as db_handler:
        try:
            # Determine the appropriate query based on the method
            if method == "Total":
                query = """
                    SELECT muscle_group, ROUND(SUM(total_sets), 1) AS total_sets,
                           ROUND(SUM(total_reps), 1) AS total_reps,
                           ROUND(SUM(total_weight), 1) AS total_weight
                    FROM (
                        SELECT e.primary_muscle_group AS muscle_group, SUM(us.sets) AS total_sets,
                               SUM(us.sets * us.max_rep_range) AS total_reps,
                               SUM(us.sets * us.weight) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        GROUP BY e.primary_muscle_group

                        UNION ALL

                        SELECT e.secondary_muscle_group AS muscle_group, SUM(us.sets * 0.5) AS total_sets,
                               SUM(us.sets * us.max_rep_range * 0.5) AS total_reps,
                               SUM(us.sets * us.weight * 0.5) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        WHERE e.secondary_muscle_group IS NOT NULL
                        GROUP BY e.secondary_muscle_group

                        UNION ALL

                        SELECT e.tertiary_muscle_group AS muscle_group, SUM(us.sets * 0.33) AS total_sets,
                               SUM(us.sets * us.max_rep_range * 0.33) AS total_reps,
                               SUM(us.sets * us.weight * 0.33) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        WHERE e.tertiary_muscle_group IS NOT NULL
                        GROUP BY e.tertiary_muscle_group
                    ) AS combined
                    WHERE muscle_group IS NOT NULL
                    GROUP BY muscle_group;
                """
            elif method == "Fractional":
                query = """
                    SELECT muscle_group, ROUND(SUM(total_sets), 1) AS total_sets,
                           ROUND(SUM(total_reps), 1) AS total_reps,
                           ROUND(SUM(total_weight), 1) AS total_weight
                    FROM (
                        SELECT e.primary_muscle_group AS muscle_group, SUM(us.sets * 0.5) AS total_sets,
                               SUM(us.sets * us.max_rep_range * 0.5) AS total_reps,
                               SUM(us.sets * us.weight * 0.5) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        GROUP BY e.primary_muscle_group

                        UNION ALL

                        SELECT e.secondary_muscle_group AS muscle_group, SUM(us.sets * 0.25) AS total_sets,
                               SUM(us.sets * us.max_rep_range * 0.25) AS total_reps,
                               SUM(us.sets * us.weight * 0.25) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        WHERE e.secondary_muscle_group IS NOT NULL
                        GROUP BY e.secondary_muscle_group

                        UNION ALL

                        SELECT e.tertiary_muscle_group AS muscle_group, SUM(us.sets * 0.17) AS total_sets,
                               SUM(us.sets * us.max_rep_range * 0.17) AS total_reps,
                               SUM(us.sets * us.weight * 0.17) AS total_weight
                        FROM user_selection us
                        JOIN exercises e ON us.exercise = e.exercise_name
                        WHERE e.tertiary_muscle_group IS NOT NULL
                        GROUP BY e.tertiary_muscle_group
                    ) AS combined
                    WHERE muscle_group IS NOT NULL
                    GROUP BY muscle_group;
                """
            elif method == "Direct":
                query = """
                    SELECT e.primary_muscle_group AS muscle_group, SUM(us.sets) AS total_sets,
                           SUM(us.sets * us.max_rep_range) AS total_reps,
                           SUM(us.sets * us.weight) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    GROUP BY e.primary_muscle_group;
                """
            else:
                return []  # Return an empty list for invalid methods

            # Execute the query
            db_handler.cursor.execute(query)
            results = db_handler.cursor.fetchall()

            print(f"Debug: Weekly summary results for method '{method}': {results}")

            # Format the results
            return [
                {
                    "muscle_group": row[0],
                    "total_sets": round(float(row[1]), 1) if row[1] else 0,
                    "total_reps": round(float(row[2]), 1) if row[2] else 0,
                    "total_weight": round(float(row[3]), 1) if row[3] else 0,
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error calculating weekly summary for method '{method}': {e}")
            return []



def get_weekly_summary():
    """
    Fetch weekly summary from the database.
    """
    query = """
        SELECT muscle_group, total_sets, total_reps, total_weight
        FROM weekly_summary
    """
    with DatabaseHandler() as db_handler:
        return db_handler.fetch_all(query)


def calculate_total_sets(muscle_group):
    """
    Calculate total sets for a specific muscle group.
    """
    with DatabaseHandler() as db_handler:
        query = "SELECT SUM(sets) FROM user_selection WHERE muscle_group = ?"
        result = db_handler.fetch_one(query, (muscle_group,))
        return result[0] if result and result[0] else 0
