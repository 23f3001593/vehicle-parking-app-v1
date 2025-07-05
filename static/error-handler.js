document.addEventListener("DOMContentLoaded", function () {
    const errorElement = document.getElementById("error-message");
    if (errorElement) {
        const message = errorElement.dataset.message;
        if (message) {
            alert(message);
        }
    }
});