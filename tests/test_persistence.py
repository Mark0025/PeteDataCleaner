#!/usr/bin/env python3
"""
Test Persistence Manager
"""

import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.owner_object_analyzer import OwnerObjectAnalyzer
from backend.utils.ultra_fast_processor import load_csv_ultra_fast, clean_dataframe_ultra_fast
from backend.utils.owner_persistence_manager import save_property_owners_persistent, load_property_owners_persistent


def main():
    """Test the persistence manager."""
    
    print("🧪 TESTING PERSISTENCE MANAGER")
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
    
    print(f"✅ Created {len(owner_objects):,} Owner Objects")
    
    # Test saving
    print(f"💾 Testing persistence save...")
    save_paths = save_property_owners_persistent(owner_objects, df_enhanced, "test_dataset")
    print(f"✅ Save paths: {save_paths}")
    
    # Test loading
    print(f"📂 Testing persistence load...")
    loaded_objects, loaded_df = load_property_owners_persistent("test_dataset")
    print(f"✅ Loaded {len(loaded_objects):,} Owner Objects")
    print(f"✅ Loaded dataframe: {len(loaded_df):,} rows" if loaded_df is not None else "✅ No dataframe loaded")
    
    # Verify data integrity
    print(f"🔍 Verifying data integrity...")
    if len(owner_objects) == len(loaded_objects):
        print(f"✅ Owner Objects count matches: {len(owner_objects):,}")
    else:
        print(f"❌ Owner Objects count mismatch: {len(owner_objects):,} vs {len(loaded_objects):,}")
    
    if df_enhanced is not None and loaded_df is not None:
        if len(df_enhanced) == len(loaded_df):
            print(f"✅ Dataframe count matches: {len(df_enhanced):,}")
        else:
            print(f"❌ Dataframe count mismatch: {len(df_enhanced):,} vs {len(loaded_df):,}")
    
    print(f"\n🎉 PERSISTENCE TEST COMPLETE!")


if __name__ == "__main__":
    main() 