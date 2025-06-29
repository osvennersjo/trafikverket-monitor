#!/usr/bin/env python3

import pandas as pd

def extract_skus_for_excel():
    """Extract SKUs from CSV in exact order for Excel paste"""
    
    # Read the CSV file
    print("📖 Reading shopify_for_cursor_with_skus.csv...")
    df = pd.read_csv('shopify_for_cursor_with_skus.csv', delimiter=';')
    
    print(f"📊 Found {len(df)} rows")
    
    # Extract just the SKU column
    skus = df['SKU'].tolist()
    
    # Write SKUs to a text file for easy copy-paste
    with open('skus_for_excel.txt', 'w') as f:
        for sku in skus:
            f.write(f"{sku}\n")
    
    # Also create a tab-separated version (for pasting into multiple columns)
    with open('skus_for_excel_tabs.txt', 'w') as f:
        f.write('\t'.join(skus))
    
    # Create a CSV with just SKUs for direct Excel import
    sku_df = pd.DataFrame({'SKU': skus})
    sku_df.to_csv('skus_only.csv', index=False)
    
    print(f"\n✅ SKU EXTRACTION COMPLETED!")
    print(f"=" * 60)
    print(f"📄 Files created:")
    print(f"   • skus_for_excel.txt      - One SKU per line (for vertical paste)")
    print(f"   • skus_for_excel_tabs.txt - Tab-separated (for horizontal paste)")
    print(f"   • skus_only.csv           - CSV file with just SKUs")
    print(f"📊 Total SKUs: {len(skus)}")
    
    # Show first 10 SKUs as preview
    print(f"\n📋 First 10 SKUs:")
    for i, sku in enumerate(skus[:10], 1):
        print(f"   {i:3d}. {sku}")
    
    if len(skus) > 10:
        print(f"   ... and {len(skus) - 10} more")
    
    print(f"\n📋 Instructions for Excel:")
    print(f"   1. Open skus_for_excel.txt in a text editor")
    print(f"   2. Select all (Ctrl+A) and copy (Ctrl+C)")
    print(f"   3. In Excel, select the first cell where you want SKUs")
    print(f"   4. Paste (Ctrl+V) - SKUs will fill down one per row")
    print(f"   ")
    print(f"   Alternative: Open skus_only.csv directly in Excel")
    
    return len(skus)

if __name__ == "__main__":
    extract_skus_for_excel() 