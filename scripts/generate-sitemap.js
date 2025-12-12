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
      // Skip node_modules, .git, etc.
      if (!['node_modules', '.git', 'css', 'images', 'js', '.github'].includes(file)) {
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
    let url = file.replace(/\\/g, '/').replace(/^\.\/?/, '').replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    
    if (url === '') url = ''; // homepage
    
    const fullUrl = (BASE_URL + '/' + url).replace(/\/+/g, '/');

    sitemap += `  <url>\n`;
    sitemap += `    <loc>${fullUrl}</loc>\n`;
    sitemap += `    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>\n`;
    sitemap += `  </url>\n`;
  });

  sitemap += '</urlset>';

  fs.writeFileSync(OUTPUT_FILE, sitemap);
  console.log(`✅ Sitemap generated: ${OUTPUT_FILE}`);
}

generateSitemap();
