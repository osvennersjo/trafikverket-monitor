from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
from urllib.parse import urljoin, urlparse

# WARNING: Please ensure you have permission to scrape this website
print("🚨 IMPORTANT: This script downloads images from alpingaraget.se")
print("📋 Please ensure you have permission to scrape this website")
print("⏳ Starting in 5 seconds... Press Ctrl+C to cancel")
time.sleep(5)

# Set up Selenium with Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

print("🔧 Setting up Chrome driver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Keep track of all unique images found across all pages
all_unique_images = set()
downloaded_images = []

def extract_product_images_from_page(page_url, page_num=1):
    """Extract product images from a single page"""
    try:
        print(f"🌐 Loading page {page_num}: {page_url}")
        driver.get(page_url)
        time.sleep(3)
        
        # Scroll to load any lazy-loaded images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Find product images
        selectors_to_try = [
            "div.product-card img",
            ".product-card img", 
            "div[class*='product'] img",
            "img[src*='pub_images']",
            ".product-item img",
            ".item img"
        ]
        
        page_images = set()
        for selector in selectors_to_try:
            try:
                images = driver.find_elements(By.CSS_SELECTOR, selector)
                for img in images:
                    src = img.get_attribute("src") or img.get_attribute("data-src")
                    if src and "pub_images" in src and "/original/" in src:
                        # Skip icons and small images
                        if not any(skip in src.lower() for skip in ['logo', 'facebook', 'instagram', 'tik-tok', 'icon', 'rocket', 'mountain', 'peace', 'clap']):
                            page_images.add(src)
                            
                if page_images:
                    print(f"✅ Found {len(page_images)} product images with selector: {selector}")
                    break
            except Exception as e:
                continue
        
        print(f"📊 Page {page_num}: Found {len(page_images)} unique product images")
        return page_images
        
    except Exception as e:
        print(f"❌ Error loading page {page_num}: {e}")
        return set()

try:
    # Strategy 1: Try different base URLs and parameters
    base_urls_to_try = [
        "https://alpingaraget.se/skidor/skidor",
        "https://alpingaraget.se/skidor/skidor?orderBy=NAME&direction=ASCENDING",
        "https://alpingaraget.se/skidor/skidor?orderBy=PRICE&direction=ASCENDING",
        "https://alpingaraget.se/skidor/skidor?show=all",
        "https://alpingaraget.se/skidor/skidor?limit=500",
        "https://alpingaraget.se/skidor/skidor?per_page=500",
        "https://alpingaraget.se/skidor/skidor?pageSize=500"
    ]
    
    best_url = None
    max_images_found = 0
    
    for base_url in base_urls_to_try:
        print(f"\n🔍 Trying base URL: {base_url}")
        images_found = extract_product_images_from_page(base_url, "test")
        if len(images_found) > max_images_found:
            max_images_found = len(images_found)
            best_url = base_url
            print(f"🎯 New best URL found! {len(images_found)} images")
        all_unique_images.update(images_found)
    
    print(f"\n✅ Best performing URL: {best_url} with {max_images_found} images")
    
    # Strategy 2: Try pagination if we still don't have enough images
    if len(all_unique_images) < 100:
        print(f"\n🔄 Current total: {len(all_unique_images)} images. Trying pagination...")
        
        for page in range(2, 21):  # Try pages 2-20
            found_new_images = False
            
            pagination_patterns = [
                f"{best_url}?page={page}",
                f"{best_url}&page={page}",
                f"{best_url}?p={page}",
                f"{best_url}&p={page}",
                f"{best_url}?offset={page*20}",
                f"{best_url}&offset={page*20}"
            ]
            
            for pattern in pagination_patterns:
                if page == 2:  # Only print pattern info on first iteration
                    print(f"🔄 Trying pagination pattern: {pattern}")
                
                page_images = extract_product_images_from_page(pattern, page)
                
                new_images = page_images - all_unique_images
                if new_images:
                    print(f"🎉 Page {page}: Found {len(new_images)} NEW images!")
                    all_unique_images.update(new_images)
                    found_new_images = True
                    break  # Found working pagination pattern, use it
                elif page_images:
                    print(f"ℹ️  Page {page}: Found {len(page_images)} images (all duplicates)")
                    
            if not found_new_images and page > 5:
                print(f"❌ No new images found on page {page}, stopping pagination")
                break
    
    # Strategy 3: Try different category approaches
    if len(all_unique_images) < 150:
        print(f"\n🔄 Current total: {len(all_unique_images)} images. Trying category approach...")
        
        category_urls = [
            "https://alpingaraget.se/skidor/skidor/freeride",
            "https://alpingaraget.se/skidor/skidor/all-mountain", 
            "https://alpingaraget.se/skidor/skidor/carving",
            "https://alpingaraget.se/skidor/skidor/touring",
            "https://alpingaraget.se/skidor/skidor/race",
            "https://alpingaraget.se/skidor/skidor/dam",
            "https://alpingaraget.se/skidor/skidor/herr",
            "https://alpingaraget.se/skidor/skidor/junior"
        ]
        
        for cat_url in category_urls:
            print(f"🏷️  Trying category: {cat_url}")
            cat_images = extract_product_images_from_page(cat_url, f"category")
            new_images = cat_images - all_unique_images
            if new_images:
                print(f"🎉 Category: Found {len(new_images)} NEW images!")
                all_unique_images.update(new_images)

    print(f"\n🎯 FINAL TOTAL: {len(all_unique_images)} unique product images found!")
    
    if len(all_unique_images) < 100:
        print("⚠️  Still fewer than expected. The website might:")
        print("   - Use complex JavaScript pagination")
        print("   - Have changed its structure")
        print("   - Filter products based on availability")
        print("   - Require authentication or specific headers")

    # Create folder to save images
    os.makedirs("alpingaraget_images", exist_ok=True)
    print("📁 Created 'alpingaraget_images' directory")

    # Download each unique image
    successful_downloads = 0
    for idx, img_url in enumerate(sorted(all_unique_images), 1):
        try:
            print(f"⬇️  Downloading image {idx}/{len(all_unique_images)}: {img_url}")
            
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(img_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Determine file extension
            file_extension = ".jpg"
            if "content-type" in response.headers:
                content_type = response.headers["content-type"]
                if "png" in content_type:
                    file_extension = ".png"
                elif "webp" in content_type:
                    file_extension = ".webp"
            elif ".png" in img_url:
                file_extension = ".png"
            elif ".webp" in img_url:
                file_extension = ".webp"
            
            filename = f"alpingaraget_images/product_{idx:03d}{file_extension}"
            with open(filename, "wb") as file:
                file.write(response.content)
            
            successful_downloads += 1
            print(f"✅ Downloaded: {filename}")
            downloaded_images.append(filename)
            
            # Be respectful with request timing
            time.sleep(0.2)
            
        except Exception as e:
            print(f"❌ Could not download image {idx}: {e}")

    print(f"\n🎉 DOWNLOAD COMPLETE!")
    print(f"📊 Successfully downloaded: {successful_downloads}/{len(all_unique_images)} images")
    print(f"📁 Images saved in: {os.path.abspath('alpingaraget_images')}")
    
    if successful_downloads >= 150:
        print("🎯 Success! Found close to the expected ~173 images!")
    elif successful_downloads >= 100:
        print("✅ Good result! Found a substantial number of product images.")
    else:
        print("⚠️  Fewer images than expected. This might indicate:")
        print("   - The website has changed")
        print("   - Some products are out of stock/hidden")
        print("   - Additional authentication or special handling needed")

except Exception as e:
    print(f"💥 An error occurred: {e}")

finally:
    print("🔧 Closing browser...")
    driver.quit()
    print("✅ Script completed!") 