#!/usr/bin/env python3
"""
Test Smart Seller Creator functionality
"""

import pandas as pd
from backend.utils.smart_seller_creator import SmartSellerCreator, create_seller_groups

def test_smart_seller_creator():
    """Test the smart seller creator with sample data."""
    
    print("🧪 TESTING SMART SELLER CREATOR:")
    print("="*60)
    
    # Load sample data
    df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=100)
    print(f"📊 Loaded {len(df):,} records for testing")
    
    # Create test scenarios
    print("\n🔍 CREATING TEST SCENARIOS:")
    print("="*60)
    
    # Scenario 1: Full duplicates (same address + seller + phones)
    print("\n1️⃣ FULL DUPLICATES SCENARIO:")
    test_df1 = df.head(3).copy()
    # Duplicate the first row
    duplicate_row = test_df1.iloc[0].copy()
    test_df1 = pd.concat([test_df1, pd.DataFrame([duplicate_row])], ignore_index=True)
    print(f"   Created {len(test_df1)} records with 1 full duplicate")
    
    # Scenario 2: Address duplicates (same address + different sellers)
    print("\n2️⃣ ADDRESS DUPLICATES SCENARIO:")
    test_df2 = df.head(5).copy()
    # Change the address of the last 2 rows to match the first
    test_df2.loc[3, 'Property address'] = test_df2.loc[0, 'Property address']
    test_df2.loc[4, 'Property address'] = test_df2.loc[0, 'Property address']
    print(f"   Created {len(test_df2)} records with 3 sellers at same address")
    
    # Test the smart seller creator
    print("\n🔄 TESTING SMART SELLER CREATOR:")
    print("="*60)
    
    creator = SmartSellerCreator()
    
    # Test Scenario 1
    print("\n📋 TESTING SCENARIO 1 (Full Duplicates):")
    result1 = creator.create_seller_groups(test_df1)
    stats1 = creator.get_stats()
    print(f"   Input: {len(test_df1)} records")
    print(f"   Output: {len(result1)} records")
    print(f"   Full duplicates removed: {stats1['full_duplicates_removed']}")
    print(f"   Seller groups created: {stats1['seller_groups_created']}")
    
    # Test Scenario 2
    print("\n📋 TESTING SCENARIO 2 (Address Duplicates):")
    creator2 = SmartSellerCreator()  # Reset stats
    result2 = creator2.create_seller_groups(test_df2)
    stats2 = creator2.get_stats()
    print(f"   Input: {len(test_df2)} records")
    print(f"   Output: {len(result2)} records")
    print(f"   Full duplicates removed: {stats2['full_duplicates_removed']}")
    print(f"   Seller groups created: {stats2['seller_groups_created']}")
    print(f"   Properties with multiple sellers: {stats2['properties_with_multiple_sellers']}")
    
    # Show sample output
    if len(result2) > 0:
        print("\n📊 SAMPLE OUTPUT (Address Duplicates):")
        print("="*60)
        sample_cols = ['Property address', 'Seller 1', 'Seller 1 Phone', 'Seller 1 Email', 'Phone 1', 'Phone 2']
        available_cols = [col for col in sample_cols if col in result2.columns]
        print(result2[available_cols].head(2).to_string())
    
    # Test convenience function
    print("\n🧪 TESTING CONVENIENCE FUNCTION:")
    print("="*60)
    result3 = create_seller_groups(test_df2)
    print(f"   Convenience function result: {len(result3)} records")
    
    print("\n✅ TESTING COMPLETE!")

if __name__ == "__main__":
    test_smart_seller_creator() 