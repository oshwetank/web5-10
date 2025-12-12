const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://oshwetank.github.io/web5-10';
const PAGES_DIR = './';
const OUTPUT_FILE = './sitemap.xml';

// Find all .html files
function getAllHtmlFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Skip directories that shouldn't be crawled
      if (!['node_modules', '.git', 'css', 'images', 'js', '.github', '.vscode'].includes(file)) {
        getAllHtmlFiles(filePath, fileList);
      }
    } else if (file.endsWith('.html')) {
      fileList.push(filePath);
    }
  });

  return fileList;
}

// Generate sitemap
function generateSitemap() {
  const htmlFiles = getAllHtmlFiles(PAGES_DIR);

  let sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n';
  sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

  htmlFiles.forEach(file => {
    // Convert file path to URL
    let urlPath = file.replace(/\\/g, '/').replace(/^\.\/?/, '');
    
    // For index.html, use just the directory
    if (urlPath.endsWith('/index.html')) {
      urlPath = urlPath.replace('/index.html', '/');
    } else {
      // Keep .html extension for non-index files
      // Uncomment line below if your server does URL rewriting (removes .html)
      // urlPath = urlPath.replace(/\.html$/, '');
    }
    
    const fullUrl = (BASE_URL + '/' + urlPath).replace(/\/+/g, '/').replace(/\/$/, '') || BASE_URL;

    sitemap += `  <url>\n`;
    sitemap += `    <loc>${fullUrl}</loc>\n`;
    sitemap += `    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>\n`;
    sitemap += `    <changefreq>weekly</changefreq>\n`;
    sitemap += `    <priority>0.8</priority>\n`;
    sitemap += `  </url>\n`;
  });

  sitemap += '</urlset>';

  fs.writeFileSync(OUTPUT_FILE, sitemap);
  console.log(`✅ Sitemap generated: ${OUTPUT_FILE}`);
}

generateSitemap();
