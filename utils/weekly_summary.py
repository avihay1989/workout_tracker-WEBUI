from utils.database import DatabaseHandler


def calculate_weekly_summary(method="Total"):
    """
    Calculate the weekly summary based on the selected method.
    Consolidates results across primary, secondary, and tertiary muscle groups.
    """
    with DatabaseHandler() as db_handler:
        try:
            # Scaling factors for each method
            scaling_factors = {
                "Total": {"primary": 1, "secondary": 1, "tertiary": 0.33},
                "Fractional": {"primary": 1, "secondary": 0.5, "tertiary": 0.17},
                "Direct": {"primary": 1, "secondary": 0, "tertiary": 0},
            }
            factors = scaling_factors.get(method, scaling_factors["Total"])

            # Unified query to avoid over-counting
            query = f"""
                SELECT muscle_group,
                       ROUND(SUM(total_sets), 1) AS total_sets,
                       ROUND(SUM(total_reps), 1) AS total_reps,
                       ROUND(SUM(total_weight), 1) AS total_weight
                FROM (
                    SELECT e.primary_muscle_group AS muscle_group,
                           SUM(us.sets * {factors['primary']}) AS total_sets,
                           SUM(us.sets * us.max_rep_range * {factors['primary']}) AS total_reps,
                           SUM(us.sets * us.weight * {factors['primary']}) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.primary_muscle_group IS NOT NULL
                    GROUP BY e.primary_muscle_group

                    UNION ALL

                    SELECT e.secondary_muscle_group AS muscle_group,
                           SUM(us.sets * {factors['secondary']}) AS total_sets,
                           SUM(us.sets * us.max_rep_range * {factors['secondary']}) AS total_reps,
                           SUM(us.sets * us.weight * {factors['secondary']}) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.secondary_muscle_group IS NOT NULL
                    GROUP BY e.secondary_muscle_group

                    UNION ALL

                    SELECT e.tertiary_muscle_group AS muscle_group,
                           SUM(us.sets * {factors['tertiary']}) AS total_sets,
                           SUM(us.sets * us.max_rep_range * {factors['tertiary']}) AS total_reps,
                           SUM(us.sets * us.weight * {factors['tertiary']}) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.tertiary_muscle_group IS NOT NULL
                    GROUP BY e.tertiary_muscle_group
                ) AS combined
                WHERE muscle_group IS NOT NULL
                GROUP BY muscle_group;
            """

            # Execute query and fetch results
            db_handler.cursor.execute(query)
            results = db_handler.cursor.fetchall()

            # Format results for output
            return [
                {
                    "muscle_group": row[0],
                    "total_sets": round(row[1], 1),
                    "total_reps": round(row[2], 1),
                    "total_weight": round(row[3], 1),
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
    query = "SELECT SUM(sets) FROM user_selection WHERE muscle_group = ?"
    with DatabaseHandler() as db_handler:
        result = db_handler.fetch_all(query, (muscle_group,))
        return result[0][0] if result and result[0][0] else 0
