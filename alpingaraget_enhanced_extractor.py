#!/usr/bin/env python3

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import hashlib
from urllib.parse import urljoin, urlparse
import pandas as pd
import random
import re

class EnhancedAlpingaragetExtractor:
    def __init__(self, target_count=550):
        self.target_count = target_count
        self.base_url = "https://alpingaraget.se"
        self.collected_urls = set()
        self.downloaded_hashes = set()
        self.downloaded_count = 0
        self.output_dir = "alpingaraget_enhanced_images"
        self.load_existing_hashes()
        self.setup_driver()
        self.setup_directories()
        
    def load_existing_hashes(self):
        """Load hashes from previous download to avoid duplicates"""
        existing_dir = "alpingaraget_550_images"
        if os.path.exists(existing_dir):
            print(f"🔄 Loading existing image hashes from {existing_dir}...")
            for filename in os.listdir(existing_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    filepath = os.path.join(existing_dir, filename)
                    try:
                        with open(filepath, 'rb') as f:
                            content = f.read()
                            image_hash = self.get_image_hash(content)
                            self.downloaded_hashes.add(image_hash)
                    except:
                        pass
            print(f"   📊 Loaded {len(self.downloaded_hashes)} existing image hashes")
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def setup_directories(self):
        """Create output directory"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created directory: {self.output_dir}")
    
    def get_image_hash(self, image_content):
        """Generate hash for image content to detect duplicates"""
        return hashlib.md5(image_content).hexdigest()
    
    def is_valid_image_url(self, url):
        """Check if URL is a valid image"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg']
        parsed = urlparse(url.lower())
        return any(parsed.path.endswith(ext) for ext in valid_extensions)
    
    def extract_all_possible_images(self, url):
        """Extract ALL possible image URLs from a page using multiple methods"""
        try:
            print(f"🔍 Deep scanning: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            page_images = set()
            
            # Method 1: Regular img tags
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            images = soup.find_all('img')
            
            for img in images:
                for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-srcset']:
                    if img.get(attr):
                        # Handle srcset with multiple URLs
                        if 'srcset' in attr:
                            urls = re.findall(r'(https?://[^\s,]+)', img.get(attr))
                            for img_url in urls:
                                img_url = img_url.split()[0]  # Remove size descriptors
                                if self.is_valid_image_url(img_url) and img_url not in self.collected_urls:
                                    page_images.add(img_url)
                                    self.collected_urls.add(img_url)
                        else:
                            img_url = urljoin(self.base_url, img.get(attr))
                            if self.is_valid_image_url(img_url) and img_url not in self.collected_urls:
                                page_images.add(img_url)
                                self.collected_urls.add(img_url)
            
            # Method 2: CSS background images
            elements_with_bg = soup.find_all(attrs={"style": True})
            for element in elements_with_bg:
                style = element.get('style', '')
                if 'background-image' in style:
                    bg_urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                    for bg_url in bg_urls:
                        full_url = urljoin(self.base_url, bg_url)
                        if self.is_valid_image_url(full_url) and full_url not in self.collected_urls:
                            page_images.add(full_url)
                            self.collected_urls.add(full_url)
            
            # Method 3: Look for URLs in text content that might be images
            all_text = soup.get_text()
            potential_urls = re.findall(r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|webp|gif)', all_text, re.IGNORECASE)
            for url in potential_urls:
                if url not in self.collected_urls:
                    page_images.add(url)
                    self.collected_urls.add(url)
            
            # Method 4: Look in script tags for image URLs
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_urls = re.findall(r'["\']https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif)[^"\']*["\']', script.string, re.IGNORECASE)
                    for url_match in script_urls:
                        url = url_match.strip('"\'')
                        if url not in self.collected_urls:
                            page_images.add(url)
                            self.collected_urls.add(url)
            
            # Method 5: Try to find image galleries or sliders
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Look for lazy-loaded images after scrolling
            soup_after_scroll = BeautifulSoup(self.driver.page_source, 'html.parser')
            new_images = soup_after_scroll.find_all('img')
            
            for img in new_images:
                for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                    if img.get(attr):
                        img_url = urljoin(self.base_url, img.get(attr))
                        if self.is_valid_image_url(img_url) and img_url not in self.collected_urls:
                            page_images.add(img_url)
                            self.collected_urls.add(img_url)
            
            print(f"   📷 Found {len(page_images)} new images on this page")
            return page_images
            
        except Exception as e:
            print(f"❌ Error scanning {url}: {e}")
            return set()
    
    def get_extensive_page_list(self):
        """Get an extensive list of pages to scan"""
        print("🗺️  Building comprehensive page list...")
        
        # Start with main categories
        main_categories = [
            "/", "/skidor", "/pjaxor", "/klader", "/utrustning", "/race", 
            "/hjälmar", "/goggles", "/lavinutrustning", "/vaskor", 
            "/skidvard", "/underkroppsklader", "/varumärken"
        ]
        
        all_pages = []
        
        # Add main category pages
        for category in main_categories:
            all_pages.append(urljoin(self.base_url, category))
        
        # Get product pages from each category with more thorough pagination
        for category in main_categories:
            try:
                category_url = urljoin(self.base_url, category)
                print(f"   🔍 Exploring category: {category}")
                self.driver.get(category_url)
                time.sleep(3)
                
                # Look for product links
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    if href:
                        # More aggressive link collection
                        if any(pattern in href for pattern in ['/produkter/', '/product/', '/p/', '/item/', '/ski/', '/boot/', '/jacket/']):
                            full_url = urljoin(self.base_url, href)
                            if full_url not in all_pages:
                                all_pages.append(full_url)
                
                # More thorough pagination
                page_num = 1
                while page_num < 20:  # Increased page limit
                    try:
                        # Try different pagination patterns
                        next_selectors = [
                            "//a[contains(@class, 'next')]",
                            "//a[contains(text(), 'Nästa')]",
                            "//a[contains(text(), 'Next')]",
                            f"//a[contains(@href, 'page={page_num + 1}')]",
                            f"//a[text()='{page_num + 1}']"
                        ]
                        
                        found_next = False
                        for selector in next_selectors:
                            try:
                                next_buttons = self.driver.find_elements(By.XPATH, selector)
                                if next_buttons and next_buttons[0].is_enabled():
                                    next_buttons[0].click()
                                    time.sleep(3)
                                    found_next = True
                                    break
                            except:
                                continue
                        
                        if not found_next:
                            break
                        
                        # Get products from this page
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link.get('href')
                            if href and any(pattern in href for pattern in ['/produkter/', '/product/', '/p/']):
                                full_url = urljoin(self.base_url, href)
                                if full_url not in all_pages:
                                    all_pages.append(full_url)
                        
                        page_num += 1
                        
                    except Exception as e:
                        print(f"   ⚠️  Pagination error on page {page_num}: {e}")
                        break
                        
            except Exception as e:
                print(f"❌ Error exploring {category}: {e}")
                continue
        
        # Add some common page patterns
        common_patterns = [
            "/nyheter", "/rea", "/outlet", "/kampanj", "/erbjudanden",
            "/inspiration", "/guider", "/tips", "/blogg", "/magasin"
        ]
        
        for pattern in common_patterns:
            all_pages.append(urljoin(self.base_url, pattern))
        
        print(f"🔍 Found {len(all_pages)} total pages to scan")
        return list(set(all_pages))  # Remove duplicates
    
    def download_image(self, url, filename):
        """Download an image and check for duplicates"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': self.base_url
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'webp', 'gif']):
                return False
            
            # Check for duplicates using hash
            image_hash = self.get_image_hash(response.content)
            if image_hash in self.downloaded_hashes:
                return False
            
            # Check minimum file size (avoid tiny images) - reduced threshold
            if len(response.content) < 500:  # Reduced from 1024 to 500 bytes
                return False
            
            # Save the image
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_hashes.add(image_hash)
            self.downloaded_count += 1
            
            # Get image info
            size_kb = len(response.content) / 1024
            print(f"   ✅ Downloaded: {filename} ({size_kb:.1f}KB)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to download {url}: {e}")
            return False
    
    def extract_all_images(self):
        """Main extraction process"""
        print(f"🎯 Enhanced extraction of {self.target_count} unique images from alpingaraget.se")
        print("=" * 70)
        
        # Get all pages to scan
        pages_to_scan = self.get_extensive_page_list()
        
        # Shuffle pages for variety
        random.shuffle(pages_to_scan)
        
        all_image_urls = set()
        
        # Scan all pages for images
        for i, page_url in enumerate(pages_to_scan, 1):
            if len(all_image_urls) >= self.target_count * 3:  # Get even more URLs
                break
                
            print(f"\n📄 Page {i}/{len(pages_to_scan)}")
            page_images = self.extract_all_possible_images(page_url)
            all_image_urls.update(page_images)
            
            print(f"📊 Total unique image URLs found: {len(all_image_urls)}")
            
            # Small delay between pages
            time.sleep(random.uniform(0.5, 2))
            
            # Stop early if we have enough URLs and time to download
            if len(all_image_urls) >= 1000 and i > 50:
                print(f"🎯 Stopping scan - have {len(all_image_urls)} URLs, starting downloads...")
                break
        
        print(f"\n🎯 Found {len(all_image_urls)} total unique image URLs")
        print("📥 Starting downloads...")
        
        # Convert to list and shuffle for variety
        image_urls_list = list(all_image_urls)
        random.shuffle(image_urls_list)
        
        # Download images
        for i, img_url in enumerate(image_urls_list, 1):
            if self.downloaded_count >= self.target_count:
                break
            
            # Generate filename
            parsed_url = urlparse(img_url)
            original_filename = os.path.basename(parsed_url.path)
            if not original_filename or '.' not in original_filename:
                original_filename = f"image_{i}.jpg"
            
            # Add counter to avoid filename conflicts
            name, ext = os.path.splitext(original_filename)
            filename = f"{self.downloaded_count + 1:03d}_{name}{ext}"
            
            print(f"\n🖼️  Downloading {i}/{len(image_urls_list)} (Got: {self.downloaded_count}/{self.target_count})")
            print(f"   📎 URL: {img_url}")
            
            success = self.download_image(img_url, filename)
            
            if success and self.downloaded_count % 50 == 0:
                print(f"\n🎉 Milestone: {self.downloaded_count} images downloaded!")
            
            # Shorter delay between downloads
            time.sleep(random.uniform(0.2, 1))
        
        print(f"\n✅ ENHANCED EXTRACTION COMPLETE!")
        print(f"📊 Downloaded: {self.downloaded_count} NEW unique images")
        print(f"📁 Location: {self.output_dir}/")
        
        self.create_summary_report()
    
    def create_summary_report(self):
        """Create a summary report of the extraction"""
        report_data = []
        
        for filename in os.listdir(self.output_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.output_dir, filename)
                file_size = os.path.getsize(filepath)
                
                report_data.append({
                    'filename': filename,
                    'size_kb': round(file_size / 1024, 2),
                    'format': filename.split('.')[-1].upper()
                })
        
        # Create DataFrame and save report
        df = pd.DataFrame(report_data)
        report_file = 'alpingaraget_enhanced_images_report.csv'
        df.to_csv(report_file, index=False)
        
        # Print summary statistics
        print(f"\n📋 ENHANCED SUMMARY REPORT")
        print("=" * 40)
        print(f"New images: {len(df)}")
        print(f"Total size: {df['size_kb'].sum():.1f} KB")
        print(f"Average size: {df['size_kb'].mean():.1f} KB")
        print(f"Format distribution:")
        print(df['format'].value_counts().to_string())
        print(f"Report saved: {report_file}")
    
    def cleanup(self):
        """Close browser and cleanup"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        print("🧹 Cleanup complete")

def main():
    extractor = EnhancedAlpingaragetExtractor(target_count=550)
    
    try:
        extractor.extract_all_images()
    except KeyboardInterrupt:
        print("\n⚠️  Extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main() 