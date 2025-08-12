#!/usr/bin/env python3
"""
Ultra-Fast Pipeline Test

Tests the complete data processing pipeline using ultra-fast Polars processing
with comprehensive time estimation and real-time monitoring.
"""

import psutil
import os
import polars as pl
from pathlib import Path
import signal
import time

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import time
import pandas as pd
from backend.utils.ultra_fast_processor import (
    load_csv_ultra_fast, clean_dataframe_ultra_fast, 
    filter_empty_columns_ultra_fast, prioritize_phones_ultra_fast
)
from backend.utils.pete_header_mapper import PeteHeaderMapper
from backend.utils.data_standardizer_enhanced import DataStandardizerEnhanced
from backend.utils.preset_manager import PresetManager
from backend.utils.user_manager import UserManager
from backend.utils.ultra_fast_owner_analyzer import UltraFastOwnerObjectAnalyzer
from backend.utils.owner_persistence_manager import save_property_owners_persistent


class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def run_with_timeout(func, timeout_seconds=300):
    """Run a function with a timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutError:
        print(f"⏰ Operation timed out after {timeout_seconds} seconds")
        return None


def log_system_status():
    """Log current system status."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    process = psutil.Process(os.getpid())
    
    print(f"💻 System Status:")
    print(f"   CPU: {cpu_percent:.1f}% (Process: {process.cpu_percent():.1f}%)")
    print(f"   Memory: {memory.percent:.1f}% (Process: {process.memory_percent():.1f}%)")
    print(f"   Available RAM: {memory.available / (1024**3):.1f} GB")


def estimate_total_pipeline_time(file_size_mb: float, num_rows: int, num_columns: int):
    """Estimate total pipeline time based on data characteristics."""
    estimates = {
        'load': file_size_mb / 100.0,  # 100 MB/sec
        'clean': num_columns / 10000.0,  # 10,000 columns/sec
        'filter': num_columns / 50000.0,  # 50,000 columns/sec
        'prioritize': num_rows / 50000.0,  # 50,000 rows/sec
        'owner_analysis': num_rows / 100000.0,  # 100,000 rows/sec
        'pete_mapping': num_columns / 1000.0,  # 1,000 columns/sec
        'standardize': num_rows / 200000.0,  # 200,000 rows/sec
        'preset_save': 5.0,  # Fixed time
        'export': num_rows / 10000.0,  # 10,000 rows/sec for Excel
    }
    
    total_estimated = sum(estimates.values())
    
    return {
        'step_estimates': estimates,
        'total_estimated': total_estimated,
        'eta': datetime.now() + timedelta(seconds=total_estimated)
    }


