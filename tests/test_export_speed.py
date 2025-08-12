#!/usr/bin/env python3
"""
Export Speed Test

Test different export methods to demonstrate speed improvements.
"""

import time
import pandas as pd
import polars as pl
from datetime import datetime
import os

def test_export_speeds():
    """Test different export methods and show speed comparisons."""
    
    print("🚀 EXPORT SPEED TEST")
    print("=" * 50)
    
    # Create a sample dataset (similar to your real data)
    print("📊 Creating test dataset...")
    
    # Generate sample data similar to your property data
    num_rows = 50000  # Smaller for quick test, but still significant
    
    sample_data = {
        'Property Address': [f"123 Test St #{i}" for i in range(num_rows)],
        'Property Value': [100000 + (i * 1000) for i in range(num_rows)],
        'Seller 1': [f"Owner {i}" for i in range(num_rows)],
        'Phone 1': [f"555-{i:04d}" for i in range(num_rows)],
        'Phone 2': [f"555-{i+1000:04d}" for i in range(num_rows)],
        'Phone 3': [f"555-{i+2000:04d}" for i in range(num_rows)],
        'Skip_Trace_Target': [f"Target {i}" for i in range(num_rows)],
        'Owner_Confidence': [0.8 + (i % 20) / 100 for i in range(num_rows)],
        'Property_Count': [1 + (i % 5) for i in range(num_rows)],
        'Owner_Type': ['Individual Only' if i % 3 == 0 else 'Business Only' if i % 3 == 1 else 'Individual + Business' for i in range(num_rows)]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    print(f"✅ Created test dataset: {len(df):,} rows, {len(df.columns)} columns")
    print(f"📊 Dataset size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
    
    # Create export directory
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("\n" + "=" * 50)
    print("📤 EXPORT SPEED TESTS")
    print("=" * 50)
    
    # Test 1: CSV Export (baseline - should be fast)
    print("\n1️⃣ CSV Export Test")
    csv_file = f"{export_dir}/speed_test_csv_{timestamp}.csv"
    
    start_time = time.time()
    df.to_csv(csv_file, index=False)
    csv_time = time.time() - start_time
    
    print(f"✅ CSV Export: {csv_time:.2f}s")
    print(f"📈 Speed: {len(df)/csv_time:.0f} rows/sec")
    
    # Test 2: Excel with openpyxl (slow method)
    print("\n2️⃣ Excel Export with openpyxl (SLOW)")
    excel_openpyxl_file = f"{export_dir}/speed_test_openpyxl_{timestamp}.xlsx"
    
    start_time = time.time()
    try:
        df.to_excel(excel_openpyxl_file, index=False, engine='openpyxl')
        openpyxl_time = time.time() - start_time
        print(f"✅ openpyxl Export: {openpyxl_time:.2f}s")
        print(f"📈 Speed: {len(df)/openpyxl_time:.0f} rows/sec")
        print(f"🐌 {openpyxl_time/csv_time:.1f}x slower than CSV")
    except Exception as e:
        print(f"❌ openpyxl failed: {e}")
        openpyxl_time = float('inf')
    
    # Test 3: Excel with xlsxwriter (fast method)
    print("\n3️⃣ Excel Export with xlsxwriter (FAST)")
    excel_xlsxwriter_file = f"{export_dir}/speed_test_xlsxwriter_{timestamp}.xlsx"
    
    start_time = time.time()
    try:
        df.to_excel(excel_xlsxwriter_file, index=False, engine='xlsxwriter')
        xlsxwriter_time = time.time() - start_time
        print(f"✅ xlsxwriter Export: {xlsxwriter_time:.2f}s")
        print(f"📈 Speed: {len(df)/xlsxwriter_time:.0f} rows/sec")
        print(f"⚡ {csv_time/xlsxwriter_time:.1f}x faster than CSV")
        if openpyxl_time != float('inf'):
            print(f"🚀 {openpyxl_time/xlsxwriter_time:.1f}x faster than openpyxl")
    except Exception as e:
        print(f"❌ xlsxwriter failed: {e}")
        xlsxwriter_time = float('inf')
    
    # Test 4: Polars CSV Export (for comparison)
    print("\n4️⃣ Polars CSV Export (for comparison)")
    df_polars = pl.from_pandas(df)
    polars_csv_file = f"{export_dir}/speed_test_polars_{timestamp}.csv"
    
    start_time = time.time()
    df_polars.write_csv(polars_csv_file)
    polars_time = time.time() - start_time
    
    print(f"✅ Polars CSV Export: {polars_time:.2f}s")
    print(f"📈 Speed: {len(df)/polars_time:.0f} rows/sec")
    print(f"⚡ {csv_time/polars_time:.1f}x faster than Pandas CSV")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 EXPORT SPEED SUMMARY")
    print("=" * 50)
    
    print(f"Dataset: {len(df):,} rows, {len(df.columns)} columns")
    print(f"File sizes:")
    
    # Check file sizes
    if os.path.exists(csv_file):
        csv_size = os.path.getsize(csv_file) / 1024 / 1024
        print(f"  CSV: {csv_size:.1f} MB")
    
    if os.path.exists(excel_openpyxl_file):
        openpyxl_size = os.path.getsize(excel_openpyxl_file) / 1024 / 1024
        print(f"  Excel (openpyxl): {openpyxl_size:.1f} MB")
    
    if os.path.exists(excel_xlsxwriter_file):
        xlsxwriter_size = os.path.getsize(excel_xlsxwriter_file) / 1024 / 1024
        print(f"  Excel (xlsxwriter): {xlsxwriter_size:.1f} MB")
    
    if os.path.exists(polars_csv_file):
        polars_size = os.path.getsize(polars_csv_file) / 1024 / 1024
        print(f"  Polars CSV: {polars_size:.1f} MB")
    
    print(f"\nSpeed Rankings (fastest to slowest):")
    
    # Create speed comparison
    speeds = [
        ("Polars CSV", polars_time),
        ("Pandas CSV", csv_time),
        ("xlsxwriter Excel", xlsxwriter_time if xlsxwriter_time != float('inf') else None),
        ("openpyxl Excel", openpyxl_time if openpyxl_time != float('inf') else None)
    ]
    
    # Sort by time (fastest first)
    speeds = [(name, time) for name, time in speeds if time is not None]
    speeds.sort(key=lambda x: x[1])
    
    for i, (name, time_taken) in enumerate(speeds, 1):
        print(f"  {i}. {name}: {time_taken:.2f}s ({len(df)/time_taken:.0f} rows/sec)")
    
    # Calculate improvements
    if len(speeds) >= 2:
        fastest = speeds[0][1]
        slowest = speeds[-1][1]
        improvement = slowest / fastest
        print(f"\n🚀 Speed Improvement: {improvement:.1f}x faster with {speeds[0][0]} vs {speeds[-1][0]}")
    
    print(f"\n💡 Recommendations:")
    print(f"  • Use CSV for fastest export")
    print(f"  • Use xlsxwriter for Excel (much faster than openpyxl)")
    print(f"  • Skip Excel for datasets > 50K rows")
    print(f"  • Use Polars for processing, Pandas for export")

if __name__ == "__main__":
    test_export_speeds() 