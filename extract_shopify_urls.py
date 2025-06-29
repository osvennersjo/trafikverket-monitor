#!/usr/bin/env python3

import pandas as pd
import os

def create_url_mapping_template():
    """Create a template for mapping real Shopify URLs to products"""
    
    # Read the existing CSV to get product information
    print("📖 Reading existing product data...")
    df = pd.read_csv('shopify_products_corrected.csv')
    
    print(f"📊 Found {len(df)} product variants")
    
    # Get unique product information for mapping
    mapping_data = []
    for index, row in df.iterrows():
        mapping_data.append({
            'Variant_Number': index + 1,
            'Product_Title': row['Title'],
            'Handle': row['Handle'],
            'SKU': row['Variant SKU'],
            'Current_Image_URL': row['Image Src'],
            'Real_Shopify_URL': '',  # This will be filled in manually
            'Image_Filename': f"product_{index+1:03d}.jpg",  # Expected filename
            'Notes': ''
        })
    
    # Create mapping CSV
    mapping_df = pd.DataFrame(mapping_data)
    mapping_file = 'shopify_url_mapping.csv'
    mapping_df.to_csv(mapping_file, index=False)
    
    print(f"\n✅ Created mapping template: {mapping_file}")
    print(f"📋 This file contains {len(mapping_data)} rows to fill with real URLs")
    
    return mapping_file

def apply_real_urls():
    """Apply real URLs from the completed mapping file to create final CSV"""
    
    mapping_file = 'shopify_url_mapping.csv'
    
    if not os.path.exists(mapping_file):
        print(f"❌ Mapping file {mapping_file} not found!")
        print("Please run create_url_mapping_template() first")
        return
    
    # Read the mapping file
    print(f"📖 Reading URL mapping from {mapping_file}...")
    mapping_df = pd.read_csv(mapping_file)
    
    # Check how many URLs have been filled in
    filled_urls = mapping_df[mapping_df['Real_Shopify_URL'].str.strip() != '']
    print(f"📊 Found {len(filled_urls)} filled URLs out of {len(mapping_df)} total")
    
    if len(filled_urls) == 0:
        print("❌ No real URLs found in mapping file!")
        print("Please fill in the 'Real_Shopify_URL' column with actual Shopify CDN URLs")
        return
    
    # Read the original CSV
    df = pd.read_csv('shopify_products_corrected.csv')
    
    # Apply the real URLs
    updated_count = 0
    for index, row in mapping_df.iterrows():
        real_url = str(row['Real_Shopify_URL']).strip()
        if real_url and real_url != 'nan' and real_url != '':
            # Update the corresponding row in the main CSV
            df.at[index, 'Image Src'] = real_url
            updated_count += 1
    
    # Save the final CSV
    final_file = 'shopify_products_with_real_urls.csv'
    df.to_csv(final_file, index=False)
    
    print(f"\n✅ Updated {updated_count} image URLs with real Shopify CDN URLs")
    print(f"📁 Final file saved as: {final_file}")
    print(f"🚀 Ready for Shopify import!")
    
    return final_file

def main():
    """Main function with menu options"""
    print("🛠️  Shopify URL Extraction Helper")
    print("=" * 40)
    print("1. Create URL mapping template")
    print("2. Apply real URLs to create final CSV")
    print()
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == '1':
        create_url_mapping_template()
        print("\n📋 Next steps:")
        print("1. Open shopify_url_mapping.csv")
        print("2. Fill in the 'Real_Shopify_URL' column with actual URLs from Shopify")
        print("3. Run this script again with option 2")
        
    elif choice == '2':
        apply_real_urls()
        
    else:
        print("❌ Invalid choice. Please run again and choose 1 or 2.")

if __name__ == "__main__":
    main() 