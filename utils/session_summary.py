from utils.database import DatabaseHandler


def calculate_session_summary(method="Total"):
    """
    Calculate the per-session summary for sets and reps by muscle group.
    :param method: Calculation method - "Total", "Fractional", or "Direct".
    :return: List of session summary data.
    """
    # Scaling factors for each calculation method
    scaling_factors = {
        "Total": {"primary": 1, "secondary": 1, "tertiary": 0.33},
        "Fractional": {"primary": 1, "secondary": 0.5, "tertiary": 0.17},
        "Direct": {"primary": 1, "secondary": 0, "tertiary": 0},
    }
    factors = scaling_factors.get(method, scaling_factors["Total"])

    # Query to calculate session summary
    query = f"""
        SELECT
            us.routine,
            e.primary_muscle_group AS muscle_group,
            ROUND(SUM(us.sets * {factors['primary']}), 1) AS total_sets_primary,
            ROUND(SUM(us.sets * us.max_rep_range * {factors['primary']}), 1) AS total_reps_primary,
            ROUND(SUM(us.sets * {factors['secondary']}), 1) AS total_sets_secondary,
            ROUND(SUM(us.sets * us.max_rep_range * {factors['secondary']}), 1) AS total_reps_secondary,
            ROUND(SUM(us.sets * {factors['tertiary']}), 1) AS total_sets_tertiary,
            ROUND(SUM(us.sets * us.max_rep_range * {factors['tertiary']}), 1) AS total_reps_tertiary
        FROM user_selection us
        JOIN exercises e ON us.exercise = e.exercise_name
        GROUP BY us.routine, e.primary_muscle_group;
    """

    # Fetch and calculate the consolidated session summary
    with DatabaseHandler() as db_handler:
        try:
            db_handler.cursor.execute(query)
            results = db_handler.cursor.fetchall()

            # Format results into a list of dictionaries
            summary = []
            for row in results:
                routine, muscle_group = row[0], row[1]
                total_sets = row[2] + row[4] + row[6]
                total_reps = row[3] + row[5] + row[7]
                summary.append({
                    "routine": routine,
                    "muscle_group": muscle_group,
                    "total_sets": total_sets,
                    "total_reps": total_reps,
                })
            return summary

        except Exception as e:
            print(f"Error calculating session summary: {e}")
            return []
