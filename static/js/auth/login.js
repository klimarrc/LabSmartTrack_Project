"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const toggleButtons = document.querySelectorAll(
    "[data-password-toggle]"
  );

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const inputId = button.dataset.passwordToggle;
      const passwordInput = document.getElementById(inputId);

      if (!passwordInput) {
        return;
      }

      const showingPassword =
        passwordInput.type === "text";

      passwordInput.type = showingPassword
        ? "password"
        : "text";

      button.textContent = showingPassword
        ? "Show password"
        : "Hide password";

      button.setAttribute(
        "aria-pressed",
        String(!showingPassword)
      );
    });
  });

  const loginForm = document.getElementById("login-form");

  loginForm?.addEventListener("submit", () => {
    const submitButton = loginForm.querySelector(
      'button[type="submit"]'
    );

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Logging in...";
    }
  });
});