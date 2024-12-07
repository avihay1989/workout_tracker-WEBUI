document.addEventListener("DOMContentLoaded", () => {
    // Add Exercise
    const form = document.getElementById("add-exercise-form");
    if (form) {
        form.addEventListener("submit", (e) => {
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

            fetch("/add_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(exerciseData),
            })
                .then((response) => response.json())
                .catch((error) => console.error("Error:", error));
            location.reload();
        });
    }

    // Remove Exercise
    const table = document.getElementById("workout-plan-table");
    if (table) {
        table.addEventListener("click", (e) => {
            if (e.target.classList.contains("remove-exercise")) {
                const routine = e.target.getAttribute("data-routine");
                const exercise = e.target.getAttribute("data-exercise");

                if (!routine || !exercise) {
                    alert("Invalid data attributes for routine or exercise.");
                    return;
                }

                fetch("/remove_exercise", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ routine, exercise }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        alert(data.message);
                        location.reload();
                    })
                    .catch((error) => console.error("Error:", error));
            }
        });
    }

    // Weekly Summary
    const methodSelect = document.getElementById("method");
    const summaryTableBody = document.querySelector("#weekly-summary-table tbody");

    function fetchWeeklySummary(method = "Total") {
        fetch(`/weekly_summary?method=${method}`)
            .then((response) => response.json())
            .then((data) => {
                summaryTableBody.innerHTML = "";

                if (data.length === 0) {
                    summaryTableBody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center text-muted">No data available.</td>
                        </tr>`;
                } else {
                    data.forEach((row) => {
                        const newRow = `
                            <tr>
                                <td>${row.muscle_group}</td>
                                <td>${row.total_sets}</td>
                                <td>${row.total_reps}</td>
                                <td>${row.total_weight}</td>
                            </tr>`;
                        summaryTableBody.insertAdjacentHTML("beforeend", newRow);
                    });
                }
            })
            .catch((error) => console.error("Error fetching summary:", error));
    }

    if (methodSelect) {
        // Fetch summary on page load
        fetchWeeklySummary();

        // Fetch summary on method change
        methodSelect.addEventListener("change", () => {
            const method = methodSelect.value;
            fetchWeeklySummary(method);
        });
    }
});
