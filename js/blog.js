const blogList = document.getElementById("blogList");
const searchInput = document.getElementById("blogSearch");
const tagButtons = document.querySelectorAll(".tag-btn");
const loadMoreBtn = document.getElementById("loadMoreBtn");
const emptyState = document.getElementById("emptyState");

const modal = document.getElementById("blogModal");
const modalBackdrop = document.getElementById("modalBackdrop");
const modalClose = document.getElementById("modalClose");
const modalTitle = document.getElementById("modalTitle");
const modalContent = document.getElementById("modalContent");
const modalDate = document.getElementById("modalDate");
const modalReadTime = document.getElementById("modalReadTime");
const modalTags = document.getElementById("modalTags");
const modalThumbnail = document.getElementById("modalThumbnail");

let allPosts = [];
let filteredPosts = [];
let visibleCount = 6;

const formatDate = (dateString) =>
  new Date(dateString).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric"
  });

const renderPosts = () => {
  if (!blogList) return;

  blogList.innerHTML = filteredPosts
    .slice(0, visibleCount)
    .map(
      (post) => `
    <article class="blog-card" tabindex="0" data-id="${post.id}">
      <img src="${post.thumbnail}" alt="${post.title}" class="blog-card__thumb" loading="lazy">
      <div class="blog-card__body">
        <h3>${post.title}</h3>
        <p>${post.excerpt}</p>
        <div class="card-tags">
          ${post.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}
        </div>
        <div class="blog-card__meta">
          <span>${formatDate(post.date)}</span>
          <span>${post.readTime}</span>
        </div>
      </div>
    </article>
  `
    )
    .join("");

  const hasMore = visibleCount < filteredPosts.length;
  loadMoreBtn.hidden = !hasMore;
  emptyState.hidden = filteredPosts.length > 0;

  if (filteredPosts.length === 0) {
    loadMoreBtn.hidden = true;
  }
};

const applyFilters = () => {
  const activeTagBtn = document.querySelector(".tag-btn.active");
  const activeTag = activeTagBtn ? activeTagBtn.dataset.tag : "all";
  const query = searchInput.value.trim().toLowerCase();

  filteredPosts = allPosts.filter((post) => {
    const matchesTag =
      activeTag === "all" ? true : post.tags.includes(activeTag);
    const matchesSearch =
      post.title.toLowerCase().includes(query) ||
      post.excerpt.toLowerCase().includes(query) ||
      post.tags.some((tag) => tag.toLowerCase().includes(query));
    return matchesTag && matchesSearch;
  });

  visibleCount = 6;
  renderPosts();

  const hashId = window.location.hash.replace("#", "");
  if (hashId && filteredPosts.some((post) => post.id === Number(hashId))) {
    openPost(Number(hashId));
  }
};

const openPost = (id) => {
  const post = allPosts.find((item) => item.id === id);
  if (!post) return;

  document.body.style.overflow = "hidden";
  modal.hidden = false;
  modalTitle.textContent = post.title;
  modalContent.innerHTML = post.content;
  modalDate.textContent = formatDate(post.date);
  modalReadTime.textContent = post.readTime;
  modalTags.innerHTML = post.tags
    .map((tag) => `<span class="tag">${tag}</span>`)
    .join("");
  modalThumbnail.src = post.thumbnail;
  modalThumbnail.alt = post.title;
  modalContent.scrollTop = 0;
};

const closeModal = () => {
  document.body.style.overflow = "";
  modal.hidden = true;
};

if (blogList) {
  fetch("data/blog-posts.json")
    .then((res) => res.json())
    .then((posts) => {
      allPosts = posts;
      filteredPosts = posts;
      renderPosts();
      if (window.location.hash) {
        applyFilters();
      }
    })
    .catch(() => {
      blogList.innerHTML =
        "<p>We’re updating the library. Check back soon!</p>";
      loadMoreBtn.hidden = true;
    });

  searchInput.addEventListener("input", () => {
    applyFilters();
  });

  tagButtons.forEach((button) => {
    button.addEventListener("click", () => {
      tagButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      applyFilters();
    });
  });

  loadMoreBtn.addEventListener("click", () => {
    visibleCount += 6;
    renderPosts();
  });

  blogList.addEventListener("click", (event) => {
    const card = event.target.closest(".blog-card");
    if (!card) return;
    const postId = Number(card.dataset.id);
    const post = allPosts.find(p => p.id === postId);
    if (post && post.url) {
    window.location.href = post.url; // Navigate to individual page
    }
  });


  blogList.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      const card = event.target.closest(".blog-card");
      if (card) {
        event.preventDefault();
        openPost(Number(card.dataset.id));
      }
    }
  });

  modalClose.addEventListener("click", closeModal);
  modalBackdrop.addEventListener("click", closeModal);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });

}
