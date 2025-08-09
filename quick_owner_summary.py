#!/usr/bin/env python3
"""
Quick Owner Summary with Persistent Storage

Shows the key results from Owner Object analysis and saves data persistently.
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
    """Quick summary of Owner Object analysis with persistent storage."""
    
    print("🏠 QUICK OWNER OBJECT SUMMARY WITH PERSISTENT STORAGE")
    print("=" * 70)
    
    # Check if we have saved data
    try:
        print("🔍 Checking for saved Property Owners data...")
        owner_objects, enhanced_df = load_property_owners_persistent()
        print(f"✅ Found saved data: {len(owner_objects):,} Owner Objects")
        print(f"📊 Enhanced dataframe: {len(enhanced_df):,} rows" if enhanced_df is not None else "📊 No enhanced dataframe found")
        
        # Show saved data summary
        show_owner_summary(owner_objects, enhanced_df)
        
        # Ask if user wants to re-analyze
        print(f"\n🔄 Do you want to re-analyze the data? (y/n): ", end="")
        response = input().lower().strip()
        
        if response != 'y':
            print("✅ Using saved data. No re-analysis needed.")
            return
            
    except FileNotFoundError:
        print("📁 No saved data found. Will analyze from scratch.")
    
    # Initialize analyzer
    analyzer = OwnerObjectAnalyzer()
    
    # Load data with ultra-fast processor
    csv_path = "upload/All_RECORDS_12623 (1).csv"
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📁 Loading data with ultra-fast processor...")
    df = load_csv_ultra_fast(csv_path)
    print(f"✅ Loaded: {len(df):,} records")
    
    print(f"🧹 Cleaning .0 from phone numbers...")
    df = clean_dataframe_ultra_fast(df)
    print(f"✅ Phone cleanup complete")
    
    print(f"🏠 Analyzing Owner Objects...")
    owner_objects, df_enhanced = analyzer.analyze_dataset(df)
    
    # Save data persistently
    print(f"💾 Saving data persistently...")
    save_paths = save_property_owners_persistent(owner_objects, df_enhanced)
    print(f"✅ Owner Objects saved: {save_paths['owner_objects_path']}")
    if save_paths['enhanced_data_path']:
        print(f"✅ Enhanced data saved: {save_paths['enhanced_data_path']}")
    
    # Show results
    show_owner_summary(owner_objects, df_enhanced)
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"🚀 All processing done with ultra-fast Polars/PyArrow")
    print(f"📞 Phone numbers cleaned of .0 automatically")
    print(f"💾 Data saved persistently - will be available next time you start")
    print(f"🎯 {len([obj for obj in owner_objects if hasattr(obj, 'confidence_score') and obj.confidence_score >= 0.8]):,} high-confidence skip trace targets ready for Pete!")


def show_owner_summary(owner_objects, enhanced_df=None):
    """Show summary of Owner Objects analysis."""
    
    print(f"\n📊 OWNER OBJECT ANALYSIS RESULTS:")
    print("-" * 50)
    print(f"Total Owner Objects: {len(owner_objects):,}")
    
    # Count by confidence
    high_conf = len([obj for obj in owner_objects if hasattr(obj, 'confidence_score') and obj.confidence_score >= 0.8])
    medium_conf = len([obj for obj in owner_objects if hasattr(obj, 'confidence_score') and 0.5 <= obj.confidence_score < 0.8])
    low_conf = len([obj for obj in owner_objects if hasattr(obj, 'confidence_score') and obj.confidence_score < 0.5])
    
    print(f"High Confidence (80%+): {high_conf:,} ({high_conf/len(owner_objects)*100:.1f}%)")
    print(f"Medium Confidence (50-80%): {medium_conf:,} ({medium_conf/len(owner_objects)*100:.1f}%)")
    print(f"Low Confidence (<50%): {low_conf:,} ({low_conf/len(owner_objects)*100:.1f}%)")
    
    # Count by owner type
    individual_only = len([obj for obj in owner_objects if hasattr(obj, 'is_individual_owner') and hasattr(obj, 'is_business_owner') and obj.is_individual_owner and not obj.is_business_owner])
    business_only = len([obj for obj in owner_objects if hasattr(obj, 'is_business_owner') and hasattr(obj, 'is_individual_owner') and obj.is_business_owner and not obj.is_individual_owner])
    both_types = len([obj for obj in owner_objects if hasattr(obj, 'is_individual_owner') and hasattr(obj, 'is_business_owner') and obj.is_individual_owner and obj.is_business_owner])
    
    print(f"\n👥 OWNER TYPE BREAKDOWN:")
    print(f"Individual Only: {individual_only:,} ({individual_only/len(owner_objects)*100:.1f}%)")
    print(f"Business Only: {business_only:,} ({business_only/len(owner_objects)*100:.1f}%)")
    print(f"Individual + Business: {both_types:,} ({both_types/len(owner_objects)*100:.1f}%)")
    
    # Show sample Owner Objects
    print(f"\n🎯 SAMPLE OWNER OBJECTS:")
    print("-" * 50)
    
    for i, obj in enumerate(owner_objects[:5], 1):
        if hasattr(obj, 'seller1_name'):
            print(f"Owner {i}:")
            print(f"  Seller 1: '{obj.seller1_name}'")
            if hasattr(obj, 'skip_trace_target'):
                print(f"  Skip Trace: '{obj.skip_trace_target}'")
            if hasattr(obj, 'confidence_score'):
                print(f"  Confidence: {obj.confidence_score:.1f}")
            if hasattr(obj, 'property_count'):
                print(f"  Properties: {obj.property_count}")
            if hasattr(obj, 'total_property_value'):
                print(f"  Total Value: ${obj.total_property_value:,.0f}")
            print()
    
    # Show enhanced dataframe info
    if enhanced_df is not None:
        new_cols = [col for col in enhanced_df.columns if col in [
            'Seller_1', 'Skip_Trace_Target', 'Owner_Confidence', 
            'Owner_Type', 'Property_Count'
        ]]
        print(f"📋 Owner Object columns in enhanced data: {new_cols}")


if __name__ == "__main__":
    main() 