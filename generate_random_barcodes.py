#!/usr/bin/env python3

import random

def generate_random_barcodes():
    """Generate 539 random 12-digit barcodes for Excel paste"""
    
    print("📊 Generating 539 random 12-digit barcodes...")
    
    # Generate 539 unique random 12-digit barcodes
    barcodes = []
    used_barcodes = set()
    
    while len(barcodes) < 539:
        # Generate a random 12-digit number
        # First digit can't be 0 for a proper 12-digit number
        first_digit = random.randint(1, 9)
        remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        barcode = str(first_digit) + remaining_digits
        
        # Ensure uniqueness
        if barcode not in used_barcodes:
            used_barcodes.add(barcode)
            barcodes.append(barcode)
    
    print(f"✅ Generated {len(barcodes)} unique 12-digit barcodes")
    
    # Write barcodes to a text file for easy copy-paste
    with open('barcodes_for_excel.txt', 'w') as f:
        for barcode in barcodes:
            f.write(f"{barcode}\n")
    
    # Also create a tab-separated version (for pasting into multiple columns)
    with open('barcodes_for_excel_tabs.txt', 'w') as f:
        f.write('\t'.join(barcodes))
    
    # Create a CSV with just barcodes for direct Excel import
    import pandas as pd
    barcode_df = pd.DataFrame({'Barcode': barcodes})
    barcode_df.to_csv('barcodes_only.csv', index=False)
    
    print(f"\n✅ BARCODE GENERATION COMPLETED!")
    print(f"=" * 60)
    print(f"📄 Files created:")
    print(f"   • barcodes_for_excel.txt      - One barcode per line (for vertical paste)")
    print(f"   • barcodes_for_excel_tabs.txt - Tab-separated (for horizontal paste)")
    print(f"   • barcodes_only.csv           - CSV file with just barcodes")
    print(f"📊 Total barcodes: {len(barcodes)}")
    
    # Show first 10 barcodes as preview
    print(f"\n📋 First 10 barcodes:")
    for i, barcode in enumerate(barcodes[:10], 1):
        print(f"   {i:3d}. {barcode}")
    
    if len(barcodes) > 10:
        print(f"   ... and {len(barcodes) - 10} more")
    
    # Verify all are 12 digits
    all_12_digits = all(len(barcode) == 12 and barcode.isdigit() for barcode in barcodes)
    print(f"\n🔍 Verification:")
    print(f"   • All barcodes are 12 digits: {'✅ YES' if all_12_digits else '❌ NO'}")
    print(f"   • All barcodes are unique: {'✅ YES' if len(barcodes) == len(set(barcodes)) else '❌ NO'}")
    
    print(f"\n📋 Instructions for Excel:")
    print(f"   1. Open barcodes_for_excel.txt in a text editor")
    print(f"   2. Select all (Ctrl+A) and copy (Ctrl+C)")
    print(f"   3. In Excel, select the first cell where you want barcodes")
    print(f"   4. Paste (Ctrl+V) - Barcodes will fill down one per row")
    print(f"   ")
    print(f"   Alternative: Open barcodes_only.csv directly in Excel")
    
    return len(barcodes)

if __name__ == "__main__":
    generate_random_barcodes() 