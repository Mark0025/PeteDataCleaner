#!/usr/bin/env python3
"""
Analyze owner patterns and business entity detection
"""

import pandas as pd
import re

def analyze_owner_patterns():
    """Analyze owner patterns in the data."""
    
    print("👥 OWNER PATTERN ANALYSIS:")
    print("="*60)
    
    # Load sample data
    df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=1000)
    
    # Create owner name (First Name + Last Name)
    df['owner_name'] = df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')
    df['owner_name'] = df['owner_name'].str.strip()
    
    print(f"Total records: {len(df):,}")
    print(f"Unique owner names: {df['owner_name'].nunique():,}")
    print(f"Unique mailing addresses: {df['Mailing address'].nunique():,}")
    
    # Analyze business entities
    print("\n🏢 BUSINESS ENTITY ANALYSIS:")
    print("="*60)
    
    # Common business indicators
    business_indicators = [
        'llc', 'ltd', 'inc', 'corp', 'corporation', 'company', 'co\\.',
        'trust', 'estate', 'bank', 'mortgage', 'investments', 'properties',
        'holdings', 'management', 'realty', 'real estate'
    ]
    
    business_pattern = re.compile('|'.join(business_indicators), re.IGNORECASE)
    
    # Categorize owners
    business_owners = []
    individual_owners = []
    
    for owner_name in df['owner_name'].unique():
        if pd.isna(owner_name) or owner_name == '':
            continue
            
        if business_pattern.search(owner_name):
            business_owners.append(owner_name)
        else:
            individual_owners.append(owner_name)
    
    print(f"Business entities: {len(business_owners):,}")
    print(f"Individual owners: {len(individual_owners):,}")
    
    print("\n🏢 SAMPLE BUSINESS ENTITIES:")
    for entity in business_owners[:10]:
        print(f"  {entity}")
    
    print("\n👤 SAMPLE INDIVIDUAL OWNERS:")
    for owner in individual_owners[:10]:
        print(f"  {owner}")
    
    # Analyze mailing address patterns
    print("\n📮 MAILING ADDRESS ANALYSIS:")
    print("="*60)
    
    # Group by mailing address
    addr_groups = df.groupby('Mailing address')
    
    print(f"Addresses with multiple owners: {sum(addr_groups.size() > 1):,}")
    print(f"Addresses with single owner: {sum(addr_groups.size() == 1):,}")
    
    # Show examples of addresses with multiple owners
    print("\n🏠 ADDRESSES WITH MULTIPLE OWNERS:")
    for addr, group in addr_groups:
        if len(group) > 1:
            print(f"\nAddress: {addr}")
            print(f"  Owners: {len(group)}")
            for _, row in group.head(3).iterrows():
                owner = f"{row['First Name']} {row['Last Name']}".strip()
                print(f"    - {owner}")
            if len(group) > 3:
                print(f"    ... and {len(group) - 3} more")
            break  # Just show first example
    
    # Analyze property ownership patterns
    print("\n🏠 PROPERTY OWNERSHIP PATTERNS:")
    print("="*60)
    
    # Group by owner name
    owner_groups = df.groupby('owner_name')
    
    print(f"Owners with multiple properties: {sum(owner_groups.size() > 1):,}")
    print(f"Owners with single property: {sum(owner_groups.size() == 1):,}")
    
    # Show examples of owners with multiple properties
    print("\n👤 OWNERS WITH MULTIPLE PROPERTIES:")
    for owner, group in owner_groups:
        if len(group) > 1:
            print(f"\nOwner: {owner}")
            print(f"  Properties: {len(group)}")
            for _, row in group.head(3).iterrows():
                prop_addr = row['Property address']
                print(f"    - {prop_addr}")
            if len(group) > 3:
                print(f"    ... and {len(group) - 3} more")
            break  # Just show first example
    
    # Contact quality analysis
    print("\n📞 CONTACT QUALITY ANALYSIS:")
    print("="*60)
    
    # Analyze phone data availability
    phone_cols = [col for col in df.columns if 'Phone' in col and col.count(' ') == 1]
    status_cols = [col for col in df.columns if 'Phone Status' in col]
    
    print(f"Phone columns available: {len(phone_cols)}")
    print(f"Status columns available: {len(status_cols)}")
    
    # Sample phone status analysis
    if status_cols:
        print("\n📊 SAMPLE PHONE STATUS DISTRIBUTION:")
        for status_col in status_cols[:3]:  # First 3 status columns
            status_counts = df[status_col].value_counts()
            print(f"\n{status_col}:")
            for status, count in status_counts.head(5).items():
                print(f"  {status}: {count}")

if __name__ == "__main__":
    analyze_owner_patterns() 