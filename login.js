document.addEventListener("DOMContentLoaded", function () {
    const loginButton = document.querySelector(".btn-primary");
    const emailInput = document.querySelector("input[placeholder='Email address']");
    const passwordInput = document.querySelector("input[placeholder='Password']");

    loginButton.addEventListener("click", function (event) {
        event.preventDefault();

        // Clear previous error messages
        clearErrors();

        let isValid = true;

        // Validate email address
        const email = emailInput.value.trim();
        if (!validateEmail(email)) {
            showError(emailInput, "User email doesn't match");
            isValid = false;
        }

        // Validate password
        const password = passwordInput.value.trim();
        if (!validatePassword(password)) {
            showError(passwordInput, "Password doesn't match");
            isValid = false;
        }

        // If all validations pass
        if (isValid) {
            alert("Login successful!");
            // Perform login action (e.g., send data to the server)
        }
    });

    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validatePassword(password) {
        const hasThreeUppercase = (password.match(/[A-Z]/g) || []).length >= 3;
        const hasOneSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        const hasTwoDigits = (password.match(/\d/g) || []).length >= 2;
        const isAtLeast12Chars = password.length >= 12;

        return hasThreeUppercase && hasOneSpecialChar && hasTwoDigits && isAtLeast12Chars;
    }

    function showError(input, message) {
        const error = document.createElement("small");
        error.textContent = message;
        error.style.color = "red";
        error.classList.add("error-message");
        input.parentElement.appendChild(error);
    }

    function clearErrors() {
        const errorMessages = document.querySelectorAll(".error-message");
        errorMessages.forEach((error) => error.remove());
    }
});
