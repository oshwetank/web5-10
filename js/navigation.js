const navToggle = document.getElementById("navToggle");
const navList = document.getElementById("primaryNav");

if (navToggle && navList) {
  navToggle.addEventListener("click", () => {
    const expanded = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!expanded));
    navList.classList.toggle("is-open");
  });

  navList.addEventListener("click", (event) => {
    if (event.target.matches(".nav-link")) {
      navToggle.setAttribute("aria-expanded", "false");
      navList.classList.remove("is-open");
    }
  });
}

// Smooth scroll for same-page links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (event) {
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});