#!/usr/bin/env python3

import pandas as pd
import random
import re

def fix_variants_and_inventory():
    """Fix the CSV to have proper length variants and inventory quantities"""
    
    # Read the current CSV file
    print("📖 Reading shopify_products_with_real_urls.csv...")
    df = pd.read_csv('shopify_products_with_real_urls.csv')
    
    print(f"📊 Found {len(df)} current rows")
    
    # Real Shopify URLs to redistribute
    real_urls = [
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_004.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_012.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_007.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_017.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_042.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_014.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_027.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_015.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_005.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_018.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_019.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_041.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_043.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_032.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_037.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_036.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_035.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_040.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_055.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_010.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_048.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_029.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_073.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_061.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_049.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_016.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_070.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_057.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_009.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_071.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_076.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_011.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_090.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_077.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_091.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_084.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_096.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_097.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_082.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_089.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_088.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_065.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_064.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_094.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_024.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_095.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_013.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_047.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_058.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_063.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_054.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_039.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_002.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_075.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_003.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_001.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_033.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_008.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_050.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_102.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_085.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_059.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_101.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_106.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_080.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_072.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_092.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_030.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_105.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_086.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_079.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_006.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_025.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_098.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_112.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_099.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_046.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_021.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_114.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_051.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_078.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_052.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_023.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_067.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_083.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_060.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_113.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_068.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_118.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_026.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_122.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_066.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_100.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_022.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_053.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_125.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_044.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_123.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_124.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_137.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_131.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_111.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_138.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_140.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_133.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_129.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_130.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_020.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_121.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_104.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_117.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_139.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_144.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_145.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_142.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_146.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_126.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_069.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_147.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_151.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_157.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_081.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_031.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_107.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_158.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_156.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_149.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_103.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_134.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_119.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_164.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_163.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_153.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_170.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_136.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_162.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_169.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_148.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_120.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_127.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_172.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_175.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_177.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_135.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_132.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_045.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_182.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_093.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_185.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_108.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_167.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_150.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_190.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_171.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_187.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_191.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_141.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_189.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_143.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_181.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_178.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_174.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_168.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_179.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_152.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_160.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_110.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_155.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_087.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_038.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_173.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_184.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_074.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_166.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_154.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_186.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_183.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_180.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_188.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_034.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_128.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_165.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_161.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_176.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_109.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_115.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_062.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_116.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_028.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_056.png",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_194.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_195.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_199.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_209.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_211.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_201.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_206.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_212.jpg",
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_221.jpg"
    ]
    
    # Shuffle URLs for variety
    random.shuffle(real_urls)
    
    # New dataframe for expanded variants
    new_rows = []
    url_index = 0
    
    for index, row in df.iterrows():
        # Extract length information from the Variant SKU
        variant_sku = str(row['Variant SKU'])
        
        # Parse lengths from the SKU (format: product-name-length1;length2;length3)
        lengths = []
        if ';' in variant_sku:
            # Extract lengths after the last dash
            parts = variant_sku.split('-')
            length_part = parts[-1]  # Last part should contain lengths
            lengths = [l.strip() for l in length_part.split(';') if l.strip().isdigit()]
        
        # If no lengths found, try to extract from the handle or title
        if not lengths:
            # Look for numbers in the handle that could be lengths
            handle_numbers = re.findall(r'\b(\d{2,3})\b', str(row['Handle']))
            title_numbers = re.findall(r'\b(\d{2,3})\b', str(row['Title']))
            
            # Combine and filter for reasonable ski lengths (80-200 cm)
            all_numbers = handle_numbers + title_numbers
            lengths = [n for n in all_numbers if 80 <= int(n) <= 200]
            
            # Remove duplicates while preserving order
            seen = set()
            lengths = [x for x in lengths if not (x in seen or seen.add(x))]
        
        # If still no lengths found, use default lengths based on product type
        if not lengths:
            product_type = str(row.get('Product Category', '')).lower()
            title = str(row['Title']).lower()
            
            if 'junior' in title or 'junior' in product_type:
                lengths = ['118', '128', '138']
            else:
                lengths = ['163', '170', '177', '184']
        
        print(f"   🎿 Product '{row['Title']}': Found {len(lengths)} lengths: {lengths}")
        
        # Create a variant for each length
        for i, length in enumerate(lengths):
            new_row = row.copy()
            
            # Update variant-specific fields
            new_row['Längd'] = f"{length} cm"
            new_row['Option1 Name'] = 'Längd'
            new_row['Option1 Value'] = f"{length} cm"
            
            # Update SKU to include the specific length
            base_sku = variant_sku.split(';')[0] if ';' in variant_sku else variant_sku
            new_row['Variant SKU'] = f"{base_sku}-{length}"
            
            # Set random inventory quantity
            # 20% chance of being out of stock (0), 80% chance of having 1-100 items
            if random.random() < 0.2:  # 20% out of stock
                new_row['Variant Inventory Qty'] = 0
                inventory_status = "Out of Stock"
            else:  # 80% in stock
                new_row['Variant Inventory Qty'] = random.randint(1, 100)
                inventory_status = f"In Stock ({new_row['Variant Inventory Qty']})"
            
            # Assign unique image URL
            if url_index < len(real_urls):
                new_row['Image Src'] = real_urls[url_index]
                new_row['Variant Image'] = real_urls[url_index]
                url_index += 1
            
            # Update alt text and titles to include length
            new_row['Image Alt Text'] = f"{row['Title']} {length}cm - Product {index+1:03d}"
            new_row['SEO Title'] = f"{row['Title']} {length}cm - {row['Vendor']} | Premium Alpine Skis"
            
            print(f"      📏 {length}cm variant: {inventory_status}")
            
            new_rows.append(new_row)
    
    # Create new dataframe
    new_df = pd.DataFrame(new_rows)
    
    # Add the Längd column to the column list if it's not already there
    columns = list(new_df.columns)
    if 'Längd' not in columns:
        # Insert Längd after Option1 Value
        opt1_index = columns.index('Option1 Value') if 'Option1 Value' in columns else len(columns)
        columns.insert(opt1_index + 1, 'Längd')
        new_df = new_df.reindex(columns=columns)
    
    # Save the updated CSV
    output_file = 'shopify_products_with_variants_and_inventory.csv'
    new_df.to_csv(output_file, index=False)
    
    # Create summary
    total_variants = len(new_df)
    in_stock_variants = len(new_df[new_df['Variant Inventory Qty'] > 0])
    out_of_stock_variants = len(new_df[new_df['Variant Inventory Qty'] == 0])
    unique_products = len(new_df['Handle'].unique())
    
    print(f"\n✅ VARIANTS AND INVENTORY FIXED!")
    print(f"=" * 60)
    print(f"📊 Total variants created: {total_variants}")
    print(f"📦 Unique products: {unique_products}")
    print(f"📏 Added 'Längd' column with length information")
    print(f"📦 Inventory Distribution:")
    print(f"   • In Stock variants: {in_stock_variants} ({in_stock_variants/total_variants*100:.1f}%)")
    print(f"   • Out of Stock variants: {out_of_stock_variants} ({out_of_stock_variants/total_variants*100:.1f}%)")
    print(f"🖼️  Unique image URLs assigned: {min(url_index, len(real_urls))}")
    print(f"📁 Output file: {output_file}")
    
    # Show sample of new structure
    print(f"\n📋 Sample of new structure:")
    sample_df = new_df[['Title', 'Längd', 'Variant SKU', 'Variant Inventory Qty', 'Image Src']].head(10)
    for idx, row in sample_df.iterrows():
        print(f"   {row['Title'][:30]:<30} | {row['Längd']:<8} | Qty: {row['Variant Inventory Qty']:<3} | {row['Image Src'][-20:]}")
    
    return output_file

if __name__ == "__main__":
    fix_variants_and_inventory() 