from io import BytesIO 
from flask import Flask, render_template, request, jsonify, redirect, Response
from io import BytesIO
import pandas as pd
from utils import (
    initialize_database,
    get_exercises,
    add_exercise,
    get_user_selection,
    calculate_weekly_summary,
)
from utils.database import DatabaseHandler

app = Flask(__name__)

# Initialize the database
initialize_database()


@app.route("/")
def index():
    return redirect("/workout_plan")


@app.route("/workout_plan")
def workout_plan():
    try:
        # Fetch exercises and user selection
        exercises = get_exercises()
        user_selection = get_user_selection()

        # Debug: Print the user selection
        # print("User selection data:", user_selection)

        # Fetch unique values for filters
        with DatabaseHandler() as db_handler:
            filters = {
                "Primary Muscle Group": db_handler.fetch_unique_values("exercises", "primary_muscle_group"),
                "Secondary Muscle Group": db_handler.fetch_unique_values("exercises", "secondary_muscle_group"),
                "Tertiary Muscle Group": db_handler.fetch_unique_values("exercises", "tertiary_muscle_group"),
                "Force": db_handler.fetch_unique_values("exercises", "force"),
                "Equipment": db_handler.fetch_unique_values("exercises", "equipment"),
                "Mechanic": db_handler.fetch_unique_values("exercises", "mechanic"),
                "Difficulty": db_handler.fetch_unique_values("exercises", "difficulty"),
            }

        # Routine options grouped by split type
        routine_options = {
            "4 Week Split": ["A1", "B1", "A2", "B2"],
            "Full Body": ["Fullbody1", "Fullbody2", "Fullbody3"],
            "Push, Pull, Legs": ["Push1", "Pull1", "Legs1", "Push2", "Pull2", "Legs2"],
            "2 Days Split": ["A", "B"],
            "Upper Lower": ["Upper1", "Lower1", "Upper2", "Lower2"],
            "3 Days Split": ["A", "B", "C"],
        }

        return render_template(
            "workout_plan.html",
            exercises=exercises,
            user_selection=user_selection,
            filters=filters,
            routineOptions=routine_options,
            enumerate=enumerate,
        )
    except Exception as e:
        print(f"Error in workout_plan: {e}")
        return render_template("error.html", message="Unable to load workout plan"), 500


@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    try:
        data = request.get_json()
        routine = data.get("routine")
        exercise = data.get("exercise")
        sets = data.get("sets")
        min_rep_range = data.get("min_rep_range")
        max_rep_range = data.get("max_rep_range")
        rir = data.get("rir")
        weight = data.get("weight")

        if not (routine and exercise and sets and min_rep_range and max_rep_range and weight):
            print("Invalid data received for add_exercise:", data)  # Debugging log
            return jsonify({"message": "Missing required fields"}), 400

        add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        return jsonify({"message": "Exercise added successfully"}), 200
    except Exception as e:
        print(f"Error in add_exercise: {e}")
        return jsonify({"error": "Unable to add exercise"}), 500


@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    try:
        data = request.get_json()
        routine = data.get("routine")
        exercise = data.get("exercise")

        if not (routine and exercise):
            print("Invalid data received for remove_exercise:", data)  # Debugging log
            return jsonify({"message": "Invalid request"}), 400

        with DatabaseHandler() as db_handler:
            db_handler.execute_query(
                "DELETE FROM user_selection WHERE routine = ? AND exercise = ?",
                (routine, exercise),
            )
        return jsonify({"message": "Exercise removed successfully"}), 200
    except Exception as e:
        print(f"Error in remove_exercise: {e}")
        return jsonify({"error": "Unable to remove exercise"}), 500


@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    try:
        filters = request.get_json()
        if not filters:
            return jsonify({"message": "No filters provided"}), 400
        exercises = get_exercises(filters=filters)
        return jsonify(exercises)
    except Exception as e:
        print(f"Error in filter_exercises: {e}")
        return jsonify({"error": "Unable to filter exercises"}), 500


@app.route("/weekly_summary", methods=["GET"])
def weekly_summary():
    method = request.args.get("method", "Total")
    try:
        # Fetch data from the database
        results = calculate_weekly_summary(method)

        # Format results for JSON response
        summary = [
            {
                "muscle_group": row["muscle_group"],
                "total_sets": row["total_sets"],
                "total_reps": row["total_reps"],
                "total_weight": row["total_weight"],
            }
            for row in results
        ]

        # Check if the request expects JSON
        if request.headers.get("Accept") == "application/json":
            return jsonify(summary)

        # Render the HTML page if it's a browser request
        return render_template(
            "weekly_summary.html",
            summary=summary,
            selected_method=method,
        )

    except Exception as e:
        error_details = str(e)
        print(f"Error in weekly_summary: {error_details}")

        # If JSON is expected, return an appropriate JSON error response
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Unable to fetch weekly summary", "details": error_details}), 500

        # For HTML responses, show an error page
        return render_template("error.html", message="Unable to fetch weekly summary"), 500


@app.route('/export_to_excel', methods=['GET'])
def export_to_excel():
    try:
        # Fetch user selection data
        user_selection = get_user_selection()

        # Debug: Check fetched data
        print("Debug: user_selection data before DataFrame creation:", user_selection)

        # Convert to DataFrame for exporting
        df = pd.DataFrame(user_selection)  # Automatically infer columns

        # Save DataFrame to Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Workout Plan')

        # Return Excel file as response
        output.seek(0)
        return Response(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment;filename=workout_plan.xlsx"}
        )
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500


if __name__ == "__main__":
    app.run(debug=True)
