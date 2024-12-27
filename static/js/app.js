document.addEventListener("DOMContentLoaded", () => {
    // Function to display toast notifications
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

    // Function to fetch the current workout plan
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
            console.log("DEBUG: Workout plan data fetched:", data);
            reloadWorkoutPlan(data);
        } catch (error) {
            console.error("Error loading workout plan:", error);
            showToast("Unable to load workout plan. Please try again later.", true);
        }
    }

    // Function to reload the workout plan table with data
    function reloadWorkoutPlan(data) {
        const workoutTable = document.getElementById("workout-plan-table-body");

        if (!workoutTable) {
            console.error("Error: workout-plan-table-body not found in the DOM!");
            showToast("Error loading workout plan. Please refresh the page.", true);
            return;
        }

        // Only clear the table if we're not adding a new exercise
        if (!data || !data.length) {
            workoutTable.innerHTML = `
                <tr>
                    <td colspan="17" class="text-center text-muted">No exercises in the workout plan.</td>
                </tr>`;
            return;
        }

        // If this is a new exercise being added (from add_exercise response)
        if (data[0] && !data[0].id) {
            // Fetch the full workout plan to get proper IDs
            fetchWorkoutPlan();
            return;
        }

        // Clear existing rows
        workoutTable.innerHTML = "";

        // Add all exercises to the table
        data.forEach((item) => {
            if (!item.id) {
                console.error("Missing ID for exercise:", item);
                return;
            }

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.routine || "N/A"}</td>
                <td>${item.exercise || "N/A"}</td>
                <td>${item.primary_muscle_group || "N/A"}</td>
                <td>${item.secondary_muscle_group || "N/A"}</td>
                <td>${item.tertiary_muscle_group || "N/A"}</td>
                <td>${item.target_muscles || "N/A"}</td>
                <td>${item.utility || "N/A"}</td>
                <td>${item.sets || "N/A"}</td>
                <td>${item.min_rep_range || "N/A"}</td>
                <td>${item.max_rep_range || "N/A"}</td>
                <td>${item.rir || "N/A"}</td>
                <td>${item.weight || "N/A"}</td>
                <td>${item.grips || "N/A"}</td>
                <td>${item.stabilizers || "N/A"}</td>
                <td>${item.synergists || "N/A"}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="removeExercise(${item.id})">Remove</button>
                </td>`;
            workoutTable.appendChild(row);
        });
    }

    // Function to add a new exercise to the workout plan
    async function addExercise() {
        const addButton = document.querySelector("#add-exercise-btn");
        if (addButton) addButton.disabled = true;

        try {
            const data = {
                routine: document.getElementById("routine")?.value,
                exercise: document.getElementById("exercise")?.value,
                sets: parseInt(document.getElementById("sets")?.value, 10),
                min_rep_range: parseInt(document.getElementById("min_rep_range")?.value, 10),
                max_rep_range: parseInt(document.getElementById("max_rep_range")?.value, 10),
                rir: parseInt(document.getElementById("rir")?.value, 10),
                weight: parseInt(document.getElementById("weight")?.value, 10)
            };

            console.log("DEBUG: Add exercise data:", data);

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
                console.log("DEBUG: Exercise added successfully:", result);
                showToast(result.message || "Exercise added successfully!");
                // Instead of using the response data directly, fetch the full workout plan
                fetchWorkoutPlan();
            } else {
                console.error("Error adding exercise:", result.message);
                showToast(result.message || "Failed to add exercise.", true);
            }
        } catch (error) {
            console.error("Error adding exercise:", error);
            showToast(`Unable to add exercise: ${error.message}`, true);
        } finally {
            if (addButton) addButton.disabled = false;
        }
    }

    // Function to remove an exercise from the workout plan
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
                console.log("DEBUG: Exercise removed successfully:", result);
                showToast(result.message || "Exercise removed successfully!");
                // Use fetchWorkoutPlan instead of reloadWorkoutPlan
                fetchWorkoutPlan();
            } else {
                console.error("Error removing exercise:", result.message);
                showToast(result.message || "Failed to remove exercise.", true);
            }
        } catch (error) {
            console.error("Error removing exercise:", error);
            showToast(`Unable to remove exercise: ${error.message}`, true);
        }
    }

    // Function to filter exercises
    async function filterExercises() {
        // Collect filter values from the DOM
        const filters = {};
        
        // Get all select elements from the filters form
        const filterSelects = document.querySelectorAll('#filters-form select');
        
        // Collect values from all filter selects
        filterSelects.forEach(select => {
            if (select.value) {  // Only add non-empty values
                filters[select.id] = select.value;
            }
        });

        console.log("DEBUG: Raw filters collected:", filters);

        // Filter out null, undefined, or empty values
        const validFilters = Object.fromEntries(
            Object.entries(filters).filter(([_, value]) => value && value !== "")
        );

        console.log("DEBUG: Filters being sent to backend:", validFilters);

        const exerciseDropdown = document.getElementById("exercise");
        if (!exerciseDropdown) {
            console.error("Error: Exercise dropdown not found in the DOM!");
            showToast("Error: Exercise dropdown is missing from the page. Please refresh the page.", true);
            return;
        }

        // Don't proceed if no filters are selected
        if (Object.keys(validFilters).length === 0) {
            showToast("Please select at least one filter", true);
            return;
        }

        // Display loading indicator in the dropdown
        exerciseDropdown.innerHTML = '<option value="">Loading...</option>';

        try {
            const response = await fetch("/filter_exercises", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(validFilters),
            });

            const data = await response.json();

            if (!response.ok) {
                console.error("Response error:", data);
                showToast(data.message || "Unable to filter exercises", true);
                exerciseDropdown.innerHTML = '<option value="">Error loading exercises</option>';
                return;
            }

            exerciseDropdown.innerHTML = '<option value="">Select Exercise</option>';

            if (!data || data.length === 0) {
                console.log("DEBUG: No exercises match the filters.");
                exerciseDropdown.innerHTML = '<option value="">No exercises match the filters</option>';
                return;
            }

            data.forEach((exerciseName) => {
                const option = document.createElement("option");
                // exerciseName is now a simple string
                option.value = exerciseName;
                option.textContent = exerciseName;
                exerciseDropdown.appendChild(option);
            });

            console.log(`DEBUG: Populated dropdown with ${data.length} exercises`);
            showToast(`Found ${data.length} matching exercises`);
        } catch (error) {
            console.error("Error filtering exercises:", error);
            showToast("Unable to filter exercises. Please try again.", true);
            exerciseDropdown.innerHTML = '<option value="">Error loading exercises</option>';
        }
    }
    
    // Attach functions to the global scope
    window.addExercise = addExercise;
    window.removeExercise = removeExercise;
    window.filterExercises = filterExercises;

    // Initialize event listeners
    document.getElementById("filter-btn")?.addEventListener("click", (e) => {
        e.preventDefault();
        filterExercises();
    });

    document.getElementById("add-exercise-btn")?.addEventListener("click", addExercise);

    fetchWorkoutPlan();

    document.getElementById('export-to-log-btn')?.addEventListener('click', async function() {
        try {
            const response = await fetch('/export_to_workout_log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showToast(result.message);
                // Optionally redirect to workout log
                window.location.href = '/workout_log';
            } else {
                throw new Error(result.error || 'Failed to export workout plan');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to export workout plan', true);
        }
    });
});
