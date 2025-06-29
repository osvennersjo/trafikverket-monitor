#!/usr/bin/env python3

import pandas as pd

def verify_skus():
    # Read the CSV
    df = pd.read_csv('shopify_for_cursor_with_skus.csv', delimiter=';')
    
    print("First 10 rows with SKUs:")
    print(df[['Handle', 'Title', 'Option1 Value', 'SKU']].head(10).to_string(index=False))
    
    print("\nSample of different product types:")
    handles = df['Handle'].unique()[:5]
    
    for h in handles:
        variants = df[df['Handle'] == h]
        print(f"\n{h}:")
        for _, row in variants.iterrows():
            title = row['Title'] if pd.notna(row['Title']) else '[VARIANT]'
            print(f"  {row['SKU']} (Length: {row['Option1 Value']}) - {title[:30]}...")
    
    # Check uniqueness
    all_skus = df['SKU'].tolist()
    unique_skus = set(all_skus)
    
    print(f"\nVerification Summary:")
    print(f"Total SKUs: {len(all_skus)}")
    print(f"Unique SKUs: {len(unique_skus)}")
    print(f"All unique: {'✅ YES' if len(all_skus) == len(unique_skus) else '❌ NO'}")
    
    # Show some vendor diversity
    print(f"\nVendor diversity in SKUs:")
    vendors = df['Vendor'].unique()[:10]
    for vendor in vendors:
        if pd.notna(vendor):
            vendor_skus = df[df['Vendor'] == vendor]['SKU'].head(2).tolist()
            print(f"  {vendor}: {vendor_skus}")

if __name__ == "__main__":
    verify_skus() 