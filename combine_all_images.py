#!/usr/bin/env python3

import os
import shutil
import hashlib
import pandas as pd
from collections import defaultdict

def get_image_hash(filepath):
    """Generate hash for image file to detect duplicates"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def combine_unique_images():
    """Combine all unique images from different directories"""
    
    source_dirs = [
        "alpingaraget_550_images",
        "alpingaraget_enhanced_images", 
        "alpingaraget_images"
    ]
    
    output_dir = "alpingaraget_final_unique_collection"
    
    # Create output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    print("🔄 Combining all unique images...")
    print("=" * 50)
    
    seen_hashes = set()
    copied_count = 0
    skipped_duplicates = 0
    report_data = []
    
    # Process each source directory
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            print(f"⚠️  Directory {source_dir} not found, skipping...")
            continue
            
        print(f"\n📁 Processing: {source_dir}")
        dir_files = []
        
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                dir_files.append(filename)
        
        print(f"   📊 Found {len(dir_files)} image files")
        
        for filename in dir_files:
            source_path = os.path.join(source_dir, filename)
            
            # Get image hash
            image_hash = get_image_hash(source_path)
            if not image_hash:
                continue
                
            # Skip duplicates
            if image_hash in seen_hashes:
                skipped_duplicates += 1
                continue
            
            # Copy unique image
            seen_hashes.add(image_hash)
            copied_count += 1
            
            # Create new filename with sequential numbering
            file_ext = os.path.splitext(filename)[1]
            new_filename = f"unique_{copied_count:03d}{file_ext}"
            dest_path = os.path.join(output_dir, new_filename)
            
            shutil.copy2(source_path, dest_path)
            
            # Add to report
            file_size = os.path.getsize(dest_path)
            report_data.append({
                'filename': new_filename,
                'original_source': source_dir,
                'original_filename': filename,
                'size_kb': round(file_size / 1024, 2),
                'format': file_ext[1:].upper()
            })
            
            if copied_count % 50 == 0:
                print(f"   ✅ Copied {copied_count} unique images...")
    
    # Create summary report
    df = pd.DataFrame(report_data)
    report_file = 'alpingaraget_final_collection_report.csv'
    df.to_csv(report_file, index=False)
    
    # Print final summary
    print(f"\n✅ FINAL COLLECTION COMPLETE!")
    print("=" * 50)
    print(f"📊 Total unique images: {copied_count}")
    print(f"🚫 Duplicates skipped: {skipped_duplicates}")
    print(f"📁 Output directory: {output_dir}/")
    print(f"📋 Report saved: {report_file}")
    
    # Format breakdown
    format_counts = df['format'].value_counts()
    print(f"\n📈 Format distribution:")
    for fmt, count in format_counts.items():
        print(f"   {fmt}: {count} images")
    
    # Size statistics
    total_size_mb = df['size_kb'].sum() / 1024
    avg_size_kb = df['size_kb'].mean()
    print(f"\n💾 Size statistics:")
    print(f"   Total size: {total_size_mb:.1f} MB")
    print(f"   Average size: {avg_size_kb:.1f} KB")
    
    # Achievement status
    target = 550
    if copied_count >= target:
        print(f"\n🎉 TARGET ACHIEVED! Got {copied_count} images (target: {target})")
    else:
        remaining = target - copied_count
        print(f"\n📈 Progress: {copied_count}/{target} images ({(copied_count/target)*100:.1f}%)")
        print(f"   Still need: {remaining} more images")
    
    return copied_count

if __name__ == "__main__":
    total_images = combine_unique_images() 