#!/usr/bin/env python3
"""
Property Ownership Pattern Analysis

Analyzes the data to understand property ownership patterns and create smart mapping
for Seller 1 (Pete) based on mailing addresses and owner information.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_property_ownership_patterns():
    """Analyze property ownership patterns in the data."""
    
    print("🏠 PROPERTY OWNERSHIP PATTERN ANALYSIS")
    print("=" * 80)
    
    # Load data
    csv_path = Path("upload/All_RECORDS_12623 (1).csv")
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📁 Loading: {csv_path.name}")
    df = pd.read_csv(csv_path, nrows=10000)  # Sample for analysis
    print(f"✅ Loaded: {len(df):,} records")
    
    # Check available columns
    print(f"\n📋 AVAILABLE COLUMNS:")
    print("-" * 40)
    owner_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['name', 'owner', 'business', 'mailing'])]
    for col in owner_cols:
        print(f"   {col}")
    
    # Analyze mailing address patterns
    print(f"\n📈 MAILING ADDRESS ANALYSIS:")
    print("-" * 40)
    
    if 'Mailing address' in df.columns:
        addr_counts = df['Mailing address'].value_counts()
        print(f"Unique mailing addresses: {len(addr_counts):,}")
        print(f"Addresses with >1 property: {len(addr_counts[addr_counts > 1]):,}")
        print(f"Max properties per address: {addr_counts.max()}")
        print(f"Avg properties per address: {addr_counts.mean():.1f}")
        
        # Show top addresses with multiple properties
        print(f"\n🏆 TOP 10 ADDRESSES WITH MULTIPLE PROPERTIES:")
        print("-" * 50)
        multi_prop_addresses = addr_counts[addr_counts > 1].head(10)
        for addr, count in multi_prop_addresses.items():
            print(f"   {addr}: {count} properties")
    
    # Analyze owner name patterns
    print(f"\n👤 OWNER NAME ANALYSIS:")
    print("-" * 40)
    
    # Create owner identifier
    if 'First Name' in df.columns and 'Last Name' in df.columns:
        df['owner_name'] = (df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')).str.strip()
        print(f"Individual owners: {len(df[df['owner_name'] != '']):,}")
        
        # Check for business indicators
        business_indicators = ['llc', 'inc', 'corp', 'company', 'holdings', 'properties', 'realty', 'management']
        business_owners = []
        
        for name in df['owner_name'].unique():
            if pd.notna(name) and name != '':
                name_lower = name.lower()
                if any(indicator in name_lower for indicator in business_indicators):
                    business_owners.append(name)
        
        print(f"Business entities detected: {len(business_owners):,}")
        print(f"Sample business owners: {business_owners[:5]}")
    
    # Analyze property ownership by mailing address
    print(f"\n🏠 PROPERTY OWNERSHIP BY MAILING ADDRESS:")
    print("-" * 50)
    
    if 'Mailing address' in df.columns and 'owner_name' in df.columns:
        # Group by mailing address and analyze owners
        addr_owner_groups = df.groupby('Mailing address')['owner_name'].apply(list)
        
        # Find addresses with multiple owners
        multi_owner_addresses = {}
        for addr, owners in addr_owner_groups.items():
            unique_owners = list(set([o for o in owners if pd.notna(o) and o != '']))
            if len(unique_owners) > 1:
                multi_owner_addresses[addr] = unique_owners
        
        print(f"Addresses with multiple owners: {len(multi_owner_addresses):,}")
        
        # Show examples
        print(f"\n📋 EXAMPLES OF MULTI-OWNER ADDRESSES:")
        print("-" * 50)
        for i, (addr, owners) in enumerate(list(multi_owner_addresses.items())[:5]):
            print(f"   Address {i+1}: {addr}")
            print(f"   Owners: {', '.join(owners)}")
            print()
    
    # Create smart Seller 1 mapping examples
    print(f"\n🎯 SMART SELLER 1 MAPPING EXAMPLES:")
    print("-" * 50)
    
    if 'Mailing address' in df.columns and 'owner_name' in df.columns:
        # Sample some addresses with multiple properties
        sample_addresses = addr_counts[addr_counts > 1].head(5)
        
        for addr, prop_count in sample_addresses.items():
            addr_data = df[df['Mailing address'] == addr]
            owners = addr_data['owner_name'].unique()
            owners = [o for o in owners if pd.notna(o) and o != '']
            
            # Create smart Seller 1 name
            if len(owners) == 1:
                seller1 = owners[0]
            else:
                # Multiple owners - combine them
                seller1 = " | ".join(owners)
            
            print(f"   Mailing Address: {addr}")
            print(f"   Properties: {prop_count}")
            print(f"   Owners: {owners}")
            print(f"   → Seller 1: {seller1}")
            print()
    
    # Business vs Individual analysis
    print(f"\n🏢 BUSINESS vs INDIVIDUAL OWNERSHIP:")
    print("-" * 40)
    
    if 'owner_name' in df.columns:
        business_count = 0
        individual_count = 0
        
        for name in df['owner_name'].unique():
            if pd.notna(name) and name != '':
                name_lower = name.lower()
                if any(indicator in name_lower for indicator in business_indicators):
                    business_count += 1
                else:
                    individual_count += 1
        
        total_owners = business_count + individual_count
        print(f"Business entities: {business_count:,} ({business_count/total_owners*100:.1f}%)")
        print(f"Individual owners: {individual_count:,} ({individual_count/total_owners*100:.1f}%)")
        print(f"Total unique owners: {total_owners:,}")
    
    # Property value analysis by owner type
    print(f"\n💰 PROPERTY VALUE ANALYSIS:")
    print("-" * 40)
    
    if 'Estimated value' in df.columns and 'owner_name' in df.columns:
        # Convert to numeric
        df['value_numeric'] = pd.to_numeric(df['Estimated value'], errors='coerce')
        
        # Group by owner and calculate stats
        owner_values = df.groupby('owner_name')['value_numeric'].agg(['sum', 'mean', 'count']).reset_index()
        owner_values.columns = ['owner_name', 'total_value', 'avg_value', 'property_count']
        
        print(f"Total property value: ${owner_values['total_value'].sum():,.0f}")
        print(f"Average property value: ${owner_values['avg_value'].mean():,.0f}")
        print(f"Top 5 owners by total value:")
        
        top_owners = owner_values.nlargest(5, 'total_value')
        for _, row in top_owners.iterrows():
            print(f"   {row['owner_name']}: ${row['total_value']:,.0f} ({row['property_count']} properties)")
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    analyze_property_ownership_patterns() 