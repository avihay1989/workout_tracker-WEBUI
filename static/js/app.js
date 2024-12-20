document.addEventListener("DOMContentLoaded", () => {
    function showToast(message, isError = false, duration = 3000) {
        const toastBody = document.getElementById("toast-body");
        if (!toastBody) {
            console.error("Error: toast-body not found in the DOM!");
            return;
        }
        toastBody.innerText = message;

        const toastElement = document.getElementById("liveToast");
        if (!toastElement) {
            console.error("Error: liveToast not found in the DOM!");
            return;
        }
        toastElement.classList.remove("bg-success", "bg-danger");
        toastElement.classList.add(isError ? "bg-danger" : "bg-success");

        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
    }

    async function fetchWorkoutPlan() {
        const currentPath = window.location.pathname;
        if (currentPath !== "/workout_plan") {
            console.log(`DEBUG: Skipping fetchWorkoutPlan for path: ${currentPath}`);
            return;
        }

        try {
            const response = await fetch("/get_workout_plan");
            if (!response.ok) throw new Error("Failed to fetch workout plan.");
            const data = await response.json();
            console.log("DEBUG: Workout plan data fetched:", data); // Debug print
            reloadWorkoutPlan(data);
        } catch (error) {
            console.error("Error loading workout plan:", error);
            showToast("Unable to load workout plan. Please try again later.", true);
        }
    }

    function reloadWorkoutPlan(data) {
        const workoutTable = document.getElementById("workout-plan-table-body");
        if (!workoutTable) {
            console.error("Error: workout-plan-table-body not found in the DOM!");
            showToast("Error loading workout plan. Please refresh the page.", true);
            return;
        }

        workoutTable.innerHTML = ""; // Clear existing rows

        if (!data || data.length === 0) {
            workoutTable.innerHTML = `
                <tr>
                    <td colspan="12" class="text-center text-muted">No exercises in the workout plan.</td>
                </tr>`;
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.routine}</td>
                <td>${item.exercise}</td>
                <td>${item.primary_muscle_group || "N/A"}</td>
                <td>${item.secondary_muscle_group || "N/A"}</td>
                <td>${item.tertiary_muscle_group || "N/A"}</td>
                <td>${item.sets}</td>
                <td>${item.min_rep_range}</td>
                <td>${item.max_rep_range}</td>
                <td>${item.rir || "N/A"}</td>
                <td>${item.weight}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="removeExercise(${item.id})">Remove</button>
                </td>`;
            workoutTable.appendChild(row);
        });
    }

    async function addExercise() {
        const addButton = document.querySelector("#add-exercise-btn");
        if (addButton) addButton.disabled = true; // Prevent multiple submissions

        try {
            const data = {
                routine: document.getElementById("routine")?.value,
                exercise: document.getElementById("exercise")?.value,
                sets: document.getElementById("sets")?.value,
                min_rep_range: document.getElementById("min_rep_range")?.value,
                max_rep_range: document.getElementById("max_rep_range")?.value,
                rir: document.getElementById("rir")?.value,
                weight: document.getElementById("weight")?.value,
            };

            console.log("DEBUG: Add exercise data:", data); // Debug print

            if (!data.routine || !data.exercise) {
                showToast("Routine and Exercise fields are required.", true);
                return;
            }

            const response = await fetch("/add_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                console.log("DEBUG: Exercise added successfully:", result); // Debug print
                showToast(result.message || "Exercise added successfully!");
                reloadWorkoutPlan(result.data);
            } else {
                console.error("Error adding exercise:", result.message);
                showToast(result.message || "Failed to add exercise.", true);
            }
        } catch (error) {
            console.error("Error adding exercise:", error);
            showToast(`Unable to add exercise: ${error.message}`, true);
        } finally {
            if (addButton) addButton.disabled = false; // Re-enable the button
        }
    }

    async function removeExercise(exerciseId) {
        if (!exerciseId) {
            console.error("Error: exercise ID is required to remove an exercise.");
            showToast("Exercise ID is missing. Unable to remove exercise.", true);
            return;
        }

        try {
            const response = await fetch("/remove_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: exerciseId }),
            });

            const result = await response.json();

            if (response.ok) {
                console.log("DEBUG: Exercise removed successfully:", result); // Debug print
                showToast(result.message || "Exercise removed successfully!");
                reloadWorkoutPlan(result.data);
            } else {
                console.error("Error removing exercise:", result.message);
                showToast(result.message || "Failed to remove exercise.", true);
            }
        } catch (error) {
            console.error("Error removing exercise:", error);
            showToast(`Unable to remove exercise: ${error.message}`, true);
        }
    }

    async function filterExercises() {
        const filters = {
            primary_muscle_group: document.getElementById("Primary Muscle Group")?.value,
            secondary_muscle_group: document.getElementById("Secondary Muscle Group")?.value,
            tertiary_muscle_group: document.getElementById("Tertiary Muscle Group")?.value,
            force: document.getElementById("Force")?.value,
            equipment: document.getElementById("Equipment")?.value,
            mechanic: document.getElementById("Mechanic")?.value,
            difficulty: document.getElementById("Difficulty")?.value,
        };

        const exerciseDropdown = document.getElementById("exercise");
        if (!exerciseDropdown) {
            console.error("Error: exercise dropdown not found in the DOM!");
            return;
        }
        exerciseDropdown.innerHTML = '<option value="">Loading...</option>';

        try {
            const response = await fetch("/filter_exercises", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(filters),
            });

            const data = await response.json();
            console.log("DEBUG: Data received for exercises dropdown:", data); // Debug print

            if (response.ok) {
                exerciseDropdown.innerHTML = ""; // Clear current options
                if (data.length === 0) {
                    exerciseDropdown.innerHTML = '<option value="">No exercises available</option>';
                } else {
                    data.forEach((exercise) => {
                        if (exercise && exercise.trim() !== "") {
                            const option = document.createElement("option");
                            option.value = exercise;
                            option.textContent = exercise;
                            exerciseDropdown.appendChild(option);
                        }
                    });
                }
                console.log("DEBUG: Dropdown populated successfully."); // Debug print
                showToast("Exercises filtered successfully!");
            } else {
                console.error("Error filtering exercises:", data.message);
                showToast(data.message || "Failed to filter exercises.", true);
            }
        } catch (error) {
            console.error("Error filtering exercises:", error);
            showToast(`Unable to filter exercises: ${error.message}`, true);
        }
    }

    function exportToExcel() {
        window.location.href = "/export_to_excel";
    }

    // Attach functions to global scope
    window.addExercise = addExercise;
    window.removeExercise = removeExercise;
    window.filterExercises = filterExercises;
    window.exportToExcel = exportToExcel;

    // Initialize listeners
    const filterButton = document.getElementById("filter-btn");
    if (filterButton) {
        filterButton.addEventListener("click", (e) => {
            e.preventDefault();
            filterExercises();
        });
    }

    const addExerciseForm = document.getElementById("add-exercise-form");
    if (addExerciseForm) {
        addExerciseForm.removeEventListener("submit", handleAddExercise);
        addExerciseForm.addEventListener("submit", handleAddExercise);
    } else {
        console.error("Error: add-exercise-form not found in the DOM!");
    }

    fetchWorkoutPlan(); // Load workout plan on page load
});

function handleAddExercise(event) {
    event.preventDefault();
    addExercise();
}
