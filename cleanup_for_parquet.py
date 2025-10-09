#!/usr/bin/env python3
"""
Cleanup Script - Remove Unnecessary Files for Parquet Workflow
Run this after backing up your project!
"""

import os
import sys

# Files to remove
FILES_TO_REMOVE = [
    'tian_v1_data.py',              # Large Python data file (replaced by Parquet)
    'generate_tian_v1.py',          # Single-threaded generator (use fast version)
    'create_tian_v1_deck.py',       # Old deck creator (use Parquet version)
    'PARQUET_COMPLETE.md',          # Extra documentation
    'PARQUET_IMPLEMENTATION.md',    # Extra documentation
    'example_parquet_usage.py',     # Demo/example file
    'example_data.py',              # Example data (not needed for v1 workflow)
    'demo.py',                      # Demo script
]

# Optional files (ask user)
OPTIONAL_FILES = [
    'validate_data.py',             # Only if you don't need validation
]

def get_file_size(filepath):
    """Get file size in KB"""
    try:
        return os.path.getsize(filepath) / 1024
    except Exception:
        return 0

def main():
    print("=" * 70)
    print("🧹 Cleanup Script for Parquet Workflow")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('parquet_utils.py'):
        print("\n❌ Error: Run this script from the Tian-hanzi-deck directory")
        sys.exit(1)
    
    print("\n📋 Files that will be removed:")
    print("-" * 70)
    
    total_size = 0
    existing_files = []
    
    for filename in FILES_TO_REMOVE:
        if os.path.exists(filename):
            size = get_file_size(filename)
            total_size += size
            existing_files.append(filename)
            print(f"  ✓ {filename:40} ({size:>8.1f} KB)")
        else:
            print(f"  ⊗ {filename:40} (not found)")
    
    print("-" * 70)
    print(f"  Total space to free: {total_size:.1f} KB ({total_size/1024:.2f} MB)")
    print()
    
    if not existing_files:
        print("✅ No files to remove - already cleaned up!")
        return
    
    # Confirmation
    response = input("⚠️  Are you sure you want to delete these files? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Cleanup cancelled")
        return
    
    # Remove files
    print("\n🗑️  Removing files...")
    removed_count = 0
    
    for filename in existing_files:
        try:
            os.remove(filename)
            print(f"  ✓ Removed: {filename}")
            removed_count += 1
        except Exception as e:
            print(f"  ❌ Failed to remove {filename}: {e}")
    
    print()
    print("=" * 70)
    print(f"✅ Cleanup complete! Removed {removed_count} files ({total_size:.1f} KB)")
    print("=" * 70)
    
    print("\n📂 Your streamlined workflow:")
    print("  1. generate_tian_v1_fast.py  → Generate data (multiprocessed)")
    print("  2. data/*.parquet            → Store data (efficient)")
    print("  3. create_deck_from_parquet.py → Create Anki deck (fast)")
    print("\n💡 Tip: Modify generate_tian_v1_fast.py to save directly to Parquet!")

if __name__ == '__main__':
    main()
