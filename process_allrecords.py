#!/usr/bin/env python3
"""
Process All_RECORDS_12623 (1).csv through Pete Data Cleaner features
and export a Pete-ready Excel file.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.trailing_dot_cleanup import clean_dataframe
from backend.utils.phone_prioritizer import prioritize
from backend.utils.data_standardizer import DataStandardizer

def main():
    """Process the All_RECORDS CSV file through Pete Data Cleaner."""
    
    print("🎯 Pete Data Cleaner - Processing All_RECORDS")
    print("=" * 50)
    
    # 1. Load the CSV file
    csv_path = "upload/All_RECORDS_12623 (1).csv"
    print(f"📁 Loading: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        print(f"✅ Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # 2. Show sample of original data
    print(f"\n📊 Original data sample:")
    print(f"Columns: {list(df.columns[:10])}...")
    print(f"First few rows:")
    print(df.head(3).to_string())
    
    # 3. Apply .0 cleanup
    print(f"\n🧹 Applying .0 cleanup...")
    df_cleaned = clean_dataframe(df)
    print(f"✅ .0 cleanup completed")
    
    # 4. Phone prioritization
    print(f"\n📞 Applying phone prioritization...")
    try:
        df_prioritized, phone_meta = prioritize(df_cleaned, max_phones=5)
        print(f"✅ Phone prioritization completed")
        print(f"   - Selected {len(phone_meta)} phone columns")
        for meta in phone_meta[:3]:  # Show first 3
            print(f"   - {meta.column}: {meta.status} ({meta.phone_type})")
    except Exception as e:
        print(f"⚠️ Phone prioritization failed: {e}")
        df_prioritized = df_cleaned
    
    # 5. Define Pete headers (based on common CRM fields)
    pete_headers = [
        "externalId",
        "Fullname", 
        "PropertyAddress",
        "PropertyState",
        "PropertyCity",
        "PropertyZip",
        "Phone1",
        "Phone2", 
        "Phone3",
        "Phone4",
        "Phone5",
        "Email1",
        "Email2",
        "Email3",
        "Source",
        "Notes",
        "Status",
        "CreatedDate",
        "LastContactDate",
        "OwnerName",
        "OwnerPhone",
        "OwnerEmail"
    ]
    
    # 6. Create mapping rules
    mapping_rules = {
        "never_map": ["Phone Status", "Phone Type", "Phone Tag", "Phone Tag"],
        "explicit_map": {
            "first_name": "Fullname",
            "last_name": "Fullname", 
            "address": "PropertyAddress",
            "state": "PropertyState",
            "city": "PropertyCity",
            "zip": "PropertyZip",
            "email": "Email1",
            "phone": "Phone1",
            "source": "Source",
            "notes": "Notes",
            "status": "Status",
            "created_date": "CreatedDate",
            "last_contact": "LastContactDate",
            "owner_name": "OwnerName",
            "owner_phone": "OwnerPhone",
            "owner_email": "OwnerEmail"
        },
        "concat_fields": {
            "Fullname": ["first_name", "last_name"],
            "PropertyAddress": ["address", "city", "state", "zip"]
        },
        "fuzzy_threshold": 70
    }
    
    # 7. Create data standardizer
    print(f"\n🗺️ Mapping to Pete headers...")
    standardizer = DataStandardizer(pete_headers=pete_headers, rules=mapping_rules)
    
    # 8. Propose mapping
    mapping = standardizer.propose_mapping(list(df_prioritized.columns))
    
    # 9. Show mapping results
    print(f"📋 Mapping Results:")
    mapped_count = 0
    for col, (pete_col, confidence, reason) in mapping.items():
        if pete_col and pete_col != f'(used in {pete_col})':
            print(f"   ✅ {col} → {pete_col} ({confidence:.0f}% - {reason})")
            mapped_count += 1
        else:
            print(f"   ❌ {col} → No match ({reason})")
    
    print(f"\n📊 Mapping Summary: {mapped_count} columns mapped out of {len(df_prioritized.columns)}")
    
    # 10. Transform data
    print(f"\n🔄 Transforming data to Pete format...")
    df_pete = standardizer.transform_data(df_prioritized, mapping)
    print(f"✅ Transformation completed")
    print(f"   - Pete format: {df_pete.shape[0]:,} rows, {df_pete.shape[1]} columns")
    
    # 11. Show Pete format sample
    print(f"\n📊 Pete format sample:")
    print(df_pete.head(3).to_string())
    
    # 12. Export to Excel
    output_path = "export/allrecords_pete_ready.xlsx"
    os.makedirs("export", exist_ok=True)
    
    print(f"\n💾 Exporting to: {output_path}")
    try:
        # Use xlsxwriter for faster Excel export
        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # Main Pete-ready data
                df_pete.to_excel(writer, sheet_name='Pete_Ready_Data', index=False)
                
                # Original data for reference
                df_prioritized.to_excel(writer, sheet_name='Original_Processed', index=False)
                
                # Mapping summary
                mapping_df = pd.DataFrame([
                    {
                        'Upload_Column': col,
                        'Pete_Header': pete_col or 'NOT MAPPED',
                        'Confidence': f"{confidence:.0f}%",
                        'Reason': reason
                    }
                    for col, (pete_col, confidence, reason) in mapping.items()
                ])
                mapping_df.to_excel(writer, sheet_name='Mapping_Summary', index=False)
        except ImportError:
            # Fallback to openpyxl if xlsxwriter not available
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main Pete-ready data
                df_pete.to_excel(writer, sheet_name='Pete_Ready_Data', index=False)
                
                # Original data for reference
                df_prioritized.to_excel(writer, sheet_name='Original_Processed', index=False)
                
                # Mapping summary
                mapping_df = pd.DataFrame([
                    {
                        'Upload_Column': col,
                        'Pete_Header': pete_col or 'NOT MAPPED',
                        'Confidence': f"{confidence:.0f}%",
                        'Reason': reason
                    }
                    for col, (pete_col, confidence, reason) in mapping.items()
                ])
                mapping_df.to_excel(writer, sheet_name='Mapping_Summary', index=False)
        
        print(f"✅ Export completed successfully!")
        print(f"📁 File saved: {output_path}")
        print(f"📊 Sheets created:")
        print(f"   - Pete_Ready_Data: {df_pete.shape[0]:,} rows ready for Pete")
        print(f"   - Original_Processed: {df_prioritized.shape[0]:,} rows (processed)")
        print(f"   - Mapping_Summary: {len(mapping)} column mappings")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return
    
    print(f"\n🎉 Success! Your Pete-ready file is ready at: {output_path}")
    print(f"📤 You can now upload this Excel file directly to Pete CRM")

if __name__ == "__main__":
    main() 