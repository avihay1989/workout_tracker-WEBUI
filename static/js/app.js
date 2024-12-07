document.addEventListener("DOMContentLoaded", () => {
    // Add Exercise
    const addExerciseForm = document.getElementById("add-exercise-form");
    if (addExerciseForm) {
        addExerciseForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const exerciseData = {
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
                    body: JSON.stringify(exerciseData),
                });
                const data = await response.json();
                alert(data.message);
                location.reload();
            } catch (error) {
                console.error("Error adding exercise:", error);
            }
        });
    }

    // Remove Exercise
    const workoutPlanTable = document.getElementById("workout-plan-table");
    if (workoutPlanTable) {
        workoutPlanTable.addEventListener("click", async (e) => {
            if (e.target.classList.contains("remove-exercise")) {
                const routine = e.target.getAttribute("data-routine");
                const exercise = e.target.getAttribute("data-exercise");

                if (!routine || !exercise) {
                    alert("Invalid data attributes for routine or exercise.");
                    return;
                }

                try {
                    const response = await fetch("/remove_exercise", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ routine, exercise }),
                    });
                    const data = await response.json();
                    alert(data.message);
                    location.reload();
                } catch (error) {
                    console.error("Error removing exercise:", error);
                }
            }
        });
    }

    // Filters for Exercises
    const filterForm = document.getElementById("filters-form");
    const exerciseDropdown = document.getElementById("exercise");
    if (filterForm && exerciseDropdown) {
        filterForm.addEventListener("change", async () => {
            const filters = {};
            Array.from(filterForm.elements).forEach((element) => {
                if (element.tagName === "SELECT" && element.value) {
                    filters[element.id] = element.value;
                }
            });

            try {
                const response = await fetch("/filter_exercises", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(filters),
                });
                const data = await response.json();
                exerciseDropdown.innerHTML = "";
                data.forEach((exercise) => {
                    const option = document.createElement("option");
                    option.value = exercise;
                    option.textContent = exercise;
                    exerciseDropdown.appendChild(option);
                });
            } catch (error) {
                console.error("Error filtering exercises:", error);
            }
        });
    }

    // Weekly Summary
    async function updateSummary() {
        const method = document.getElementById("method").value;
        const tableBody = document.getElementById("weekly-summary-table");
    
        try {
            const response = await fetch(`/weekly_summary?method=${method}`, {
                headers: { "Accept": "application/json" }, // Explicitly request JSON
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
    
            const data = await response.json();
    
            if (!Array.isArray(data)) {
                throw new Error("Expected an array of summary data");
            }
    
            tableBody.innerHTML = data.length
                ? data.map(row => `
                    <tr>
                        <td>${row.muscle_group || "N/A"}</td>
                        <td>${Number(row.total_sets).toFixed(1)}</td>
                        <td>${Number(row.total_reps).toFixed(1)}</td>
                        <td>${Number(row.total_weight).toFixed(1)}</td>
                    </tr>`).join("")
                : `<tr><td colspan="4" class="text-center text-muted">No data available.</td></tr>`;
        } catch (error) {
            console.error("Error fetching weekly summary:", error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">
                        Unable to fetch data. Please try again later.
                    </td>
                </tr>`;
        }
    }
    

    const methodSelect = document.getElementById("method");
    if (methodSelect) {
        methodSelect.addEventListener("change", updateSummary);
        updateSummary(); // Initial load
    }
});
