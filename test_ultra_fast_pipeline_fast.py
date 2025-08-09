#!/usr/bin/env python3
"""
Ultra-Fast Pipeline Test - FAST VERSION

This version skips Excel export for large datasets to ensure fast completion.
"""

import time
import os
import signal
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Import ultra-fast processing functions
from backend.utils.ultra_fast_processor import (
    load_dataframe_ultra_fast,
    clean_dataframe_ultra_fast,
    filter_empty_columns_ultra_fast,
    prioritize_phones_ultra_fast
)

from backend.utils.ultra_fast_owner_analyzer import UltraFastOwnerObjectAnalyzer
from backend.utils.owner_persistence_manager import save_property_owners_persistent
from backend.utils.pete_header_mapper import PeteHeaderMapper
from backend.utils.data_standardizer import DataStandardizerEnhanced
from backend.utils.preset_manager import PresetManager

import pandas as pd
import polars as pl

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
    import psutil
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    print(f"💻 CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB/{memory.total/1024/1024/1024:.1f}GB)")

def estimate_total_pipeline_time(file_size_mb: float, num_rows: int, num_columns: int):
    """Estimate total pipeline time based on data size."""
    # Base estimates (seconds)
    load_time = max(2, file_size_mb / 50)  # 50MB/sec
    clean_time = num_rows / 100000  # 100k rows/sec
    filter_time = num_rows / 200000  # 200k rows/sec
    phone_time = num_rows / 50000   # 50k rows/sec
    owner_time = num_rows / 10000   # 10k rows/sec (most intensive)
    mapping_time = num_rows / 100000  # 100k rows/sec
    export_time = num_rows / 100000  # 100k rows/sec (CSV only)
    
    total_estimated = load_time + clean_time + filter_time + phone_time + owner_time + mapping_time + export_time
    return total_estimated

