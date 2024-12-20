from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, Response
import pandas as pd
from utils import (
    initialize_database,
    get_exercises,
    add_exercise,
    get_user_selection,
    calculate_weekly_summary,
)
from utils.session_summary import calculate_session_summary
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

        # Fetch unique values for filters
        def fetch_unique_values(column):
            query = f"SELECT DISTINCT {column} FROM exercises WHERE {column} IS NOT NULL ORDER BY {column} ASC"
            with DatabaseHandler() as db_handler:
                return [row[0] for row in db_handler.fetch_all(query)]

        filters = {
            "Primary Muscle Group": fetch_unique_values("primary_muscle_group"),
            "Secondary Muscle Group": fetch_unique_values("secondary_muscle_group"),
            "Tertiary Muscle Group": fetch_unique_values("tertiary_muscle_group"),
            "Force": fetch_unique_values("force"),
            "Equipment": fetch_unique_values("equipment"),
            "Mechanic": fetch_unique_values("mechanic"),
            "Difficulty": fetch_unique_values("difficulty"),
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

@app.route("/get_workout_plan", methods=["GET"])
def get_workout_plan():
    try:
        user_selection = get_user_selection()
        return jsonify(user_selection), 200
    except Exception as e:
        print(f"Error in get_workout_plan: {e}")
        return jsonify({"error": "Unable to fetch workout plan"}), 500

@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    try:
        data = request.get_json()
        print(f"Received data for add_exercise: {data}")  # Debugging log

        routine = data.get("routine")
        exercise = data.get("exercise")
        sets = int(data.get("sets"))
        min_rep_range = int(data.get("min_rep_range"))
        max_rep_range = int(data.get("max_rep_range"))
        rir = int(data.get("rir")) if data.get("rir") else None
        weight = float(data.get("weight"))

        if not all([routine, exercise, sets, min_rep_range, max_rep_range, weight]):
            print("Missing required fields in add_exercise")
            return jsonify({"message": "Missing required fields"}), 400

        add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)

        updated_data = get_user_selection()
        return jsonify({"message": "Exercise added successfully!", "data": updated_data}), 200
    except Exception as e:
        print(f"Error in add_exercise: {e}")
        return jsonify({"error": "Unable to add exercise"}), 500

@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    try:
        data = request.get_json()
        print(f"Received data for remove_exercise: {data}")  # Debugging log

        exercise_id = data.get("id")
        if not exercise_id or not str(exercise_id).isdigit():
            print(f"Invalid request: Received ID = {exercise_id}")  # Debugging
            return jsonify({"message": "Invalid request: Missing or non-numeric exercise ID"}), 400

        with DatabaseHandler() as db_handler:
            db_handler.execute_query(
                "DELETE FROM user_selection WHERE id = ?", (int(exercise_id),)
            )
            print(f"Deleted exercise with ID = {exercise_id}")  # Debugging

        updated_data = get_user_selection()
        return jsonify({"message": "Exercise removed successfully", "data": updated_data}), 200
    except Exception as e:
        print(f"Error in remove_exercise: {e}")
        return jsonify({"error": "Unable to remove exercise"}), 500

@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    try:
        filters = request.get_json()
        print(f"Filters received: {filters}")  # Debugging log

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
        results = calculate_weekly_summary(method)

        if request.headers.get("Accept") == "application/json":
            return jsonify(results)

        return render_template("weekly_summary.html", summary=results, selected_method=method)
    except Exception as e:
        print(f"Error in weekly_summary: {e}")
        return jsonify({"error": "Unable to fetch weekly summary"}), 500

@app.route("/session_summary", methods=["GET"])
def session_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_session_summary(method)

        if request.headers.get("Accept") == "application/json":
            return jsonify(results)

        return render_template("session_summary.html", summary=results, selected_method=method)
    except Exception as e:
        print(f"Error in session_summary: {e}")
        return jsonify({"error": "Unable to fetch session summary"}), 500

@app.route("/export_to_excel", methods=["GET"])
def export_to_excel():
    try:
        # Fetch data for each tab
        user_selection = get_user_selection()  # Workout Plan Data
        weekly_summary_data = calculate_weekly_summary(method="Total")  # Weekly Summary Data
        session_summary_data = calculate_session_summary(method="Total")  # Per Session Summary Data

        # Create an in-memory output for the Excel file
        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # Write workout plan data
            user_selection_df = pd.DataFrame(user_selection)
            user_selection_df.to_excel(writer, index=False, sheet_name="Workout Plan")

            # Write weekly summary data
            weekly_summary_df = pd.DataFrame(weekly_summary_data)
            weekly_summary_df.to_excel(writer, index=False, sheet_name="Weekly Summary")

            # Write per session summary data
            session_summary_df = pd.DataFrame(session_summary_data)
            session_summary_df.to_excel(writer, index=False, sheet_name="Per Session Summary")

        # Reset the output buffer's position to the beginning
        output.seek(0)

        # Serve the Excel file for download
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_tracker_summary.xlsx"},
        )

    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500

if __name__ == "__main__":
    app.run(debug=True)
