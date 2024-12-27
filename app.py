import sqlite3
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, Response
import pandas as pd
from utils import (
    initialize_database,
    get_exercises,
    add_exercise,
    get_user_selection,
    calculate_weekly_summary,
    get_workout_logs,
    calculate_exercise_categories,
)
from utils.session_summary import calculate_session_summary
from utils.database import DatabaseHandler
from utils.volume_classifier import (
    get_volume_class, 
    get_volume_label, 
    get_volume_tooltip,
    get_category_tooltip,
    get_subcategory_tooltip
)

app = Flask(__name__)

# Initialize the database
initialize_database()

@app.route("/")
def index():
    return redirect("/workout_plan")

def fetch_unique_values(column):
    """
    Fetch unique values for a specified column from the exercises table.
    Handles both dictionary and tuple-based query results.
    :param column: The column name to fetch unique values for.
    :return: A list of unique values from the specified column.
    """
    query = f"SELECT DISTINCT {column} FROM exercises WHERE {column} IS NOT NULL ORDER BY {column} ASC"
    try:
        with DatabaseHandler() as db_handler:
            results = db_handler.fetch_all(query)
            # Handle both dictionary and tuple results
            if results and isinstance(results[0], dict):
                return [row[column] for row in results if row[column]]
            else:
                return [row[0] for row in results if row[0]]
    except sqlite3.Error as db_error:
        print(f"Database error while fetching unique values for column '{column}': {db_error}")
        return []
    except Exception as e:
        print(f"Unexpected error while fetching unique values for column '{column}': {e}")
        return []
    

@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    """
    Apply filters to the exercises based on user input.
    """
    try:
        filters = request.get_json()
        print(f"DEBUG: Received raw filters: {filters}")

        # Define valid fields for filtering
        valid_fields = [
            "primary_muscle_group", "secondary_muscle_group", "tertiary_muscle_group",
            "target_muscles", "utility", "grips", "stabilizers", "synergists",
            "force", "equipment", "mechanic", "difficulty"
        ]

        # Convert field names from frontend to match database columns
        field_mapping = {
            "Primary Muscle Group": "primary_muscle_group",
            "Secondary Muscle Group": "secondary_muscle_group",
            "Tertiary Muscle Group": "tertiary_muscle_group",
            "Target Muscles": "target_muscles",
            "Force": "force",
            "Equipment": "equipment",
            "Mechanic": "mechanic",
            "Difficulty": "difficulty",
            "Utility": "utility",
            "Grips": "grips",
            "Stabilizers": "stabilizers",
            "Synergists": "synergists"
        }

        # Convert frontend field names to database column names
        sanitized_filters = {}
        for key, value in filters.items():
            db_field = field_mapping.get(key)
            if db_field and value and db_field in valid_fields:
                sanitized_filters[db_field] = value
            elif key != 'routine':
                print(f"DEBUG: Unmatched filter field: {key}")

        print(f"DEBUG: Sanitized filters: {sanitized_filters}")

        # Fetch exercises based on filters
        exercise_names = get_exercises(filters=sanitized_filters)
        
        if not exercise_names:
            print("DEBUG: No exercises match the provided filters.")
            return jsonify({"message": "No exercises match the provided filters."}), 404

        print(f"DEBUG: Found {len(exercise_names)} matching exercises")
        return jsonify(exercise_names), 200

    except Exception as e:
        print(f"Error in filter_exercises: {e}")
        return jsonify({"error": "Unable to filter exercises"}), 500
    

@app.route("/workout_plan")
def workout_plan():
    try:
        exercises = get_exercises() or []
        user_selection = get_user_selection() or []

        filters = {
            "Primary Muscle Group": fetch_unique_values("primary_muscle_group"),
            "Secondary Muscle Group": fetch_unique_values("secondary_muscle_group"),
            "Tertiary Muscle Group": fetch_unique_values("tertiary_muscle_group"),
            "Target Muscles": fetch_unique_values("target_muscles"),
            "Utility": fetch_unique_values("utility"),
            "Grips": fetch_unique_values("grips"),
            "Stabilizers": fetch_unique_values("stabilizers"),
            "Synergists": fetch_unique_values("synergists"),
            "Force": fetch_unique_values("force"),
            "Equipment": fetch_unique_values("equipment"),
            "Mechanic": fetch_unique_values("mechanic"),
            "Difficulty": fetch_unique_values("difficulty"),
        }

        print(f"DEBUG: Rendering template with exercises={len(exercises)}, user_selection={len(user_selection)}, filters={len(filters)}")
        return render_template(
            "workout_plan.html",
            exercises=exercises,
            user_selection=user_selection,
            filters=filters,
            routineOptions={
                "4 Week Split": ["A1", "B1", "A2", "B2"],
                "Full Body": ["Fullbody1", "Fullbody2", "Fullbody3"],
                "Push, Pull, Legs": ["Push1", "Pull1", "Legs1", "Push2", "Pull2", "Legs2"],
                "2 Days Split": ["A", "B"],
                "Upper Lower": ["Upper1", "Lower1", "Upper2", "Lower2"],
                "3 Days Split": ["A", "B", "C"],
            },
            enumerate=enumerate,
        )
    except Exception as e:
        print(f"Error in workout_plan: {e}")
        return render_template("error.html", message="Unable to load workout plan."), 500


