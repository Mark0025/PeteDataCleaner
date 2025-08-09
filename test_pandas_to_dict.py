#!/usr/bin/env python3
"""
Test to figure out correct pandas to_dict() syntax
"""

import pandas as pd

# Create test DataFrame
df = pd.DataFrame({
    'name': ['John', 'Jane', 'Bob'],
    'value': [100, 200, 300],
    'count': [1, 2, 3]
})

print("🧪 Testing pandas to_dict() syntax...")
print(f"DataFrame: {df}")

# Test different syntaxes
try:
    print("\n1. Testing to_dict() with no arguments:")
    result1 = df.to_dict()
    print(f"✅ Success: {type(result1)}")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n2. Testing to_dict('records'):")
    result2 = df.to_dict('records')
    print(f"✅ Success: {type(result2)}")
    print(f"   Result: {result2}")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n3. Testing to_dict(orient='records'):")
    result3 = df.to_dict(orient='records')
    print(f"✅ Success: {type(result3)}")
    print(f"   Result: {result3}")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n4. Testing to_dict('list'):")
    result4 = df.to_dict('list')
    print(f"✅ Success: {type(result4)}")
    print(f"   Result: {result4}")
except Exception as e:
    print(f"❌ Failed: {e}")

print(f"\n📊 Pandas version: {pd.__version__}") 