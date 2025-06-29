#!/usr/bin/env python3

import pandas as pd
import numpy as np

def verify_grouping():
    # Read the CSV
    df = pd.read_csv('shopify_products_properly_grouped.csv')
    
    print("✅ HANDLE VERIFICATION:")
    handle_groups = df.groupby('Handle').size()
    print(f"   • Total unique products: {len(handle_groups)}")
    print(f"   • Products with 1 variant: {sum(handle_groups == 1)}")
    print(f"   • Products with 2+ variants: {sum(handle_groups > 1)}")
    print(f"   • Average variants per product: {handle_groups.mean():.1f}")
    print()
    
    print("📋 Sample Handle grouping:")
    sample_handles = ['nordica-enforcer-99', 'völkl-mantra-m7', 'atomic-bent-110-2425']
    
    for handle in sample_handles:
        variants = df[df['Handle'] == handle]
        if len(variants) > 0:
            print(f"  {handle}:")
            for idx, row in variants.iterrows():
                # Handle NaN/empty titles properly
                title = str(row['Title']) if pd.notna(row['Title']) and row['Title'] else '[VARIANT]'
                title_display = title[:25] + "..." if len(title) > 25 else title
                print(f"    - {row['Längd']} | Title: \"{title_display}\" | Qty: {row['Variant Inventory Qty']}")
            print()
    
    # Check that only first variant has product info
    print("🔍 PRODUCT INFO VERIFICATION:")
    print("Checking that only first variant of each product has Title/Body/etc...")
    
    for handle in df['Handle'].unique()[:5]:  # Check first 5 products
        variants = df[df['Handle'] == handle]
        first_variant = variants.iloc[0]
        other_variants = variants.iloc[1:]
        
        print(f"\n  Product: {handle}")
        has_title = pd.notna(first_variant['Title']) and str(first_variant['Title']).strip()
        print(f"    First variant has Title: {'Yes' if has_title else 'No'}")
        
        if len(other_variants) > 0:
            empty_titles = sum([1 for _, row in other_variants.iterrows() if pd.isna(row['Title']) or not str(row['Title']).strip()])
            print(f"    Other variants with empty Title: {empty_titles}/{len(other_variants)}")
        
    print("\n✅ VERIFICATION COMPLETE!")

if __name__ == "__main__":
    verify_grouping() 