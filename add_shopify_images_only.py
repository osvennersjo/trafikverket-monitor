#!/usr/bin/env python3

import pandas as pd
import random

def add_shopify_images_only():
    """Add Shopify image URLs to the existing CSV without making any other changes"""
    
    # Read the current CSV file with semicolon delimiter
    print("📖 Reading shopify_for_cursor.csv...")
    df = pd.read_csv('shopify_for_cursor.csv', delimiter=';')
    
    print(f"📊 Found {len(df)} rows (including variants)")
    
    # Real Shopify URLs (200 URLs provided earlier)
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
    
    print(f"🔗 Available Shopify URLs: {len(real_urls)}")
    
    # Simple assignment: add URLs sequentially to each row
    url_index = 0
    
    for index in range(len(df)):
        if url_index < len(real_urls):
            # Add the image URL to both Image Src and Variant Image columns
            df.at[index, 'Image Src'] = real_urls[url_index]
            df.at[index, 'Variant Image'] = real_urls[url_index]
            url_index += 1
        else:
            # If we run out of URLs, cycle back to the beginning
            url_index = 0
            df.at[index, 'Image Src'] = real_urls[url_index]
            df.at[index, 'Variant Image'] = real_urls[url_index]
            url_index += 1
    
    # Save the updated CSV with semicolon delimiter
    output_file = 'shopify_for_cursor_with_images.csv'
    df.to_csv(output_file, index=False, sep=';')
    
    print(f"\n✅ SHOPIFY IMAGES ADDED SUCCESSFULLY!")
    print(f"=" * 60)
    print(f"📄 Input file: shopify_for_cursor.csv")
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total variants: {len(df)}")
    print(f"🖼️  Unique URLs used: {min(len(real_urls), len(df))}")
    print(f"🔗 Image columns updated: Image Src, Variant Image")
    print(f"⚡ No other changes made to the data")
    
    # Verify the results
    non_empty_images = df[df['Image Src'].notna() & (df['Image Src'] != '')].shape[0]
    print(f"✅ Variants with images: {non_empty_images}/{len(df)}")
    
    return output_file

if __name__ == "__main__":
    add_shopify_images_only() 