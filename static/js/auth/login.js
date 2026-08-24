"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#login-form");
  if (!form) return;
  const password = form.querySelector("#login-password");
  const toggle = form.querySelector("[data-password-toggle]");

  toggle?.addEventListener("click", () => {
    const showing = password.type === "text";
    password.type = showing ? "password" : "text";
    toggle.textContent = showing ? "Show password" : "Hide password";
  });

  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "Logging in...";
  });
});
