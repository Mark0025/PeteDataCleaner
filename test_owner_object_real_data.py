#!/usr/bin/env python3
"""
Test Owner Object Analyzer on Real Data

Analyzes the actual property data to see Owner Object patterns and skip trace opportunities.
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.owner_object_analyzer import OwnerObjectAnalyzer


def test_real_data_analysis():
    """Test the Owner Object Analyzer on real property data."""
    
    print("🏠 REAL DATA OWNER OBJECT ANALYSIS")
    print("=" * 80)
    
    # Load real data
    csv_path = Path("upload/All_RECORDS_12623 (1).csv")
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📁 Loading: {csv_path.name}")
    
    # Load sample for analysis (first 50k records for speed)
    df = pd.read_csv(csv_path, nrows=50000, low_memory=False)
    print(f"✅ Loaded: {len(df):,} records")
    
    # Initialize analyzer
    analyzer = OwnerObjectAnalyzer()
    
    # Run analysis
    print(f"\n🔍 Running Owner Object analysis...")
    owner_objects, df_enhanced = analyzer.analyze_dataset(df)
    
    # Show detailed examples
    print(f"\n📋 DETAILED OWNER OBJECT EXAMPLES:")
    print("-" * 80)
    
    # Show high confidence examples (individual + business)
    high_confidence = [obj for obj in owner_objects if obj.confidence_score >= 0.8]
    print(f"\n🎯 HIGH CONFIDENCE EXAMPLES (Skip Trace Success: 90%+):")
    print("-" * 60)
    
    for i, obj in enumerate(high_confidence[:5], 1):
        print(f"\nExample {i}:")
        print(f"  Individual: '{obj.individual_name}'")
        print(f"  Business: '{obj.business_name}'")
        print(f"  Mailing Address: '{obj.mailing_address}'")
        print(f"  Seller 1: '{obj.seller1_name}'")
        print(f"  Skip Trace Target: '{obj.skip_trace_target}'")
        print(f"  Confidence: {obj.confidence_score:.1f}")
        print(f"  Properties: {obj.property_count}")
        print(f"  Total Value: ${obj.total_property_value:,.0f}")
    
    # Show business-only examples
    business_only = [obj for obj in owner_objects if obj.is_business_owner and not obj.is_individual_owner]
    print(f"\n🏢 BUSINESS-ONLY EXAMPLES (Skip Trace Success: 40-70%):")
    print("-" * 60)
    
    for i, obj in enumerate(business_only[:3], 1):
        print(f"\nExample {i}:")
        print(f"  Business: '{obj.business_name}'")
        print(f"  Mailing Address: '{obj.mailing_address}'")
        print(f"  Seller 1: '{obj.seller1_name}'")
        print(f"  Skip Trace Target: '{obj.skip_trace_target}'")
        print(f"  Confidence: {obj.confidence_score:.1f}")
        print(f"  Properties: {obj.property_count}")
        print(f"  Total Value: ${obj.total_property_value:,.0f}")
    
    # Show multi-property examples
    multi_prop = [obj for obj in owner_objects if obj.property_count > 1]
    print(f"\n🏘️ MULTI-PROPERTY OWNERS (Serious Investors):")
    print("-" * 60)
    
    for i, obj in enumerate(multi_prop[:3], 1):
        print(f"\nExample {i}:")
        print(f"  Individual: '{obj.individual_name}'")
        print(f"  Business: '{obj.business_name}'")
        print(f"  Mailing Address: '{obj.mailing_address}'")
        print(f"  Seller 1: '{obj.seller1_name}'")
        print(f"  Skip Trace Target: '{obj.skip_trace_target}'")
        print(f"  Confidence: {obj.confidence_score:.1f}")
        print(f"  Properties: {obj.property_count}")
        print(f"  Total Value: ${obj.total_property_value:,.0f}")
    
    # Show enhanced dataframe sample
    print(f"\n📊 ENHANCED DATAFRAME SAMPLE:")
    print("-" * 60)
    
    sample_cols = ['Property address', 'Mailing address', 'First Name', 'Last Name', 
                   'Business Name', 'Seller_1', 'Skip_Trace_Target', 'Owner_Confidence', 
                   'Owner_Type', 'Property_Count']
    
    available_cols = [col for col in sample_cols if col in df_enhanced.columns]
    print(df_enhanced[available_cols].head(10).to_string())
    
    # Save enhanced data for inspection
    output_path = Path("data/processed/reports/owner_analysis_sample.csv")
    df_enhanced[available_cols].head(1000).to_csv(output_path, index=False)
    print(f"\n💾 Saved sample to: {output_path}")
    
    # Summary statistics
    print(f"\n📈 SKIP TRACE OPPORTUNITIES:")
    print("-" * 60)
    
    high_opp = len([obj for obj in owner_objects if obj.confidence_score >= 0.8])
    medium_opp = len([obj for obj in owner_objects if 0.5 <= obj.confidence_score < 0.8])
    low_opp = len([obj for obj in owner_objects if obj.confidence_score < 0.5])
    
    total_owners = len(owner_objects)
    
    print(f"High Success Rate (80%+): {high_opp:,} owners ({high_opp/total_owners*100:.1f}%)")
    print(f"Medium Success Rate (50-80%): {medium_opp:,} owners ({medium_opp/total_owners*100:.1f}%)")
    print(f"Low Success Rate (<50%): {low_opp:,} owners ({low_opp/total_owners*100:.1f}%)")
    
    # Value analysis
    high_value_owners = [obj for obj in owner_objects if obj.total_property_value > 1000000]
    print(f"\n💰 HIGH-VALUE OWNERS (>$1M): {len(high_value_owners):,}")
    
    if high_value_owners:
        avg_confidence = sum(obj.confidence_score for obj in high_value_owners) / len(high_value_owners)
        print(f"Average Skip Trace Confidence: {avg_confidence:.1f}")
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    test_real_data_analysis() 