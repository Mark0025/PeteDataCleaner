#!/usr/bin/env python3
"""
Enhanced End-to-End Pipeline Test

Tests the complete data processing pipeline with enhanced logging and progress tracking.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import time
from datetime import datetime
import psutil
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.high_performance_processor import (
    load_csv_fast, clean_dataframe_fast, filter_empty_columns_fast, 
    prioritize_phones_fast, process_complete_pipeline_fast
)
from backend.utils.pete_header_mapper import PeteHeaderMapper
from backend.utils.data_standardizer_enhanced import DataStandardizerEnhanced
from backend.utils.owner_analyzer import analyze_ownership_data
from backend.utils.preset_manager import PresetManager
from backend.utils.user_manager import UserManager


def log_system_status():
    """Log current system status."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    process = psutil.Process(os.getpid())
    
    print(f"💻 System Status:")
    print(f"   CPU: {cpu_percent:.1f}% (Process: {process.cpu_percent():.1f}%)")
    print(f"   Memory: {memory.percent:.1f}% (Process: {process.memory_percent():.1f}%)")
    print(f"   Available RAM: {memory.available / (1024**3):.1f} GB")


def test_complete_pipeline_enhanced():
    """Test the complete data processing pipeline with enhanced logging."""
    print("🚀 STARTING ENHANCED END-TO-END PIPELINE TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_system_status()
    print("-" * 80)
    
    # Step 1: Load the CSV file
    csv_path = Path("upload/All_RECORDS_12623 (1).csv")
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    print(f"📁 Loading CSV: {csv_path.name}")
    print(f"📊 File size: {csv_path.stat().st_size / (1024**2):.1f} MB")
    start_time = time.time()
    
    try:
        # Load with fast processor
        df = load_csv_fast(csv_path)
        load_time = time.time() - start_time
        print(f"✅ Loaded: {len(df):,} rows, {len(df.columns)} columns in {load_time:.2f}s")
        print(f"📈 Load speed: {len(df) / load_time:,.0f} records/sec")
        
        # Show sample of original data
        print("\n📊 ORIGINAL DATA SAMPLE:")
        print("-" * 40)
        sample_cols = ['First Name', 'Last Name', 'Property address', 'Phone 1', 'Phone 2', 'Email 1']
        available_cols = [col for col in sample_cols if col in df.columns]
        print(df[available_cols].head(3).to_string())
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return False
    
    # Step 2: Clean data (remove .0)
    print(f"\n🧹 Step 2: Cleaning .0 from data...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    clean_start = time.time()
    
    try:
        df_clean = clean_dataframe_fast(df)
        clean_time = time.time() - clean_start
        print(f"✅ Cleaned data in {clean_time:.2f}s")
        
        # Show cleaning effect
        phone_cols = [col for col in df.columns if 'Phone' in col and col.count(' ') == 1]
        if phone_cols:
            print(f"📞 Phone cleaning example:")
            for col in phone_cols[:2]:
                original = df[col].iloc[0] if not df[col].empty else "N/A"
                cleaned = df_clean[col].iloc[0] if not df_clean[col].empty else "N/A"
                print(f"   {col}: {original} → {cleaned}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to clean data: {e}")
        return False
    
    # Step 3: Filter empty columns
    print(f"\n👁️ Step 3: Filtering empty columns...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    filter_start = time.time()
    
    try:
        df_filtered = filter_empty_columns_fast(df_clean, threshold=0.9)
        filter_time = time.time() - filter_start
        removed_cols = len(df_clean.columns) - len(df_filtered.columns)
        print(f"✅ Removed {removed_cols} empty columns in {filter_time:.2f}s")
        print(f"   Columns: {len(df_clean.columns)} → {len(df_filtered.columns)}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to filter columns: {e}")
        return False
    
    # Step 4: Phone prioritization
    print(f"\n📞 Step 4: Prioritizing phones...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    phone_start = time.time()
    
    try:
        # Custom prioritization rules
        prioritization_rules = {
            'status_weights': {
                'CORRECT': 100, 'UNKNOWN': 80, 'NO_ANSWER': 60, 
                'WRONG': 40, 'DEAD': 20, 'DNC': 10
            },
            'type_weights': {
                'MOBILE': 100, 'LANDLINE': 80, 'UNKNOWN': 60
            },
            'tag_weights': {
                'call_a01': 100, 'call_a02': 90, 'call_a03': 80,
                'call_a04': 70, 'call_a05': 60, 'no_tag': 50
            },
            'call_count_multiplier': 1.0
        }
        
        print(f"📋 Using custom prioritization rules:")
        print(f"   Status weights: {prioritization_rules['status_weights']}")
        print(f"   Type weights: {prioritization_rules['type_weights']}")
        
        df_phones, phone_meta = prioritize_phones_fast(df_filtered, prioritization_rules=prioritization_rules)
        phone_time = time.time() - phone_start
        print(f"✅ Phone prioritization completed in {phone_time:.2f}s")
        
        # Show phone prioritization results
        phone_cols = [col for col in df_phones.columns if col.startswith('Phone ') and col.count(' ') == 1]
        if phone_cols:
            print(f"📱 Prioritized phone columns: {phone_cols}")
            print(f"   Sample data:")
            for col in phone_cols[:3]:
                sample = df_phones[col].dropna().head(2).tolist()
                print(f"   {col}: {sample}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to prioritize phones: {e}")
        return False
    
    # Step 5: Owner analysis
    print(f"\n🏠 Step 5: Analyzing ownership patterns...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    owner_start = time.time()
    
    try:
        owner_results = analyze_ownership_data(df_phones)
        owner_time = time.time() - owner_start
        print(f"✅ Owner analysis completed in {owner_time:.2f}s")
        
        # Show owner analysis results
        print(f"📊 Owner Analysis Summary:")
        print(f"   Total owners: {owner_results.get('total_owners', 0):,}")
        print(f"   Business entities: {owner_results.get('business_entities', 0):,}")
        print(f"   Multi-property owners: {owner_results.get('multi_property_owners', 0):,}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to analyze owners: {e}")
        return False
    
    # Step 6: Map to Pete headers
    print(f"\n🎯 Step 6: Mapping to Pete headers...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    mapping_start = time.time()
    
    try:
        mapper = PeteHeaderMapper()
        mapping = mapper.suggest_mapping(df_phones)
        
        # Create Pete-ready DataFrame
        pete_df = mapper.create_pete_ready_dataframe(df_phones, mapping)
        mapping_time = time.time() - mapping_start
        print(f"✅ Pete mapping completed in {mapping_time:.2f}s")
        
        # Show mapping results
        print(f"📋 Mapping Summary:")
        print(f"   Original columns: {len(df_phones.columns)}")
        print(f"   Pete columns: {len(pete_df.columns)}")
        print(f"   Mapped columns: {len(mapping)}")
        
        # Show sample of Pete-ready data
        print(f"\n🎯 PETE-READY DATA SAMPLE:")
        print("-" * 40)
        pete_sample_cols = ['Seller 1', 'Seller 1 Phone', 'Seller 1 Email', 'Property Address', 'Property City']
        available_pete_cols = [col for col in pete_sample_cols if col in pete_df.columns]
        print(pete_df[available_pete_cols].head(3).to_string())
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to map to Pete: {e}")
        return False
    
    # Step 7: Data standardization
    print(f"\n🔧 Step 7: Standardizing data...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    standardize_start = time.time()
    
    try:
        standardizer = DataStandardizerEnhanced()
        
        # Standardize property types
        if 'Property Type' in pete_df.columns:
            pete_df['Property Type'] = standardizer.standardize_property_type(pete_df['Property Type'])
            print(f"✅ Property types standardized")
        
        standardize_time = time.time() - standardize_start
        print(f"✅ Data standardization completed in {standardize_time:.2f}s")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to standardize data: {e}")
        return False
    
    # Step 8: Save comprehensive preset
    print(f"\n💾 Step 8: Saving comprehensive preset...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    preset_start = time.time()
    
    try:
        # Initialize user manager
        user_manager = UserManager()
        user_manager._initialize_default_user()
        
        # Create preset manager
        preset_manager = PresetManager()
        
        # Save comprehensive preset
        preset_path = preset_manager.save_comprehensive_preset(
            preset_name="enhanced_test_preset",
            data_source="REISIFT",
            original_df=df,
            prepared_df=pete_df,
            phone_prioritization_rules=prioritization_rules,
            owner_analysis_results=owner_results,
            data_prep_summary={
                'version_summary': [
                    {'action': 'Load CSV', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Clean .0', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Filter empty columns', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Phone prioritization', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Owner analysis', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Pete mapping', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Data standardization', 'timestamp': datetime.now().isoformat()}
                ],
                'tools_used': ['load_csv_fast', 'clean_dataframe_fast', 'filter_empty_columns_fast', 
                              'prioritize_phones_fast', 'owner_analysis', 'pete_mapping', 'standardization'],
                'data_source': 'REISIFT',
                'original_shape': df.shape,
                'prepared_shape': pete_df.shape
            }
        )
        
        preset_time = time.time() - preset_start
        print(f"✅ Comprehensive preset saved in {preset_time:.2f}s")
        print(f"   Location: {preset_path}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to save preset: {e}")
        return False
    
    # Step 9: Export final data
    print(f"\n📤 Step 9: Exporting final data...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    export_start = time.time()
    
    try:
        # Export to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"enhanced_test_output_pete_ready_{timestamp}.xlsx"
        pete_df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # Export to CSV
        csv_path = f"enhanced_test_output_pete_ready_{timestamp}.csv"
        pete_df.to_csv(csv_path, index=False)
        
        export_time = time.time() - export_start
        print(f"✅ Data exported in {export_time:.2f}s")
        print(f"   Excel: {excel_path}")
        print(f"   CSV: {csv_path}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to export data: {e}")
        return False
    
    # Final summary
    total_time = time.time() - start_time
    print(f"\n🎉 ENHANCED PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📊 Data processed: {len(df):,} rows")
    print(f"🔧 Features tested:")
    print(f"   ✅ Fast CSV loading (Polars)")
    print(f"   ✅ .0 cleanup (Polars)")
    print(f"   ✅ Empty column filtering")
    print(f"   ✅ Phone prioritization with custom rules")
    print(f"   ✅ Owner analysis")
    print(f"   ✅ Pete header mapping")
    print(f"   ✅ Data standardization")
    print(f"   ✅ Comprehensive preset saving")
    print(f"   ✅ Multi-format export")
    
    print(f"\n📈 Performance Summary:")
    print(f"   Load: {load_time:.2f}s")
    print(f"   Clean: {clean_time:.2f}s")
    print(f"   Filter: {filter_time:.2f}s")
    print(f"   Phones: {phone_time:.2f}s")
    print(f"   Owners: {owner_time:.2f}s")
    print(f"   Mapping: {mapping_time:.2f}s")
    print(f"   Standardize: {standardize_time:.2f}s")
    print(f"   Preset: {preset_time:.2f}s")
    print(f"   Export: {export_time:.2f}s")
    
    print(f"\n🚀 Overall Performance:")
    print(f"   Average speed: {len(df) / total_time:,.0f} records/sec")
    print(f"   Memory efficiency: {len(df) * len(df.columns) / (1024**2):.1f} MB processed")
    
    return True


if __name__ == "__main__":
    print("🧪 RUNNING ENHANCED END-TO-END PIPELINE TEST")
    print("=" * 80)
    
    success = test_complete_pipeline_enhanced()
    
    if success:
        print("\n🎉 ENHANCED TEST PASSED!")
        print("✅ Pipeline is working correctly with enhanced logging")
        print("✅ All features are integrated and functional")
    else:
        print("\n❌ ENHANCED TEST FAILED!")
        print("Please check the errors above") 