// Shopify Files URL Extractor
// Run this in your browser console while on the Shopify Files page

console.log("🔍 Extracting Shopify File URLs...");

// Find all image elements and their URLs
const images = document.querySelectorAll('img[src*="cdn.shopify.com"]');
const urls = [];

images.forEach((img, index) => {
    const url = img.src;
    const filename = url.split('/').pop().split('?')[0];
    
    urls.push({
        index: index + 1,
        filename: filename,
        url: url
    });
});

console.log(`Found ${urls.length} images:`);
urls.forEach(item => {
    console.log(`${item.index}. ${item.filename}: ${item.url}`);
});

// Create downloadable CSV content
const csvContent = "Index,Filename,URL\n" + 
    urls.map(item => `${item.index},"${item.filename}","${item.url}"`).join('\n');

// Create download link
const blob = new Blob([csvContent], { type: 'text/csv' });
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'shopify_file_urls.csv';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);

console.log("📁 Downloaded shopify_file_urls.csv with all URLs!");
console.log("Now you can match these URLs to your products."); 