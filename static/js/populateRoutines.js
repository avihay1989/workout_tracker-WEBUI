// Function to show a toast notification
function showToast(message, isError = false) {
    const toastBody = document.getElementById("toast-body");
    toastBody.innerText = message;

    const toastElement = document.getElementById("liveToast");
    toastElement.classList.remove("bg-success", "bg-danger");
    toastElement.classList.add(isError ? "bg-danger" : "bg-success");

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

// Access the global routineOptions variable
const routineOptions = window.routineOptions;

// Function to populate routines based on the selected split type
function populateRoutines() {
    const splitType = document.getElementById("routineType").value;
    const routineDropdown = document.getElementById("routine");

    // Clear current options
    routineDropdown.innerHTML = '<option value="">Select Routine</option>';

    // Populate routines based on the selected split type
    if (routineOptions[splitType] && routineOptions[splitType].length > 0) {
        routineOptions[splitType].forEach((routine) => {
            const option = document.createElement("option");
            option.value = routine;
            option.textContent = routine;
            routineDropdown.appendChild(option);
        });
        showToast("Routines populated successfully!");
    } else {
        showToast("No routines available for the selected split type.", true);
    }
}
