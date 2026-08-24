"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#registration-form");
  if (!form) return;

  const birthday = form.querySelector("#birth_date");
  const password = form.querySelector("#password");
  const confirmation = form.querySelector("#confirm_password");
  const message = form.querySelector("[data-password-message]");
  const toggle = form.querySelector("[data-password-toggle]");

  if (birthday) birthday.max = new Date().toISOString().split("T")[0];

  const validatePasswords = () => {
    const matches = password.value === confirmation.value;
    confirmation.setCustomValidity(matches ? "" : "Passwords do not match.");
    if (message) message.textContent = matches ? "" : "Passwords do not match.";
    return matches;
  };

  password.addEventListener("input", validatePasswords);
  confirmation.addEventListener("input", validatePasswords);
  toggle?.addEventListener("click", () => {
    const showing = password.type === "text";
    password.type = showing ? "password" : "text";
    toggle.textContent = showing ? "Show password" : "Hide password";
  });

  form.addEventListener("submit", (event) => {
    validatePasswords();
    if (!form.checkValidity()) {
      event.preventDefault();
      form.reportValidity();
      return;
    }
    const button = form.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "Submitting...";
  });
});