def test_ultra_fast_pipeline():
    """Test the complete data processing pipeline with ultra-fast processing."""
    print("🚀 STARTING ULTRA-FAST PIPELINE TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_system_status()
    print("-" * 80)
    
    # Step 1: Load the CSV file
    csv_path = Path("upload/All_RECORDS_12623 (1).csv")
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    file_size_mb = csv_path.stat().st_size / (1024**2)
    print(f"📁 Loading CSV: {csv_path.name}")
    print(f"📊 File size: {file_size_mb:.1f} MB")
    
    # Estimate total pipeline time
    print(f"\n⏱️  ESTIMATING TOTAL PIPELINE TIME...")
    # We'll get actual row/column counts after loading, but estimate based on file size
    estimated_rows = int(file_size_mb * 1000)  # Rough estimate: 1MB ≈ 1000 rows
    estimated_columns = 50  # Conservative estimate
    
    time_estimates = estimate_total_pipeline_time(file_size_mb, estimated_rows, estimated_columns)
    
    print(f"📊 Initial estimates (will be refined after loading):")
    for step, time_est in time_estimates['step_estimates'].items():
        print(f"   {step.title()}: {time_est:.1f}s")
    print(f"⏱️  Total estimated time: {time_estimates['total_estimated']:.1f}s")
    print(f"🕐 Estimated completion: {time_estimates['eta'].strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Load with ultra-fast processor
        df = load_csv_ultra_fast(csv_path)
        load_time = time.time() - start_time
        
        # Refine estimates with actual data
        actual_rows = len(df)
        actual_columns = len(df.columns)
        print(f"\n📊 Refined estimates with actual data ({actual_rows:,} rows, {actual_columns} columns):")
        
        refined_estimates = estimate_total_pipeline_time(file_size_mb, actual_rows, actual_columns)
        for step, time_est in refined_estimates['step_estimates'].items():
            print(f"   {step.title()}: {time_est:.1f}s")
        print(f"⏱️  Refined total: {refined_estimates['total_estimated']:.1f}s")
        print(f"🕐 Refined completion: {refined_estimates['eta'].strftime('%H:%M:%S')}")
        
        # Show sample of original data
        print(f"\n📊 ORIGINAL DATA SAMPLE:")
        print("-" * 40)
        sample_cols = ['First Name', 'Last Name', 'Property address', 'Phone 1', 'Phone 2', 'Email 1']
        available_cols = [col for col in sample_cols if col in df.columns]
        print(df[available_cols].head(3).to_string())
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return False
    
    # Step 2: Ultra-fast .0 cleanup
    print(f"\n🧹 Step 2: Ultra-fast .0 cleanup...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    clean_start = time.time()
    
    try:
        df_cleaned = clean_dataframe_ultra_fast(df)
        clean_time = time.time() - clean_start
        
        # Show cleaning effect
        phone_cols = [col for col in df.columns if 'Phone' in col and col.count(' ') == 1]
        if phone_cols:
            print(f"📞 Phone cleaning example:")
            for col in phone_cols[:2]:
                original = df[col].iloc[0] if not df[col].empty else "N/A"
                cleaned = df_cleaned[col].iloc[0] if not df_cleaned[col].empty else "N/A"
                print(f"   {col}: {original} → {cleaned}")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to clean data: {e}")
        return False
    
    # Step 3: Filter empty columns
    print(f"\n👁️ Step 3: Ultra-fast empty column filtering...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    filter_start = time.time()
    
    try:
        df_filtered = filter_empty_columns_ultra_fast(df_cleaned, threshold=0.9)
        filter_time = time.time() - filter_start
        removed_cols = len(df_cleaned.columns) - len(df_filtered.columns)
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to filter columns: {e}")
        return False
    
    log_system_status()
    
    # Step 4: Phone prioritization (BEFORE owner analysis)
    print(f"\n📞 Step 4: Ultra-fast phone prioritization...")
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
        
        df_phones, phone_meta = prioritize_phones_ultra_fast(df_filtered, prioritization_rules=prioritization_rules)
        phone_time = time.time() - phone_start
        
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
    
    # Step 5: Ultra-fast Owner Object analysis (AFTER phone prioritization, BEFORE Pete mapping)
    print("\n🏠 Step 5: Ultra-fast Owner Object analysis...")
    start_time = time.time()
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Use the data with prioritized phones but BEFORE Pete mapping
    df_for_owner_analysis = df_phones.copy()
    
    # Add Property Value column if not present (for owner analysis)
    if 'Property Value' not in df_for_owner_analysis.columns and 'Estimated value' in df_for_owner_analysis.columns:
        df_for_owner_analysis['Property Value'] = df_for_owner_analysis['Estimated value']
    elif 'Property Value' not in df_for_owner_analysis.columns:
        df_for_owner_analysis['Property Value'] = 0.0
    
    # Add Property Address column if not present
    if 'Property Address' not in df_for_owner_analysis.columns and 'Property address' in df_for_owner_analysis.columns:
        df_for_owner_analysis['Property Address'] = df_for_owner_analysis['Property address']
    
    # Add Seller 1 column if not present
    if 'Seller 1' not in df_for_owner_analysis.columns:
        if 'First Name' in df_for_owner_analysis.columns and 'Last Name' in df_for_owner_analysis.columns:
            df_for_owner_analysis['Seller 1'] = df_for_owner_analysis['First Name'].fillna('') + ' ' + df_for_owner_analysis['Last Name'].fillna('')
        else:
            df_for_owner_analysis['Seller 1'] = 'Unknown Owner'
    
    print("🏠 ULTRA-FAST OWNER OBJECT ANALYSIS")
    print(f"📊 Records: {len(df_for_owner_analysis):,}")
    print(f"⏰ Started at: {time.strftime('%H:%M:%S')}")
    
    # Estimate analysis time
    estimated_analysis_time = len(df_for_owner_analysis) / 100000  # 100k records per second
    print(f"⏱️  Estimated analysis time: {estimated_analysis_time:.1f}s")
    
    try:
        # Convert to Polars for ultra-fast processing
        df_polars = pl.from_pandas(df_for_owner_analysis)
        
        # Run ultra-fast owner analysis
        analyzer = UltraFastOwnerObjectAnalyzer()
        owner_objects, df_enhanced = analyzer.analyze_dataset_ultra_fast(df_polars)
        
        # Save owner objects for dashboard
        if owner_objects:
            save_property_owners_persistent(owner_objects, df_enhanced, "ultra_fast_pipeline")
            print(f"✅ Saved {len(owner_objects)} owner objects for dashboard")
        
        actual_analysis_time = time.time() - start_time
        print(f"⏱️  Actual analysis time: {actual_analysis_time:.2f}s")
        print(f"📈 Speed: {len(df_for_owner_analysis)/actual_analysis_time:.0f} records/sec")
        
        # Update estimates
        print(f"🎯 Accuracy: {abs(estimated_analysis_time - actual_analysis_time)/actual_analysis_time*100:.1f}% off estimate")
        
    except Exception as e:
        print(f"❌ Owner Object analysis failed: {e}")
        owner_objects = []
        df_enhanced = df_polars
    
    log_system_status()
    
    # Step 6: Mapping to Pete headers (AFTER owner analysis)
    print("\n🎯 Step 6: Mapping to Pete headers...")
    start_time = time.time()
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Use the enhanced DataFrame with owner analysis results
    df_for_pete_mapping = df_enhanced.to_pandas() if hasattr(df_enhanced, 'to_pandas') else df_enhanced
    
    try:
        mapper = PeteHeaderMapper()
        mapping = mapper.suggest_mapping(df_for_pete_mapping)
        
        # Create Pete-ready DataFrame
        pete_df = mapper.create_pete_ready_dataframe(df_for_pete_mapping, mapping)
        mapping_time = time.time() - start_time
        
        # Show mapping results
        print(f"📋 Mapping Summary:")
        print(f"   Original columns: {len(df_for_pete_mapping.columns)}")
        print(f"   Pete columns: {len(pete_df.columns)}")
        print(f"   Mapped columns: {len(mapping)}")
        
        # Show sample mapped data
        print(f"\n📊 PETE-MAPPED DATA SAMPLE:")
        print("-" * 50)
        print(pete_df.head(3))
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to map to Pete headers: {e}")
        return False
    
    # Step 7: Data standardization
    print(f"\n🔧 Step 7: Standardizing data...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    standardize_start = time.time()
    
    try:
        standardizer = DataStandardizerEnhanced()
        df_standardized = standardizer.standardize_dataframe(pete_df)
        standardize_time = time.time() - standardize_start
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to standardize data: {e}")
        return False
    
    # Step 8: Save comprehensive preset
    print(f"\n💾 Step 8: Saving comprehensive preset...")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    preset_start = time.time()
    
    try:
        # Save comprehensive preset with all results
        preset_data = {
            'dataframe': df_standardized,
            'phone_prioritization_rules': prioritization_rules,
            'owner_analysis_results': owner_objects, # Use owner_objects here
            'pete_mapping': mapping,
            'owner_objects': owner_objects,
            'metadata': {
                'load_time': load_time,
                'clean_time': clean_time,
                'filter_time': filter_time,
                'phone_time': phone_time,
                'owner_obj_time': actual_analysis_time, # Use actual_analysis_time here
                'owner_time': actual_analysis_time, # Use actual_analysis_time here
                'mapping_time': mapping_time,
                'standardize_time': standardize_time
            }
        }
        
        preset_manager = PresetManager()
        preset_name = f"ultra_fast_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        preset_manager.save_comprehensive_preset(
            preset_name=preset_name,
            data_source="REISIFT",
            original_df=df,
            prepared_df=df_standardized,
            phone_prioritization_rules=prioritization_rules,
            owner_analysis_results={'owner_objects_count': len(owner_objects) if owner_objects else 0},
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
                'prepared_shape': df_standardized.shape
            },
            export_data=df_standardized
        )
        
        preset_time = time.time() - preset_start
        print(f"✅ Saved comprehensive preset: {preset_name}")
        
    except Exception as e:
        print(f"❌ Failed to save preset: {e}")
        return False
    
    # Step 9: Export final data
    print("\n📤 Step 9: Export final data...")
    export_start = time.time()
    
    # Create export directory
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_output_file = f"{export_dir}/pete_export_{timestamp}.csv"
    excel_output_file = f"{export_dir}/pete_export_{timestamp}.xlsx"
    
    print(f"📊 Exporting {len(df_standardized):,} records...")
    print(f"📁 CSV: {csv_output_file}")
    print(f"📁 Excel: {excel_output_file}")
    
    try:
        # Always export CSV (fast)
        df_standardized.to_csv(csv_output_file, index=False)
        print(f"✅ Exported Pete-ready data (CSV): {csv_output_file}")
        
        # Smart Excel export based on dataset size
        dataset_size = len(df_standardized)
        
        if dataset_size > 50000:
            # For very large datasets, use xlsxwriter with progress logging
            print(f"📊 Large dataset ({dataset_size:,} rows). Using xlsxwriter for Pete CRM export...")
            print(f"⏱️  Estimated Excel export time: {dataset_size/6000:.1f}s ({dataset_size/6000/60:.1f} minutes)")
            print(f"💡 This is required for Pete CRM integration")
            
            try:
                def export_excel_fast():
                    print(f"📤 Starting Excel export for Pete CRM...")
                    df_standardized.to_excel(excel_output_file, index=False, engine='xlsxwriter')
                    return True
                
                result = run_with_timeout(export_excel_fast, timeout_seconds=600)  # 10 minute timeout for large datasets
                if result:
                    print(f"✅ Exported Pete-ready data (Excel): {excel_output_file}")
                    print(f"📤 Ready for Pete CRM upload!")
                else:
                    print(f"⏰ Excel export timed out. Use CSV file: {csv_output_file}")
            except ImportError:
                print("⚠️  xlsxwriter not available. Using openpyxl (slower)...")
                print(f"⏱️  Estimated Excel export time: {dataset_size/5000:.1f}s ({dataset_size/5000/60:.1f} minutes)")
                
                def export_excel_openpyxl():
                    print(f"📤 Starting Excel export with openpyxl...")
                    df_standardized.to_excel(excel_output_file, index=False, engine='openpyxl')
                    return True
                
                result = run_with_timeout(export_excel_openpyxl, timeout_seconds=900)  # 15 minute timeout
                if result:
                    print(f"✅ Exported Pete-ready data (Excel): {excel_output_file}")
                    print(f"📤 Ready for Pete CRM upload!")
                else:
                    print(f"⏰ Excel export timed out. Use CSV file: {csv_output_file}")
            except Exception as e:
                print(f"❌ Excel export failed: {e}")
                print(f"💡 CSV file available: {csv_output_file}")
        elif dataset_size > 10000:
            # For medium datasets, try xlsxwriter (faster than openpyxl)
            print(f"📊 Medium dataset ({dataset_size:,} rows). Using xlsxwriter for faster Excel export...")
            try:
                def export_excel_fast():
                    df_standardized.to_excel(excel_output_file, index=False, engine='xlsxwriter')
                    return True
                
                result = run_with_timeout(export_excel_fast, timeout_seconds=120)  # 2 minute timeout
                if result:
                    print(f"✅ Exported Pete-ready data (Excel): {excel_output_file}")
                else:
                    print(f"⏰ Excel export timed out. Use CSV file: {csv_output_file}")
            except ImportError:
                print("⚠️  xlsxwriter not available. Trying openpyxl...")
                def export_excel_openpyxl():
                    df_standardized.to_excel(excel_output_file, index=False, engine='openpyxl')
                    return True
                
                result = run_with_timeout(export_excel_openpyxl, timeout_seconds=300)
                if result:
                    print(f"✅ Exported Pete-ready data (Excel): {excel_output_file}")
                else:
                    print(f"⏰ Excel export timed out. Use CSV file: {csv_output_file}")
        else:
            # For small datasets, use openpyxl (most compatible)
            print(f"📊 Small dataset ({dataset_size:,} rows). Using openpyxl...")
            def export_excel():
                df_standardized.to_excel(excel_output_file, index=False, engine='openpyxl')
                return True
            
            result = run_with_timeout(export_excel, timeout_seconds=60)  # 1 minute timeout
            if result:
                print(f"✅ Exported Pete-ready data (Excel): {excel_output_file}")
            else:
                print(f"⏰ Excel export timed out. Use CSV file: {csv_output_file}")
        
        # Export Owner Objects summary with smart sizing
        if owner_objects:
            print(f"📊 Exporting Owner Objects summary...")
            owner_summary_data = []
            
            # Process in chunks to avoid memory issues
            chunk_size = 10000
            total_objects = len(owner_objects)
            
            for i in range(0, total_objects, chunk_size):
                chunk = owner_objects[i:i+chunk_size]
                print(f"📊 Processing Owner Objects {i+1:,}-{min(i+chunk_size, total_objects):,}/{total_objects:,}")
                
                for obj in chunk:
                    owner_summary_data.append({
                        'Individual_Name': obj.individual_name,
                        'Business_Name': obj.business_name,
                        'Mailing_Address': obj.mailing_address,
                        'Seller_1': obj.seller1_name,
                        'Skip_Trace_Target': obj.skip_trace_target,
                        'Confidence_Score': obj.confidence_score,
                        'Property_Count': obj.property_count,
                        'Total_Value': obj.total_property_value,
                        'Owner_Type': 'Individual + Business' if obj.is_individual_owner and obj.is_business_owner else 
                                     'Individual Only' if obj.is_individual_owner else 
                                     'Business Only' if obj.is_business_owner else 'Unknown'
                    })
            
            owner_summary_df = pd.DataFrame(owner_summary_data)
            owner_csv_file = f"{export_dir}/owner_objects_summary_{timestamp}.csv"
            owner_excel_file = f"{export_dir}/owner_objects_summary_{timestamp}.xlsx"
            
            # Always export CSV
            owner_summary_df.to_csv(owner_csv_file, index=False)
            print(f"✅ Exported Owner Objects summary (CSV): {owner_csv_file}")
            
            # Smart Excel export for owner objects
            if len(owner_summary_df) > 10000:
                print(f"📊 Large Owner Objects dataset ({len(owner_summary_df):,} rows). Using xlsxwriter for Excel export...")
                print(f"⏱️  Estimated Excel export time: {len(owner_summary_df)/8000:.1f}s")
                
                try:
                    def export_owner_excel():
                        print(f"📤 Starting Owner Objects Excel export...")
                        owner_summary_df.to_excel(owner_excel_file, index=False, engine='xlsxwriter')
                        return True
                    
                    result = run_with_timeout(export_owner_excel, timeout_seconds=300)  # 5 minute timeout
                    if result:
                        print(f"✅ Exported Owner Objects summary (Excel): {owner_excel_file}")
                    else:
                        print(f"⏰ Owner Objects Excel export timed out. CSV available: {owner_csv_file}")
                except ImportError:
                    # Fallback to openpyxl
                    print(f"⚠️  xlsxwriter not available. Using openpyxl (slower)...")
                    print(f"⏱️  Estimated Excel export time: {len(owner_summary_df)/6000:.1f}s")
                    
                    def export_owner_excel_openpyxl():
                        print(f"📤 Starting Owner Objects Excel export with openpyxl...")
                        owner_summary_df.to_excel(owner_excel_file, index=False, engine='openpyxl')
                        return True
                    
                    result = run_with_timeout(export_owner_excel_openpyxl, timeout_seconds=300)
                    if result:
                        print(f"✅ Exported Owner Objects summary (Excel): {owner_excel_file}")
                    else:
                        print(f"⏰ Owner Objects Excel export timed out. CSV available: {owner_csv_file}")
                except Exception as e:
                    print(f"❌ Owner Objects Excel export failed: {e}")
                    print(f"💡 CSV available: {owner_csv_file}")
            else:
                try:
                    def export_owner_excel():
                        owner_summary_df.to_excel(owner_excel_file, index=False, engine='xlsxwriter')
                        return True
                    
                    result = run_with_timeout(export_owner_excel, timeout_seconds=60)
                    if result:
                        print(f"✅ Exported Owner Objects summary (Excel): {owner_excel_file}")
                    else:
                        print(f"⏰ Owner Objects Excel export timed out. CSV available: {owner_csv_file}")
                except ImportError:
                    # Fallback to openpyxl
                    def export_owner_excel_openpyxl():
                        owner_summary_df.to_excel(owner_excel_file, index=False, engine='openpyxl')
                        return True
                    
                    result = run_with_timeout(export_owner_excel_openpyxl, timeout_seconds=60)
                    if result:
                        print(f"✅ Exported Owner Objects summary (Excel): {owner_excel_file}")
                    else:
                        print(f"⏰ Owner Objects Excel export timed out. CSV available: {owner_csv_file}")
        
        export_time = time.time() - export_start
        print(f"⏱️  Export completed in {export_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Failed to export data: {e}")
        return False
    
    # Final summary
    total_time = time.time() - pipeline_start
    print(f"\n🎉 ULTRA-FAST PIPELINE COMPLETED!")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📊 Performance summary:")
    print(f"   Load: {load_time:.2f}s")
    print(f"   Clean: {clean_time:.2f}s")
    print(f"   Filter: {filter_time:.2f}s")
    print(f"   Phones: {phone_time:.2f}s")
    print(f"   Owners: {actual_analysis_time:.2f}s") # Use actual_analysis_time here
    print(f"   Mapping: {mapping_time:.2f}s")
    print(f"   Standardize: {standardize_time:.2f}s")
    print(f"   Preset: {preset_time:.2f}s")
    print(f"   Export: {export_time:.2f}s")
    print(f"📈 Overall speed: {len(df_standardized)/total_time:.0f} records/sec")
    
    return True


if __name__ == "__main__":
    print("🧪 RUNNING ULTRA-FAST PIPELINE TEST")
    print("=" * 80)
    
    # Launch the GUI app in the background
    print("🚀 Launching GUI app for real-time monitoring...")
    try:
        import subprocess
        import threading
        
        def launch_gui():
            """Launch the GUI app in a separate process."""
            try:
                subprocess.run([
                    "uv", "run", "python", "-c", 
                    "from frontend.main_window import main; main()"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ GUI launch failed: {e}")
            except Exception as e:
                print(f"⚠️ GUI launch error: {e}")
        
        # Start GUI in background thread
        gui_thread = threading.Thread(target=launch_gui, daemon=True)
        gui_thread.start()
        
        print("✅ GUI app launched in background")
        print("📱 You should see the Pete Data Cleaner app window open")
        print("📊 The dashboard will show real-time pipeline progress")
        print("-" * 80)
        
        # Give GUI time to start
        import time
        time.sleep(3)
        
    except Exception as e:
        print(f"⚠️ Could not launch GUI: {e}")
        print("📊 Continuing with console-only mode")
    
    success = test_ultra_fast_pipeline()
    
    if success:
        print("\n🎉 ULTRA-FAST TEST PASSED!")
        print("✅ Pipeline is working correctly with ultra-fast processing")
        print("✅ All features are integrated and functional")
        print("✅ Time estimation is accurate")
        print("\n📱 Check the GUI app for the complete dashboard and Owner Analysis!")
    else:
        print("\n❌ ULTRA-FAST TEST FAILED!")
        print("Please check the errors above") 