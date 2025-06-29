# How to Extract Real Shopify Image URLs

Since you've uploaded all images to Shopify, here are **3 proven methods** to get the real CDN URLs:

## 🎯 **Method 1: Shopify Files Page (Easiest)**

### Step 1: Navigate to Files
1. **Go to Shopify Admin** → Settings → Files
2. **Find your uploaded product images**

### Step 2: Copy URLs Manually
1. **Right-click on each image** → "Copy image address"
2. **URLs will look like**: `https://cdn.shopify.com/s/files/1/0947/3435/2707/files/ACTUAL_FILENAME.jpg?v=REAL_NUMBER`
3. **Paste each URL** into the `shopify_url_mapping.csv` file

### Step 3: Fill the Mapping File
1. **Open**: `shopify_url_mapping.csv`
2. **Fill column**: `Real_Shopify_URL` with the copied URLs
3. **Match by**: Product title or expected filename

---

## 🚀 **Method 2: Browser Console Script (Automatic)**

### Step 1: Go to Shopify Files
1. **Navigate to**: Shopify Admin → Settings → Files
2. **Make sure all your images are visible** (scroll down if needed)

### Step 2: Run Browser Script
1. **Press F12** to open Developer Tools
2. **Go to Console tab**
3. **Copy and paste** the contents of `extract_urls_browser.js`
4. **Press Enter** to run the script
5. **A CSV file will be downloaded** with all URLs!

### Step 3: Match URLs to Products
1. **Open both CSV files**: downloaded URLs + `shopify_url_mapping.csv`
2. **Match by filename** or manually assign URLs to products

---

## 📦 **Method 3: Create Test Product (Quick Check)**

### Step 1: Create One Test Product
1. **Go to**: Products → Add product
2. **Add title**: "Test Product"
3. **Upload 2-3 of your images**
4. **Save product**

### Step 2: Export to See URL Format
1. **Go to**: Products → Export
2. **Select**: "All products" + "CSV format"
3. **Download and open** the CSV file
4. **Copy the image URLs** from the "Image Src" column

### Step 3: Apply the Pattern
1. **Note the URL format** (you'll see the real CDN pattern)
2. **Use the same format** for your other images
3. **Delete the test product** when done

---

## 🔧 **After Getting URLs**

### Apply Real URLs to Your CSV:
```bash
# Run the extraction helper
python3 extract_shopify_urls.py

# Choose option 2 after filling the mapping file
```

### Final Result:
- ✅ **File**: `shopify_products_with_real_urls.csv`
- ✅ **Ready for import** with working image URLs
- ✅ **All 173 variants** with real Shopify CDN URLs

---

## 💡 **Pro Tips**

### URL Format Will Be:
```
https://cdn.shopify.com/s/files/1/0947/3435/2707/files/YOUR_FILENAME.jpg?v=TIMESTAMP
```

### What Changes:
- ✅ **`YOUR_FILENAME`**: The actual filename you uploaded
- ✅ **`TIMESTAMP`**: Real version number (not 1748986989)

### What Stays the Same:
- ✅ **Domain**: `cdn.shopify.com`
- ✅ **Path**: `/s/files/1/0947/3435/2707/files/`
- ✅ **Extension**: `.jpg` (or whatever format you uploaded)

---

## 🎯 **Recommended Workflow**

1. **Use Method 2** (browser script) for bulk extraction
2. **Fill mapping file** with real URLs
3. **Run script option 2** to create final CSV
4. **Import to Shopify** with confidence!

**Files Ready:**
- 📁 `shopify_url_mapping.csv` - Fill this with real URLs
- 📁 `extract_urls_browser.js` - Run in browser console
- 📁 `extract_shopify_urls.py` - Final processing script 