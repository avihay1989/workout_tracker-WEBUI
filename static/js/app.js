document.addEventListener("DOMContentLoaded", () => {
    function showToast(message, isError = false) {
        const toastBody = document.getElementById("toast-body");
        toastBody.innerText = message;

        const toastElement = document.getElementById("liveToast");
        toastElement.classList.remove("bg-success", "bg-danger");
        toastElement.classList.add(isError ? "bg-danger" : "bg-success");

        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }

    async function addExercise() {
        const data = {
            routine: document.getElementById("routine").value,
            exercise: document.getElementById("exercise").value,
            sets: document.getElementById("sets").value,
            min_rep_range: document.getElementById("min_rep_range").value,
            max_rep_range: document.getElementById("max_rep_range").value,
            rir: document.getElementById("rir").value,
            weight: document.getElementById("weight").value,
        };

        try {
            const response = await fetch("/add_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                showToast(result.message || "Exercise added successfully!");
                reloadWorkoutPlan(result.data);
            } else {
                throw new Error(result.message || "Failed to add exercise.");
            }
        } catch (error) {
            console.error("Error adding exercise:", error);
            showToast("Unable to add exercise. Please try again.", true);
        }
    }

    async function removeExercise(routine, exercise) {
        try {
            const response = await fetch("/remove_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ routine, exercise }),
            });

            const result = await response.json();

            if (response.ok) {
                showToast(result.message || "Exercise removed successfully!");
                reloadWorkoutPlan(result.data);
            } else {
                throw new Error(result.message || "Failed to remove exercise.");
            }
        } catch (error) {
            console.error("Error removing exercise:", error);
            showToast("Unable to remove exercise. Please try again.", true);
        }
    }

    function reloadWorkoutPlan(data) {
        const tableBody = document.getElementById("workout-plan-table");
        tableBody.innerHTML = ""; // Clear existing rows

        data.forEach((item, index) => {
            const row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.routine}</td>
                    <td>${item.exercise}</td>
                    <td>${item.primary_muscle_group || "N/A"}</td>
                    <td>${item.secondary_muscle_group || "N/A"}</td>
                    <td>${item.tertiary_muscle_group || "N/A"}</td>
                    <td>${item.sets}</td>
                    <td>${item.min_rep_range}</td>
                    <td>${item.max_rep_range}</td>
                    <td>${item.rir}</td>
                    <td>${item.weight}</td>
                    <td>
                        <button class="btn btn-danger btn-sm"
                                onclick="removeExercise('${item.routine}', '${item.exercise}')">Remove</button>
                    </td>
                </tr>`;
            tableBody.insertAdjacentHTML("beforeend", row);
        });
    }

    async function filterExercises() {
        const filters = {
            primary_muscle_group: document.getElementById("Primary Muscle Group").value,
            secondary_muscle_group: document.getElementById("Secondary Muscle Group").value,
            tertiary_muscle_group: document.getElementById("Tertiary Muscle Group").value,
            force: document.getElementById("Force").value,
            equipment: document.getElementById("Equipment").value,
            mechanic: document.getElementById("Mechanic").value,
            difficulty: document.getElementById("Difficulty").value,
        };

        try {
            const response = await fetch("/filter_exercises", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(filters),
            });

            const data = await response.json();

            if (!response.ok) throw new Error("Failed to filter exercises.");

            const exerciseDropdown = document.getElementById("exercise");
            exerciseDropdown.innerHTML = ""; // Clear current options

            if (data.length === 0) {
                exerciseDropdown.innerHTML = '<option value="">No exercises available</option>';
            } else {
                data.forEach((exercise) => {
                    const option = document.createElement("option");
                    option.value = exercise;
                    option.textContent = exercise;
                    exerciseDropdown.appendChild(option);
                });
            }

            showToast("Exercises filtered successfully!");
        } catch (error) {
            console.error("Error filtering exercises:", error);
            showToast("Unable to filter exercises. Please try again.", true);
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
});
