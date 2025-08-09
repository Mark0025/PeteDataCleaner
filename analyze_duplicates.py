#!/usr/bin/env python3
"""
Analyze duplicate addresses and property type standardization
"""

import pandas as pd

# Load sample data
print("🏠 PROPERTY ADDRESS ANALYSIS:")
print("="*60)
df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=1000)
print(f"Unique addresses: {df['Property address'].nunique():,}")
print(f"Total rows: {len(df):,}")

# Analyze duplicates
addr_counts = df['Property address'].value_counts()
duplicates = addr_counts[addr_counts > 1]
print(f"Addresses with multiple records: {len(duplicates):,}")

print("\n🔍 SAMPLE DUPLICATE ADDRESSES:")
print("="*60)
for addr, count in list(duplicates.head(3).items()):
    print(f"\nAddress: {addr}")
    addr_df = df[df['Property address'] == addr]
    print(f"  Records: {len(addr_df)}")
    
    print("  Phone variations:")
    for i, row in addr_df.head(3).iterrows():
        phones = []
        for j in range(1, 6):
            if pd.notna(row[f'Phone {j}']):
                phones.append(str(row[f'Phone {j}']))
        print(f"    Row {i}: {phones}")
    
    print("  Seller variations:")
    for i, row in addr_df.head(3).iterrows():
        seller = f"{row['First Name']} {row['Last Name']}".strip()
        print(f"    Row {i}: {seller}")

print("\n🏠 PROPERTY TYPE ANALYSIS:")
print("="*60)
if 'Structure type' in df.columns:
    print("Current Structure type values:")
    structure_counts = df['Structure type'].value_counts()
    for prop_type, count in structure_counts.head(10).items():
        print(f"  {prop_type}: {count}")

print("\n📊 DUPLICATION SCENARIOS:")
print("="*60)
print("1. FULL DUPLICATES: Same address + same seller + same phones → DEDUPE")
print("2. ADDRESS DUPLICATES: Same address + different sellers/phones → CREATE SELLER 2,3,4,5")
print("3. PROPERTY TYPE STANDARDIZATION: single family = single family residence = sfr")
print("4. PHONE PRIORITIZATION: Use existing phone prioritizer for Seller 1-5")
print("5. HOLDING STRATEGY: Keep additional sellers until first 5 are processed in Pete") 