@app.route("/get_workout_plan", methods=["GET"])
def get_workout_plan():
    """
    Fetch all workout plan data.
    """
    query = """
    SELECT 
        us.id, us.routine, us.exercise, us.sets, us.min_rep_range, 
        us.max_rep_range, us.rir, us.weight,
        e.primary_muscle_group, e.secondary_muscle_group, 
        e.tertiary_muscle_group, e.target_muscles, e.utility, 
        e.grips, e.stabilizers, e.synergists
    FROM user_selection us
    JOIN exercises e ON us.exercise = e.exercise_name;
    """
    try:
        with DatabaseHandler() as db_handler:
            results = db_handler.fetch_all(query)
            print(f"DEBUG: Retrieved workout plan data: {results}")
            return jsonify(results), 200
    except Exception as e:
        print(f"Error in get_workout_plan: {e}")
        return jsonify({"error": "Unable to fetch workout plan"}), 500


@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    """
    Add a new exercise to the user's workout plan.
    """
    try:
        data = request.get_json()
        print(f"DEBUG: Received data for add_exercise: {data}")

        required_fields = ["exercise", "routine", "sets", "min_rep_range", "max_rep_range", "weight"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        exercise = data["exercise"]
        routine = data["routine"]
        sets = data["sets"]
        min_rep_range = data["min_rep_range"]
        max_rep_range = data["max_rep_range"]
        rir = data.get("rir", 0)  # Default to 0 if not provided
        weight = data["weight"]

        # Insert into database
        query = """
        INSERT INTO user_selection 
        (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with DatabaseHandler() as db_handler:
                db_handler.execute_query(
                    query, 
                    (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
                )
                
                # Get the ID of the newly inserted exercise
                new_id = db_handler.cursor.lastrowid
                
                # Fetch the complete exercise details including the new ID
                details_query = """
                SELECT 
                    us.id, us.routine, us.exercise, us.sets, 
                    us.min_rep_range, us.max_rep_range, us.rir, us.weight,
                    e.primary_muscle_group, e.secondary_muscle_group, 
                    e.tertiary_muscle_group, e.target_muscles, e.utility,
                    e.grips, e.stabilizers, e.synergists
                FROM user_selection us
                JOIN exercises e ON us.exercise = e.exercise_name
                WHERE us.id = ?
                """
                exercise_details = db_handler.fetch_one(details_query, (new_id,))
                
                if not exercise_details:
                    raise Exception("Failed to fetch newly added exercise details")
                
                print(f"DEBUG: Added exercise with ID {new_id}: {exercise_details}")
                return jsonify({
                    "message": "Exercise added successfully!",
                    "data": [exercise_details]
                }), 200

        except sqlite3.Error as e:
            print(f"Database error in add_exercise: {e}")
            return jsonify({"message": f"Database error: {str(e)}"}), 500

    except Exception as e:
        print(f"Error in add_exercise: {e}")
        return jsonify({"error": "Unable to add exercise"}), 500

@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    try:
        data = request.get_json()
        print(f"DEBUG: Received data for remove_exercise: {data}")

        exercise_id = data.get("id")
        if not exercise_id or not str(exercise_id).isdigit():
            return jsonify({"message": "Invalid exercise ID"}), 400

        query = "DELETE FROM user_selection WHERE id = ?"
        with DatabaseHandler() as db_handler:
            db_handler.execute_query(query, (int(exercise_id),))

        print(f"DEBUG: Deleted exercise with ID = {exercise_id}")
        return jsonify({"message": "Exercise removed successfully"}), 200
    except Exception as e:
        print(f"Error in remove_exercise: {e}")
        return jsonify({"error": "Unable to remove exercise"}), 500

@app.route("/weekly_summary", methods=["GET"])
def weekly_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_weekly_summary(method)
        category_results = calculate_exercise_categories()
        
        if request.headers.get("Accept") == "application/json":
            return jsonify({
                "weekly_summary": results,
                "categories": category_results
            })
        
        return render_template(
            "weekly_summary.html",
            weekly_summary=results,
            categories=category_results,
            get_volume_class=get_volume_class,
            get_volume_label=get_volume_label,
            get_volume_tooltip=get_volume_tooltip,
            get_category_tooltip=get_category_tooltip,
            get_subcategory_tooltip=get_subcategory_tooltip
        )
    except Exception as e:
        print(f"Error in weekly_summary: {e}")
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Unable to fetch weekly summary"}), 500
        return render_template("error.html", message="Unable to load weekly summary."), 500

@app.route("/session_summary", methods=["GET"])
def session_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_session_summary(method)
        category_results = calculate_exercise_categories()
        
        if request.headers.get("Accept") == "application/json":
            return jsonify({
                "session_summary": results,
                "categories": category_results
            })
        
        return render_template(
            "session_summary.html",
            session_summary=results,
            categories=category_results,
            get_volume_class=get_volume_class,
            get_volume_label=get_volume_label,
            get_volume_tooltip=get_volume_tooltip,
            get_category_tooltip=get_category_tooltip,
            get_subcategory_tooltip=get_subcategory_tooltip
        )
    except Exception as e:
        print(f"Error in session_summary: {e}")
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Unable to fetch session summary"}), 500
        return render_template("error.html", message="Unable to load session summary."), 500

@app.route("/export_to_excel", methods=["GET"])
def export_to_excel():
    try:
        user_selection = get_user_selection()
        weekly_summary_data = calculate_weekly_summary(method="Total")
        session_summary_data = calculate_session_summary(method="Total")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pd.DataFrame(user_selection).to_excel(writer, index=False, sheet_name="Workout Plan")
            pd.DataFrame(weekly_summary_data).to_excel(writer, index=False, sheet_name="Weekly Summary")
            pd.DataFrame(session_summary_data).to_excel(writer, index=False, sheet_name="Per Session Summary")

        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_tracker_summary.xlsx"},
        )
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500

@app.route("/workout_log")
def workout_log():
    """Render the workout log page."""
    try:
        workout_logs = get_workout_logs()  # We'll create this function
        return render_template(
            "workout_log.html",
            workout_logs=workout_logs,
            enumerate=enumerate,
        )
    except Exception as e:
        print(f"Error in workout_log: {e}")
        return render_template("error.html", message="Unable to load workout log."), 500

@app.route("/export_to_workout_log", methods=["POST"])
def export_to_workout_log():
    """Export workout plan to workout log."""
    try:
        with DatabaseHandler() as db:
            # Get current workout plan
            plan_query = """
            SELECT 
                us.id, us.routine, us.exercise, us.sets, 
                us.min_rep_range, us.max_rep_range, us.rir, us.weight
            FROM user_selection us
            """
            workout_plan = db.fetch_all(plan_query)

            # Insert each exercise into workout log
            insert_query = """
            INSERT INTO workout_log (
                workout_plan_id, routine, exercise, planned_sets,
                planned_min_reps, planned_max_reps, planned_rir, planned_weight
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for exercise in workout_plan:
                db.execute_query(
                    insert_query,
                    (
                        exercise["id"],
                        exercise["routine"],
                        exercise["exercise"],
                        exercise["sets"],
                        exercise["min_rep_range"],
                        exercise["max_rep_range"],
                        exercise["rir"],
                        exercise["weight"]
                    )
                )

        return jsonify({"message": "Workout plan exported to log successfully"}), 200
    except Exception as e:
        print(f"Error exporting to workout log: {e}")
        return jsonify({"error": "Failed to export workout plan"}), 500

@app.route("/update_workout_log", methods=["POST"])
def update_workout_log():
    """Update workout log entry."""
    try:
        data = request.get_json()
        log_id = data.get("id")
        updates = data.get("updates", {})

        valid_fields = {
            "scored_weight", "scored_min_reps", 
            "scored_max_reps", "last_progression_date"
        }

        # Filter out invalid fields
        valid_updates = {k: v for k, v in updates.items() if k in valid_fields}

        if not valid_updates:
            return jsonify({"message": "No valid fields to update"}), 400

        # Build update query
        set_clause = ", ".join(f"{k} = ?" for k in valid_updates.keys())
        query = f"UPDATE workout_log SET {set_clause} WHERE id = ?"
        
        # Prepare parameters
        params = list(valid_updates.values()) + [log_id]

        with DatabaseHandler() as db:
            db.execute_query(query, params)

        return jsonify({"message": "Workout log updated successfully"}), 200
    except Exception as e:
        print(f"Error updating workout log: {e}")
        return jsonify({"error": "Failed to update workout log"}), 500

if __name__ == "__main__":
    app.run(debug=True)
