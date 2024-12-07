from flask import Flask, render_template, request, jsonify
from utils.helpers import (
    initialize_database,
    add_exercise,
    get_exercises,
    get_user_selection,
    calculate_weekly_summary,
    get_weekly_summary,
)
from utils.data_handler import DataHandler

app = Flask(__name__)

# Initialize the database
initialize_database()

@app.route("/")
def index():
    return redirect("/workout_plan")

@app.route("/workout_plan")
def workout_plan():
    exercises = get_exercises()
    user_selection = get_user_selection()

    # Fetch unique values for filtering
    connection = DataHandler()
    primary_muscle_groups = connection.fetch_unique_values("exercises", "primary_muscle_group")
    secondary_muscle_groups = connection.fetch_unique_values("exercises", "secondary_muscle_group")
    tertiary_muscle_groups = connection.fetch_unique_values("exercises", "tertiary_muscle_group")
    forces = connection.fetch_unique_values("exercises", "force")
    equipments = connection.fetch_unique_values("exercises", "equipment")
    mechanics = connection.fetch_unique_values("exercises", "mechanic")
    difficulties = connection.fetch_unique_values("exercises", "difficulty")
    connection.close_connection()

    return render_template(
        "workout_plan.html",
        exercises=exercises,
        user_selection=user_selection,
        primary_muscle_groups=primary_muscle_groups,
        secondary_muscle_groups=secondary_muscle_groups,
        tertiary_muscle_groups=tertiary_muscle_groups,
        forces=forces,
        equipments=equipments,
        mechanics=mechanics,
        difficulties=difficulties,
        enumerate=enumerate,
    )

@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    data = request.get_json()
    routine = data.get("routine")
    exercise = data.get("exercise")
    sets = data.get("sets")
    min_rep_range = data.get("min_rep_range")
    max_rep_range = data.get("max_rep_range")
    rir = data.get("rir")
    weight = data.get("weight")
    add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
    return jsonify({"message": "Exercise added successfully"}), 200

@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    data = request.get_json()
    routine = data.get("routine")
    exercise = data.get("exercise")

    print(f"Payload received: {data}")  # Debugging log

    if routine and exercise:
        db_handler = DataHandler()
        db_handler.execute_query(
            "DELETE FROM user_selection WHERE routine = ? AND exercise = ?",
            (routine, exercise)
        )
        db_handler.close_connection()
        return jsonify({"message": "Exercise removed successfully"}), 200

    return jsonify({"message": "Invalid request"}), 400

@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    filters = request.get_json()
    exercises = get_exercises(filters=filters)
    return jsonify(exercises)

@app.route("/weekly_summary", methods=["GET"])
def weekly_summary():
    method = request.args.get("method", "Total")  # Default to "Total" method
    calculate_weekly_summary(method=method)
    summary = get_weekly_summary()
    return render_template("weekly_summary.html", summary=summary, selected_method=method)

if __name__ == "__main__":
    app.run(debug=True)
