#!/usr/bin/env python3

import pandas as pd
import re
from collections import defaultdict

def create_base_sku(title, vendor):
    """Create a base SKU from product title and vendor"""
    # Clean up vendor name
    vendor_clean = str(vendor).upper().replace(' ', '').replace('-', '')[:3]
    if not vendor_clean or vendor_clean == 'NAN':
        vendor_clean = 'SKI'
    
    # Clean up title
    title_clean = str(title).upper()
    
    # Extract key product identifiers
    # Remove common words and numbers
    title_clean = re.sub(r'\b(24/25|25/26|2425|2526|2324)\b', '', title_clean)
    title_clean = re.sub(r'\b(CM|MM|INCH|TI|W|JR|JUNIOR|SHORT|LONG)\b', '', title_clean)
    title_clean = re.sub(r'\b\d{2,3}(?:CM|MM)?\b', '', title_clean)  # Remove lengths
    
    # Get meaningful words from title
    words = re.findall(r'[A-Z]+', title_clean)
    words = [w for w in words if len(w) >= 2]  # Only words with 2+ chars
    
    # Create base from vendor + key product words
    if len(words) >= 2:
        product_part = words[0][:3] + '_' + words[1][:3]
    elif len(words) == 1:
        product_part = words[0][:6]
    else:
        product_part = 'SKI_PRD'
    
    base_sku = f"{vendor_clean}_{product_part}"
    
    # Ensure it's valid (no double underscores, etc.)
    base_sku = re.sub(r'_+', '_', base_sku)
    base_sku = base_sku.strip('_')
    
    return base_sku

def generate_unique_skus():
    """Generate unique SKUs for all variants in the CSV"""
    
    # Read the CSV
    print("📖 Reading CSV file...")
    df = pd.read_csv('shopify_for_cursor_with_images.csv', delimiter=';')
    
    print(f"📊 Found {len(df)} rows")
    
    # Group products by Handle to understand variants
    product_groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        handle = row['Handle']
        title = row['Title']
        vendor = row['Vendor']
        length = row['Option1 Value']  # This is the "längd" value
        
        # Create or get product info
        if handle not in product_groups:
            product_groups[handle] = {
                'title': title if pd.notna(title) and title.strip() else f"Product {handle}",
                'vendor': vendor if pd.notna(vendor) and vendor.strip() else 'unknown',
                'variants': []
            }
        
        product_groups[handle]['variants'].append({
            'index': idx,
            'length': length if pd.notna(length) else '000'
        })
    
    print(f"🎯 Found {len(product_groups)} unique products")
    
    # Generate base SKUs for each product
    base_skus = {}
    used_bases = set()
    
    for handle, product_info in product_groups.items():
        base_sku = create_base_sku(product_info['title'], product_info['vendor'])
        
        # Ensure uniqueness
        original_base = base_sku
        counter = 1
        while base_sku in used_bases:
            base_sku = f"{original_base}_{counter}"
            counter += 1
        
        used_bases.add(base_sku)
        base_skus[handle] = base_sku
    
    # Generate full SKUs for each variant
    all_skus = []
    
    for handle, product_info in product_groups.items():
        base_sku = base_skus[handle]
        variants = product_info['variants']
        
        # Sort variants by length for consistent numbering
        variants.sort(key=lambda x: str(x['length']))
        
        for i, variant in enumerate(variants, 1):
            # Create 3-digit number for this variant
            variant_num = f"{i:03d}"
            full_sku = f"{base_sku}_{variant_num}"
            
            all_skus.append({
                'index': variant['index'],
                'sku': full_sku,
                'base': base_sku,
                'variant_num': variant_num,
                'length': variant['length']
            })
    
    # Add SKUs to the dataframe
    df['SKU'] = ''
    
    for sku_info in all_skus:
        df.at[sku_info['index'], 'SKU'] = sku_info['sku']
    
    # Save the updated CSV
    output_file = 'shopify_for_cursor_with_skus.csv'
    df.to_csv(output_file, index=False, sep=';')
    
    print(f"\n✅ SKU GENERATION COMPLETED!")
    print(f"=" * 60)
    print(f"📄 Input file: shopify_for_cursor_with_images.csv")
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total SKUs generated: {len(all_skus)}")
    print(f"🏷️  Unique product bases: {len(base_skus)}")
    
    # Show some examples
    print(f"\n📋 Example SKUs:")
    for i, sku_info in enumerate(all_skus[:10]):
        print(f"   {sku_info['sku']} (Length: {sku_info['length']})")
    if len(all_skus) > 10:
        print(f"   ... and {len(all_skus) - 10} more")
    
    # Verify uniqueness
    all_sku_values = [sku_info['sku'] for sku_info in all_skus]
    unique_skus = set(all_sku_values)
    
    print(f"\n🔍 Verification:")
    print(f"   • Total SKUs: {len(all_sku_values)}")
    print(f"   • Unique SKUs: {len(unique_skus)}")
    print(f"   • All unique: {'✅ YES' if len(all_sku_values) == len(unique_skus) else '❌ NO'}")
    
    # Show product grouping examples
    print(f"\n🎯 Product Grouping Examples:")
    sample_handles = list(product_groups.keys())[:3]
    for handle in sample_handles:
        base = base_skus[handle]
        variants = [sku['sku'] for sku in all_skus if sku['sku'].startswith(base)]
        print(f"   {handle}: {base}")
        for variant in variants[:3]:  # Show first 3 variants
            print(f"     - {variant}")
        if len(variants) > 3:
            print(f"     ... and {len(variants) - 3} more variants")
    
    return output_file

if __name__ == "__main__":
    generate_unique_skus() 