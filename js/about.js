document.addEventListener("DOMContentLoaded", () => {
  const timelineItems = document.querySelectorAll(".timeline-item");
  timelineItems.forEach((item) => {
    const toggle = item.querySelector(".timeline-toggle");
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      item.classList.toggle("is-open");
    });
  });

  // Skill bar animations
  const skillItems = document.querySelectorAll("[data-skill]");
  if (skillItems.length) {
    const skillsObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const bar = entry.target.querySelector(".skill-bar span");
            const target = entry.target.dataset.skillTarget;
            requestAnimationFrame(() => {
              bar.style.width = `${target}%`;
            });
            skillsObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    skillItems.forEach((item) => skillsObserver.observe(item));
  }
});