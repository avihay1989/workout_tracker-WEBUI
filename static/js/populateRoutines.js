// Access the global routineOptions variable
const routineOptions = window.routineOptions;

// Function to populate routines based on the selected split type
function populateRoutines() {
    const splitType = document.getElementById("routineType").value;
    const routineDropdown = document.getElementById("routine");

    // Clear current options
    routineDropdown.innerHTML = `<option value="">Select Routine</option>`;

    // Populate routines based on the selected split type
    if (routineOptions[splitType]) {
        routineOptions[splitType].forEach((routine) => {
            const option = document.createElement("option");
            option.value = routine;
            option.textContent = routine;
            routineDropdown.appendChild(option);
        });
    }
}
