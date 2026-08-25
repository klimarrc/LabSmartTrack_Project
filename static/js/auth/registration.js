"use strict";
/* Initialize the registration form */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById(
    "registration-form"
  );

  if (!form) {
    return;
  }

  const birthday = form.querySelector(
    '[name="birth_date"]'
  );

  const password = form.querySelector(
    '[name="password"]'
  );

  const confirmation = form.querySelector(
    '[name="confirm_password"]'
  );

  const passwordMessage = form.querySelector(
    "#password-match-message"
  );
  const toggleButtons = document.querySelectorAll(
  "[data-password-toggle]"
);


  setMaximumBirthday(birthday);
  initializePasswordToggles(form);

  if (password && confirmation) {
    const validatePasswords = () => {
      const bothCompleted =
        password.value.length > 0 &&
        confirmation.value.length > 0;

      const passwordsMatch =
        password.value === confirmation.value;

      confirmation.setCustomValidity(
        passwordsMatch
          ? ""
          : "Passwords do not match."
      );

      if (passwordMessage) {
        if (!bothCompleted) {
          passwordMessage.textContent = "";
          passwordMessage.className = "field-help";
          return passwordsMatch;
        }

        passwordMessage.textContent = passwordsMatch
          ? "Passwords match."
          : "Passwords do not match.";

        passwordMessage.className = passwordsMatch
          ? "field-help field-success"
          : "field-help field-error";
      }

      return passwordsMatch;
    };

    password.addEventListener(
      "input",
      validatePasswords
    );

    confirmation.addEventListener(
      "input",
      validatePasswords
    );

    form.addEventListener("submit", (event) => {
      validatePasswords();

      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
        return;
      }

      const submitButton = form.querySelector(
        'button[type="submit"]'
      );

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";
      }
    });
  }
});

/**
 * Initializes the password visibility toggle buttons.
 * @param {HTMLFormElement} form - The registration form element.
 */
function initializePasswordToggles(form) {
  const toggleButtons = form.querySelectorAll(
    "[data-password-toggle]"
  );

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const inputId = button.dataset.passwordToggle;
      const input = document.getElementById(inputId);

      if (!input) {
        return;
      }

      const willShow = input.type === "password";

      input.type = willShow
        ? "text"
        : "password";

      button.textContent = willShow
        ? "Hide"
        : "Show";

      button.setAttribute(
        "aria-pressed",
        String(willShow)
      );
    });
  });
}

/**
 * Sets the maximum allowable date for the birthday input field to today's date.
 * @param {HTMLInputElement} input - The birthday input element.
 */
function setMaximumBirthday(input) {
  if (!input) {
    return;
  }

  const today = new Date();
  const year = today.getFullYear();
  const month = String(
    today.getMonth() + 1
  ).padStart(2, "0");
  const day = String(
    today.getDate()
  ).padStart(2, "0");

  input.max = `${year}-${month}-${day}`;
}