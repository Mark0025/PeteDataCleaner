#!/usr/bin/env python3
"""
Inspect phone data structure from upload CSV
"""

import pandas as pd

def inspect_phone_data():
    print("📱 Inspecting phone data structure from upload CSV...")
    
    # Read just a few rows to see the phone data structure
    df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=10)
    
    # Find phone-related columns
    phone_cols = [col for col in df.columns if 'phone' in col.lower()]
    print(f'\n🔍 Phone-related columns found ({len(phone_cols)} total):')
    for col in phone_cols:
        print(f'  📞 {col}')
    
    print('\n📊 Sample phone data (first 5 rows):')
    for i in range(min(5, len(df))):
        print(f'\n--- 📋 Row {i+1} ---')
        for col in phone_cols:
            if col in df.columns:
                value = df.iloc[i][col]
                if pd.notna(value) and value != '':
                    print(f'  {col}: {value}')
    
    print('\n🎯 Phone Status Values Found:')
    status_cols = [col for col in phone_cols if 'status' in col.lower()]
    for col in status_cols:
        unique_values = df[col].dropna().unique()
        print(f'  {col}: {list(unique_values)}')
    
    print('\n📱 Phone Type Values Found:')
    type_cols = [col for col in phone_cols if 'type' in col.lower()]
    for col in type_cols:
        unique_values = df[col].dropna().unique()
        print(f'  {col}: {list(unique_values)}')

if __name__ == "__main__":
    inspect_phone_data()