"use strict";

document.addEventListener("DOMContentLoaded", () => {
    initializeRegistrationSearch();
    initializeApprovalForms();
});


function initializeRegistrationSearch() {
    const searchInput = document.querySelector(
        "#registration-search"
    );

    const rows = document.querySelectorAll(
        "#pending-registrations tbody tr"
    );

    if (!searchInput || rows.length === 0) {
        return;
    }

    searchInput.addEventListener("input", () => {
        const searchText = searchInput.value
            .trim()
            .toLowerCase();

        rows.forEach((row) => {
            const rowText = row.textContent.toLowerCase();

            row.hidden = !rowText.includes(searchText);
        });
    });
}


function initializeApprovalForms() {
    const forms = document.querySelectorAll(
        "[data-registration-action]"
    );

    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const action =
                form.dataset.registrationAction;

            const staffName =
                form.dataset.staffName ||
                "this staff member";

            const confirmed = confirmDecision(
                action,
                staffName
            );

            if (!confirmed) {
                event.preventDefault();
                return;
            }

            disableActionButtons(form);
        });
    });
}


function confirmDecision(action, staffName) {
    if (action === "approve") {
        return window.confirm(
            `Approve ${staffName} and allow access to LabSmartTrack?`
        );
    }

    if (action === "reject") {
        return window.confirm(
            `Reject ${staffName}'s registration?`
        );
    }

    return false;
}


function disableActionButtons(submittedForm) {
    const row = submittedForm.closest("tr");

    if (!row) {
        return;
    }

    const buttons = row.querySelectorAll(
        "button[type='submit']"
    );

    buttons.forEach((button) => {
        button.disabled = true;
    });

    const submittedButton = submittedForm.querySelector(
        "button[type='submit']"
    );

    if (!submittedButton) {
        return;
    }

    const action =
        submittedForm.dataset.registrationAction;

    submittedButton.textContent =
        action === "approve"
            ? "Approving..."
            : "Rejecting...";
}