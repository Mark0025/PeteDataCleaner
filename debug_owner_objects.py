#!/usr/bin/env python3
"""
Debug Owner Objects
"""

import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.owner_object_analyzer import OwnerObjectAnalyzer
from backend.utils.ultra_fast_processor import load_csv_ultra_fast, clean_dataframe_ultra_fast


def main():
    """Debug Owner Objects to see what's happening."""
    
    print("🔍 DEBUGGING OWNER OBJECTS")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = OwnerObjectAnalyzer()
    
    # Load a small sample of data
    csv_path = "upload/All_RECORDS_12623 (1).csv"
    print(f"📁 Loading small sample of data...")
    df = load_csv_ultra_fast(csv_path)
    df_sample = df.head(1000)  # Just 1000 rows for testing
    print(f"✅ Loaded: {len(df_sample):,} records")
    
    print(f"🧹 Cleaning .0 from phone numbers...")
    df_sample = clean_dataframe_ultra_fast(df_sample)
    print(f"✅ Phone cleanup complete")
    
    print(f"🏠 Analyzing Owner Objects...")
    owner_objects, df_enhanced = analyzer.analyze_dataset(df_sample)
    
    print(f"\n📊 OWNER OBJECTS ANALYSIS:")
    print(f"Total Owner Objects: {len(owner_objects):,}")
    
    # Check first few objects
    print(f"\n🔍 FIRST 5 OWNER OBJECTS:")
    for i, obj in enumerate(owner_objects[:5], 1):
        print(f"\nOwner {i}:")
        print(f"  Type: {type(obj)}")
        print(f"  Has individual_name: {hasattr(obj, 'individual_name')}")
        if hasattr(obj, 'individual_name'):
            print(f"  Individual name: '{obj.individual_name}'")
        print(f"  Has seller1_name: {hasattr(obj, 'seller1_name')}")
        if hasattr(obj, 'seller1_name'):
            print(f"  Seller 1 name: '{obj.seller1_name}'")
        print(f"  Has property_count: {hasattr(obj, 'property_count')}")
        if hasattr(obj, 'property_count'):
            print(f"  Property count: {obj.property_count}")
        print(f"  Has confidence_score: {hasattr(obj, 'confidence_score')}")
        if hasattr(obj, 'confidence_score'):
            print(f"  Confidence score: {obj.confidence_score}")
    
    # Check if any objects are strings
    string_objects = [obj for obj in owner_objects if isinstance(obj, str)]
    print(f"\n⚠️  String objects found: {len(string_objects)}")
    if string_objects:
        print(f"First few string objects: {string_objects[:3]}")
    
    # Check valid Owner Objects
    valid_objects = [obj for obj in owner_objects if hasattr(obj, 'individual_name')]
    print(f"\n✅ Valid Owner Objects: {len(valid_objects):,}")
    
    # Check what's missing
    invalid_objects = [obj for obj in owner_objects if not hasattr(obj, 'individual_name')]
    print(f"❌ Invalid objects: {len(invalid_objects):,}")
    
    if invalid_objects:
        print(f"Types of invalid objects: {set(type(obj) for obj in invalid_objects)}")
        print(f"Sample invalid objects: {invalid_objects[:3]}")


if __name__ == "__main__":
    main() 