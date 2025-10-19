const fs = require("fs");
const path = require("path");
const matter = require("gray-matter");

const postsDir = path.join(__dirname, "../data/posts");
const outputFile = path.join(__dirname, "../data/blog-posts.json");
const blogDir = path.join(__dirname, "../blog"); // Folder for individual blog pages

// Create blog directory if it doesn't exist
if (!fs.existsSync(blogDir)) {
  fs.mkdirSync(blogDir);
}

const posts = [];

fs.readdirSync(postsDir).forEach(filename => {
  if (!filename.endsWith(".md")) return;

  const filePath = path.join(postsDir, filename);
  const md = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(md);

  // Generate slug from filename
  const slug = filename.replace(".md", "");
  
  // Add to JSON array
  posts.push({
    id: Date.now() + Math.floor(Math.random() * 1000),
    title: data.title,
    date: data.date,
    excerpt: data.excerpt || content.substring(0, 120),
    thumbnail: data.thumbnail || "",
    tags: data.tags || [],
    seotitle: data.seotitle || data.title,
    seodescription: data.seodescription || data.excerpt,
    readTime: data.readTime || "3 min read",
    content: content,
    slug: slug, // Add slug for linking
    url: `blog/${slug}.html` // Full URL path
  });

  // Generate individual HTML page for this post
  const htmlContent = generatePostHTML(data, content, slug);
  fs.writeFileSync(path.join(blogDir, `${slug}.html`), htmlContent);
});

// Write JSON
fs.writeFileSync(outputFile, JSON.stringify(posts, null, 2));
console.log("blog-posts.json and individual blog pages generated!");

// HTML Template for individual blog posts
function generatePostHTML(frontmatter, content, slug) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${frontmatter.seotitle || frontmatter.title}</title>
  <meta name="description" content="${frontmatter.seodescription || frontmatter.excerpt || ''}">
  <meta property="og:title" content="${frontmatter.seotitle || frontmatter.title}">
  <meta property="og:description" content="${frontmatter.seodescription || frontmatter.excerpt || ''}">
  <meta property="og:image" content="${frontmatter.thumbnail || ''}">
  <meta property="og:url" content="https://oshwetank.com/blog/${slug}.html">
  <meta property="og:type" content="article">
  <link rel="canonical" href="https://oshwetank.com/blog/${slug}.html">
  <link rel="stylesheet" href="../css/main.css">
  <link rel="stylesheet" href="../css/blog.css">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "${frontmatter.title}",
    "description": "${frontmatter.excerpt || ''}",
    "image": "${frontmatter.thumbnail || ''}",
    "datePublished": "${frontmatter.date}",
    "author": {
      "@type": "Person",
      "name": "Shwetank Ojha"
    }
  }
  </script>
</head>
<body>
  <header class="site-header">
    <div class="logo">
      <a href="../index.html" aria-label="Shwetank Ojha Home">
        <span class="logo-mark">SO</span>
        <span class="logo-text">Shwetank Ojha</span>
      </a>
    </div>
    <nav class="site-nav">
      <ul class="nav-list">
        <li><a href="../index.html" class="nav-link">Home</a></li>
        <li><a href="../blog.html" class="nav-link">Blog</a></li>
        <li><a href="../about.html" class="nav-link">About</a></li>
        <li><a href="../contact.html" class="nav-link">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main class="blog-post-page">
    <article>
      <h1>${frontmatter.title}</h1>
      <p class="post-meta">${frontmatter.date} • ${frontmatter.readTime || '3 min read'}</p>
      <img src="../${frontmatter.thumbnail}" alt="${frontmatter.title}" style="max-width:100%; border-radius:8px; margin:1rem 0;">
      <div class="post-content">
        ${content}
      </div>
      <div class="post-tags">
        ${(frontmatter.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('')}
      </div>
    </article>
  </main>

  <footer class="site-footer">
    <p>© ${new Date().getFullYear()} Shwetank Ojha. Keep learning.</p>
  </footer>
</body>
</html>`;
}
