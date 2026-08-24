"use strict";

document.addEventListener("DOMContentLoaded", () => {
  initializeNavigation();
  initializeFlashMessages();
  initializeFormProtection();
  initializeExternalLinks();
});


/**
 * Highlight the navigation link for the current page.
 */
function initializeNavigation() {
  const currentPath = window.location.pathname;
  const navigationLinks = document.querySelectorAll(
    ".nav-list a"
  );

  navigationLinks.forEach((link) => {
    const linkPath = new URL(
      link.href,
      window.location.origin
    ).pathname;

    const isDashboard =
      linkPath === "/" && currentPath === "/";

    const isSection =
      linkPath !== "/" &&
      currentPath.startsWith(linkPath);

    if (isDashboard || isSection) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}


/**
 * Allow flash messages to be dismissed.
 */
function initializeFlashMessages() {
  const closeButtons = document.querySelectorAll(
    ".flash-close"
  );

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const message = button.closest(".flash-message");

      if (message) {
        message.remove();
      }
    });
  });
}


/**
 * Prevent forms from being submitted repeatedly.
 */
function initializeFormProtection() {
  const forms = document.querySelectorAll(
    "form[data-prevent-double-submit]"
  );

  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      if (form.dataset.submitting === "true") {
        return;
      }

      form.dataset.submitting = "true";

      const submitButton = form.querySelector(
        'button[type="submit"], input[type="submit"]'
      );

      if (!submitButton) {
        return;
      }

      submitButton.disabled = true;

      if (submitButton.tagName === "BUTTON") {
        submitButton.dataset.originalText =
          submitButton.textContent;

        submitButton.textContent =
          submitButton.dataset.submittingText ||
          "Processing...";
      }
    });
  });
}


/**
 * Protect links that open new browser tabs.
 */
function initializeExternalLinks() {
  const externalLinks = document.querySelectorAll(
    'a[target="_blank"]'
  );

  externalLinks.forEach((link) => {
    const relValues = new Set(
      (link.getAttribute("rel") || "")
        .split(/\s+/)
        .filter(Boolean)
    );

    relValues.add("noopener");
    relValues.add("noreferrer");

    link.setAttribute(
      "rel",
      [...relValues].join(" ")
    );
  });
}