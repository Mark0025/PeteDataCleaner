#!/usr/bin/env python3
"""
Quick test to verify preset saving functionality works.
"""

import pandas as pd
from datetime import datetime
from backend.utils.preset_manager import PresetManager

def test_preset_save():
    """Test preset saving with sample data."""
    
    print("🧪 Testing Preset Save Functionality")
    print("=" * 50)
    
    try:
        # Create sample data (similar to what we processed)
        sample_data = {
            'Seller 1': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'Property Address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
            'Property Value': [100000, 150000, 200000],
            'Phone 1': ['555-1234', '555-5678', '555-9012']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create preset manager
        preset_manager = PresetManager()
        
        # Test saving comprehensive preset
        preset_name = f"test_preset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"📝 Saving preset: {preset_name}")
        
        preset_path = preset_manager.save_comprehensive_preset(
            preset_name=preset_name,
            data_source="TEST",
            original_df=df,
            prepared_df=df,
            phone_prioritization_rules={
                'status_weights': {'CORRECT': 100, 'UNKNOWN': 80},
                'type_weights': {'MOBILE': 100, 'LANDLINE': 80}
            },
            owner_analysis_results={
                'total_owners': 3,
                'individual_only': 3,
                'business_only': 0
            },
            data_prep_summary={
                'version_summary': [
                    {'action': 'Test Load', 'timestamp': datetime.now().isoformat()},
                    {'action': 'Test Process', 'timestamp': datetime.now().isoformat()}
                ],
                'tools_used': ['test_tools'],
                'data_source': 'TEST',
                'original_shape': df.shape,
                'prepared_shape': df.shape
            },
            export_data=df
        )
        
        print(f"✅ Preset saved successfully!")
        print(f"📁 Location: {preset_path}")
        
        # Test loading the preset
        print("\n📂 Testing preset loading...")
        # The actual preset ID includes timestamp, so we need to list presets first
        presets = preset_manager.list_presets()
        if presets:
            latest_preset_id = presets[0]['preset_id']
            loaded_preset = preset_manager.load_preset(latest_preset_id)
        else:
            print("❌ No presets found to load")
            return False
        
        print(f"✅ Preset loaded successfully!")
        print(f"📊 Metadata: {loaded_preset['metadata']['preset_name']}")
        print(f"📊 Original shape: {loaded_preset['metadata']['original_shape']}")
        print(f"📊 Prepared shape: {loaded_preset['metadata']['prepared_shape']}")
        
        if 'phone_prioritization_rules' in loaded_preset:
            print("📞 Phone rules: ✅ Loaded")
        
        if 'owner_analysis' in loaded_preset:
            print("🏠 Owner analysis: ✅ Loaded")
        
        if 'data_prep_summary' in loaded_preset:
            print("🔧 Data prep summary: ✅ Loaded")
        
        print(f"\n🎉 Preset save/load test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Preset test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_preset_save() 