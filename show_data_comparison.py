#!/usr/bin/env python3
"""
Show data comparison between REISift and Pete-ready format
"""

import pandas as pd
from backend.utils.pete_header_mapper import PeteHeaderMapper
from backend.utils.data_standardizer_enhanced import analyze_property_types

# Load sample of original REISift data
print("📊 YOUR REISIFT DATA (Sample):")
print("="*80)
df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=3)
print(df[['First Name', 'Last Name', 'Property address', 'Property city', 'Property state', 'Property zip', 'Phone 1', 'Phone 2', 'Phone 3', 'Email 1', 'Email 2']].to_string())
print()

# Show Pete's expected headers
print("🎯 PETE EXPECTED HEADERS:")
print("="*80)
pete_headers = PeteHeaderMapper.PETE_HEADERS
print(", ".join(pete_headers))
print()

# Create Pete-ready mapping
mapper = PeteHeaderMapper()
mapping = mapper.suggest_mapping(df)
pete_df = mapper.create_pete_ready_dataframe(df, mapping)

print("🎯 PETE-READY EXPORT (Sample):")
print("="*80)
print(pete_df[['Seller 1', 'Seller 1 Phone', 'Seller 1 Email', 'Property Address', 'Property City', 'Property State', 'Property Zip', 'Phone 1', 'Phone 2', 'Phone 3', 'Phone 4', 'Phone 5']].to_string())
print()

# Show mapping summary
print("📊 MAPPING SUMMARY:")
print("="*80)
print("✅ REISift → Pete Mapping:")
for source, target in mapping.items():
    print(f"   {source} → {target}")

print("\n🔧 CONCATENATION & STANDARDIZATION:")
print("   ✅ Seller 1 = First Name + Last Name")
print("   ✅ Seller 1 Email = Email 1; Email 2; Email 3; Email 4; Email 5")
print("   ✅ Seller 1 Phone = Phone 1 (best contact number)")
print("   ✅ Property Type = Standardized (SFR → Single Family Residential)")

print("\n❌ Missing for Pete (will be empty columns):")
missing = [h for h in pete_headers if h not in pete_df.columns or pete_df[h].isna().all()]
for missing_col in missing:
    print(f"   {missing_col}")

print("\n📈 DATA QUALITY:")
print("="*80)
print(f"   Total rows: {len(df):,}")
print(f"   Seller 1 data: {len(pete_df['Seller 1'].dropna()):,}")
print(f"   Address data: {len(df['Property address'].dropna()):,}")
print(f"   Phone data: {len(df[['Phone 1', 'Phone 2', 'Phone 3', 'Phone 4', 'Phone 5']].dropna(how='all')):,}")
print(f"   Seller 1 Email data: {len(pete_df['Seller 1 Email'].dropna()):,}")
print(f"   Seller 1 Phone data: {len(pete_df['Seller 1 Phone'].dropna()):,}")
print(f"   Pete-ready rows: {len(pete_df):,}")

# Analyze property types if available
if 'Structure type' in df.columns:
    print(f"\n🏠 PROPERTY TYPE ANALYSIS:")
    print("="*80)
    property_analysis = analyze_property_types(df, 'Structure type')
    for prop_type, count in property_analysis.items():
        print(f"   {prop_type}: {count}") 