document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-print-card]").forEach((button) => {
    button.addEventListener("click", () => {
      window.print();
    });
  });
});