def test_ultra_fast_pipeline_fast():
    """Test the ultra-fast pipeline with CSV-only export for speed."""
    
    print("🚀 ULTRA-FAST PIPELINE TEST - FAST VERSION")
    print("=" * 60)
    print("📋 This version skips Excel export for large datasets")
    print("📋 Focuses on CSV export for maximum speed")
    print("=" * 60)
    
    # Launch GUI in background
    def launch_gui():
        try:
            subprocess.run([
                "uv", "run", "python", "-c",
                "from frontend.main_window import main; main()"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ GUI launch failed: {e}")
        except Exception as e:
            print(f"⚠️ GUI launch error: {e}")
    
    gui_thread = threading.Thread(target=launch_gui, daemon=True)
    gui_thread.start()
    print("✅ GUI app launched in background")
    print("📱 You should see the Pete Data Cleaner app window open")
    print("📊 The dashboard will show real-time pipeline progress")
    time.sleep(3)  # Give GUI time to start
    
    pipeline_start = time.time()
    
    # Step 1: Load data
    print("\n📂 Step 1: Loading data...")
    load_start = time.time()
    
    try:
        # Use the same test file
        test_file = "data/raw/test_data_310k.csv"
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return False
        
        df = load_dataframe_ultra_fast(test_file)
        load_time = time.time() - load_start
        
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        print(f"⏱️  Load time: {load_time:.2f}s")
        print(f"📊 Speed: {len(df)/load_time:.0f} rows/sec")
        
        # Estimate total time
        file_size_mb = os.path.getsize(test_file) / 1024 / 1024
        estimated_total = estimate_total_pipeline_time(file_size_mb, len(df), len(df.columns))
        print(f"⏱️  Estimated total pipeline time: {estimated_total:.1f}s")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return False
    
    # Step 2: Clean data
    print("\n🧹 Step 2: Cleaning data...")
    clean_start = time.time()
    
    try:
        df_clean = clean_dataframe_ultra_fast(df)
        clean_time = time.time() - clean_start
        
        print(f"✅ Cleaned data: {len(df_clean):,} rows")
        print(f"⏱️  Clean time: {clean_time:.2f}s")
        print(f"📊 Speed: {len(df_clean)/clean_time:.0f} rows/sec")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to clean data: {e}")
        return False
    
    # Step 3: Filter empty columns
    print("\n🔍 Step 3: Filtering empty columns...")
    filter_start = time.time()
    
    try:
        df_filtered = filter_empty_columns_ultra_fast(df_clean)
        filter_time = time.time() - filter_start
        
        print(f"✅ Filtered data: {len(df_filtered):,} rows, {len(df_filtered.columns)} columns")
        print(f"⏱️  Filter time: {filter_time:.2f}s")
        print(f"📊 Speed: {len(df_filtered)/filter_time:.0f} rows/sec")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to filter data: {e}")
        return False
    
    # Step 4: Phone prioritization
    print("\n📱 Step 4: Phone prioritization...")
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
    
    # Step 5: Ultra-fast Owner Object analysis
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
            save_property_owners_persistent(owner_objects, df_enhanced, "ultra_fast_pipeline_fast")
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
    
    # Step 6: Mapping to Pete headers
    print("\n🎯 Step 6: Mapping to Pete headers...")
    mapping_start = time.time()
    
    try:
        # Convert back to pandas for mapping
        df_for_mapping = df_enhanced.to_pandas() if hasattr(df_enhanced, 'to_pandas') else df_enhanced
        
        # Initialize Pete header mapper
        mapper = PeteHeaderMapper()
        
        # Map to Pete headers
        df_mapped, mapping_info = mapper.map_to_pete_headers(df_for_mapping)
        mapping_time = time.time() - mapping_start
        
        print(f"✅ Mapped to Pete headers: {len(df_mapped):,} rows, {len(df_mapped.columns)} columns")
        print(f"⏱️  Mapping time: {mapping_time:.2f}s")
        print(f"📊 Speed: {len(df_mapped)/mapping_time:.0f} rows/sec")
        
        # Show mapping results
        mapped_columns = [col for col in df_mapped.columns if col in mapper.pete_headers]
        print(f"🎯 Mapped columns: {len(mapped_columns)}/{len(mapper.pete_headers)} Pete headers")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to map to Pete headers: {e}")
        return False
    
    # Step 7: Data standardization
    print("\n🔧 Step 7: Data standardization...")
    standardize_start = time.time()
    
    try:
        # Initialize data standardizer
        standardizer = DataStandardizerEnhanced()
        
        # Standardize the data
        df_standardized = standardizer.standardize_dataframe(df_mapped)
        standardize_time = time.time() - standardize_start
        
        print(f"✅ Standardized data: {len(df_standardized):,} rows")
        print(f"⏱️  Standardize time: {standardize_time:.2f}s")
        print(f"📊 Speed: {len(df_standardized)/standardize_time:.0f} rows/sec")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to standardize data: {e}")
        return False
    
    # Step 8: Save comprehensive preset
    print("\n💾 Step 8: Saving comprehensive preset...")
    preset_start = time.time()
    
    try:
        # Initialize preset manager
        preset_manager = PresetManager()
        
        # Create comprehensive preset
        preset_data = {
            'name': 'mark_carpenter_test_comprehensive_preset',
            'description': 'Comprehensive test preset with all features',
            'created_at': datetime.now().isoformat(),
            'data_info': {
                'total_rows': len(df_standardized),
                'total_columns': len(df_standardized.columns),
                'pete_headers_mapped': len([col for col in df_standardized.columns if col in mapper.pete_headers]),
                'owner_objects_created': len(owner_objects) if owner_objects else 0
            },
            'processing_config': {
                'prioritization_rules': prioritization_rules,
                'mapping_info': mapping_info,
                'standardization_applied': True
            }
        }
        
        # Save preset
        preset_id = preset_manager.save_preset(preset_data)
        preset_time = time.time() - preset_start
        
        print(f"✅ Saved comprehensive preset: {preset_id}")
        print(f"⏱️  Preset save time: {preset_time:.2f}s")
        
        log_system_status()
        
    except Exception as e:
        print(f"❌ Failed to save preset: {e}")
        return False
    
    # Step 9: Export final data (CSV ONLY for speed)
    print("\n📤 Step 9: Export final data (CSV ONLY for speed)...")
    export_start = time.time()
    
    # Create export directory
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_output_file = f"{export_dir}/pete_export_fast_{timestamp}.csv"
    
    print(f"📊 Exporting {len(df_standardized):,} records...")
    print(f"📁 CSV: {csv_output_file}")
    print(f"💡 Skipping Excel export for speed (large dataset)")
    
    try:
        # Export CSV only (fast)
        df_standardized.to_csv(csv_output_file, index=False)
        print(f"✅ Exported Pete-ready data (CSV): {csv_output_file}")
        
        # Export Owner Objects summary as CSV only
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
            owner_csv_file = f"{export_dir}/owner_objects_summary_fast_{timestamp}.csv"
            
            # Export CSV only
            owner_summary_df.to_csv(owner_csv_file, index=False)
            print(f"✅ Exported Owner Objects summary (CSV): {owner_csv_file}")
        
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
    print(f"   Owners: {actual_analysis_time:.2f}s")
    print(f"   Mapping: {mapping_time:.2f}s")
    print(f"   Standardize: {standardize_time:.2f}s")
    print(f"   Preset: {preset_time:.2f}s")
    print(f"   Export: {export_time:.2f}s")
    
    print(f"\n🚀 SPEED IMPROVEMENTS:")
    print(f"   • CSV-only export: {export_time:.2f}s (vs 60s+ for Excel)")
    print(f"   • Total pipeline: {total_time:.2f}s (vs 4+ hours before)")
    print(f"   • Speed improvement: {240*60/total_time:.0f}x faster!")
    
    print(f"\n📁 Output files:")
    print(f"   • Pete-ready data: {csv_output_file}")
    if owner_objects:
        print(f"   • Owner Objects summary: {owner_csv_file}")
    
    print(f"\n✅ Pipeline completed successfully!")
    return True

if __name__ == "__main__":
    test_ultra_fast_pipeline_fast() 