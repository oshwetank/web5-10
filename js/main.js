document.addEventListener("DOMContentLoaded", () => {
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Intersection Observer for reveal animations
  const observedElements = document.querySelectorAll("[data-observe]");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  observedElements.forEach((el) => observer.observe(el));

  // Featured posts on home page
  const featuredContainer = document.getElementById("featuredPosts");
  if (featuredContainer) {
    fetch("data/blog-posts.json")
      .then((res) => res.json())
      .then((posts) => {
        const featured = posts
          .filter((post) => post.featured)
          .slice(0, 3);

        featuredContainer.innerHTML = featured
          .map(
            (post) => `
          <article class="featured-card">
            <img src="${post.thumbnail}" alt="${post.title}" loading="lazy">
            <div class="card-body">
              <div class="card-date">${new Date(post.date).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
                year: "numeric"
              })} • ${post.readTime}</div>
              <h3>${post.title}</h3>
              <p>${post.excerpt}</p>
              <div class="card-tags">
                ${post.tags
                  .map((tag) => `<span class="tag">${tag}</span>`)
                  .join("")}
              </div>
              <a class="text-link" href="blog.html#${post.id}">
                Read article <i class="fa-solid fa-arrow-right"></i>
              </a>
            </div>
          </article>`
          )
          .join("");
      })
      .catch(() => {
        featuredContainer.innerHTML =
          "<p>Featured posts are on the way. Check back soon!</p>";
      });
  }
});