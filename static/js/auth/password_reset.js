"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const forgotForm = document.querySelector("#forgot-password-form");
  forgotForm?.addEventListener("submit", () => {
    const button = forgotForm.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "Sending...";
  });

  const resetForm = document.querySelector("#reset-password-form");
  if (!resetForm) return;
  const password = resetForm.querySelector("#password");
  const confirmation = resetForm.querySelector("#confirm_password");
  const message = resetForm.querySelector("[data-password-message]");

  const validate = () => {
    const matches = password.value === confirmation.value;
    confirmation.setCustomValidity(matches ? "" : "Passwords do not match.");
    if (message) message.textContent = matches ? "" : "Passwords do not match.";
  };
  password.addEventListener("input", validate);
  confirmation.addEventListener("input", validate);
  resetForm.addEventListener("submit", (event) => {
    validate();
    if (!resetForm.checkValidity()) {
      event.preventDefault();
      resetForm.reportValidity();
      return;
    }
    const button = resetForm.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "Changing...";
  });
});
