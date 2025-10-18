const fs = require("fs");
const path = require("path");
const matter = require("gray-matter");

const postsDir = path.join(__dirname, "../data/posts");
const outputFile = path.join(__dirname, "../data/blog-posts.json");

const posts = [];

fs.readdirSync(postsDir).forEach(filename => {
  if (!filename.endsWith(".md")) return;

  const filePath = path.join(postsDir, filename);
  const md = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(md);

  // You might want to customize this mapping to fit your blog.js expectations
  posts.push({
    id: Date.now() + Math.floor(Math.random()*1000), // Or use better unique id logic
    title: data.title,
    date: data.date,
    excerpt: data.excerpt || content.substring(0, 120),
    thumbnail: data.thumbnail || "",
    tags: data.tags || [],
    seotitle: data.seotitle || "",
    seodescription: data.seodescription || "",
    readTime: data.readTime || "3 min read", // Estimate, or use a library
    content: content // Full Markdown, you may want to convert to HTML for preview
  });
});

// Write the JSON array
fs.writeFileSync(outputFile, JSON.stringify(posts, null, 2));
console.log("blog-posts.json generated!");
