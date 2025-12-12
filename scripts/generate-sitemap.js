const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://oshwetank.com';  // Must start with https://
const PAGES_DIR = './';
const OUTPUT_FILE = './sitemap.xml';

// Find all .html files
function getAllHtmlFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      if (!['node_modules', '.git', 'css', 'images', 'js', '.github', '.vscode'].includes(file)) {
        getAllHtmlFiles(filePath, fileList);
      }
    } else if (file.endsWith('.html')) {
      fileList.push(filePath);
    }
  });

  return fileList;
}

// Generate sitemap with clean URLs
function generateSitemap() {
  const htmlFiles = getAllHtmlFiles(PAGES_DIR);

  let sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n';
  sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

  htmlFiles.forEach(file => {
    // Convert file path to URL
    let urlPath = file.replace(/\\/g, '/').replace(/^\.\/?/, '');
    
    // Remove .html extension
    if (urlPath.endsWith('/index.html')) {
      urlPath = urlPath.replace('/index.html', '');
    } else {
      urlPath = urlPath.replace(/\.html$/, '');
    }
    
    // Build full URL correctly
    let fullUrl;
    if (urlPath === '') {
      fullUrl = BASE_URL + '/';  // Homepage
    } else {
      fullUrl = BASE_URL + '/' + urlPath;
    }
    
    // Clean up multiple slashes
    fullUrl = fullUrl.replace(/([^:]\/)\/+/g, '$1');

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
  
