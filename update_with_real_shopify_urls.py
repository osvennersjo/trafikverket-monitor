#!/usr/bin/env python3

import pandas as pd
import random

def update_shopify_csv_with_real_urls():
    """Update the Shopify CSV with real Shopify URLs following user requirements"""
    
    # Read the latest CSV file
    print("📖 Reading shopify_products_corrected.csv...")
    df = pd.read_csv('shopify_products_corrected.csv')
    
    print(f"📊 Found {len(df)} total variants")
    
    # Real Shopify URLs provided by user
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
        "https://cdn.shopify.com/s/files/1/0947/3435/2707/files/unique_159.jpg",
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
    
    print(f"🖼️  Received {len(real_urls)} real Shopify URLs")
    
    # Group variants by product (using Handle as product identifier)
    products = {}
    for index, row in df.iterrows():
        handle = row['Handle']
        if handle not in products:
            products[handle] = []
        products[handle].append(index)
    
    print(f"📦 Found {len(products)} unique products")
    
    # Create a copy of URLs for distribution
    available_urls = real_urls.copy()
    random.shuffle(available_urls)  # Shuffle for variety
    
    # Track URL assignments
    url_assignments = {}
    used_urls = set()
    
    # First pass: Ensure each product gets at least one URL
    # Products with multiple variants get at least 2 URLs
    for handle, variant_indices in products.items():
        num_variants = len(variant_indices)
        
        if num_variants == 1:
            # Single variant - assign one URL
            if available_urls:
                url = available_urls.pop(0)
                url_assignments[variant_indices[0]] = url
                used_urls.add(url)
                print(f"   ✅ Product '{handle}' (1 variant): {url}")
        else:
            # Multiple variants - assign at least 2 URLs
            urls_to_assign = min(2, len(available_urls), num_variants)
            for i in range(urls_to_assign):
                if available_urls:
                    url = available_urls.pop(0)
                    url_assignments[variant_indices[i]] = url
                    used_urls.add(url)
            print(f"   ✅ Product '{handle}' ({num_variants} variants): assigned {urls_to_assign} URLs")
    
    # Second pass: Distribute remaining URLs to variants that don't have images yet
    unassigned_variants = []
    for handle, variant_indices in products.items():
        for idx in variant_indices:
            if idx not in url_assignments:
                unassigned_variants.append(idx)
    
    print(f"🔄 Distributing {len(available_urls)} remaining URLs to {len(unassigned_variants)} unassigned variants")
    
    # Distribute remaining URLs
    for variant_idx in unassigned_variants:
        if available_urls:
            url = available_urls.pop(0)
            url_assignments[variant_idx] = url
            used_urls.add(url)
    
    # Update the dataframe with new URLs
    df_updated = df.copy()
    df_updated['Variant Image'] = ''  # Add the "variant images" column
    
    for index, row in df_updated.iterrows():
        if index in url_assignments:
            # Update both Image Src and Variant Image columns
            df_updated.at[index, 'Image Src'] = url_assignments[index]
            df_updated.at[index, 'Variant Image'] = url_assignments[index]
        else:
            # Keep existing placeholder or set empty
            df_updated.at[index, 'Variant Image'] = ''
    
    # Save the updated CSV
    output_file = 'shopify_products_with_real_urls.csv'
    df_updated.to_csv(output_file, index=False)
    
    # Create summary
    print(f"\n✅ UPDATE COMPLETE!")
    print(f"=" * 50)
    print(f"📊 Total variants updated: {len(url_assignments)}")
    print(f"🔗 Unique URLs used: {len(used_urls)}")
    print(f"📁 Output file: {output_file}")
    print(f"📋 Added 'Variant Image' column for variant-specific images")
    
    # Verification
    unique_assigned_urls = set(url_assignments.values())
    print(f"\n🔍 VERIFICATION:")
    print(f"   • All URLs unique: {'✅ Yes' if len(unique_assigned_urls) == len(url_assignments) else '❌ No'}")
    print(f"   • No URL used twice: {'✅ Yes' if len(used_urls) == len(unique_assigned_urls) else '❌ No'}")
    
    # Product coverage stats
    products_with_images = 0
    products_with_multiple_images = 0
    
    for handle, variant_indices in products.items():
        variants_with_images = sum(1 for idx in variant_indices if idx in url_assignments)
        if variants_with_images > 0:
            products_with_images += 1
        if variants_with_images > 1:
            products_with_multiple_images += 1
    
    print(f"   • Products with images: {products_with_images}/{len(products)}")
    print(f"   • Products with multiple variant images: {products_with_multiple_images}")
    
    return output_file

if __name__ == "__main__":
    update_shopify_csv_with_real_urls() 