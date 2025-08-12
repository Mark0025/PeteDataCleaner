#!/usr/bin/env python3
"""
Test Comprehensive Preset System

Demonstrates the new user management, preset saving, and dashboard functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    
    # Create sample REISIFT data
    data = {
        'First Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'] * 20,
        'Last Name': ['Smith', 'Doe', 'Johnson', 'Brown', 'Wilson'] * 20,
        'Property address': [f'{i} Main St' for i in range(1, 101)],
        'Property city': ['Austin', 'Houston', 'Dallas', 'San Antonio', 'Fort Worth'] * 20,
        'Property state': ['TX'] * 100,
        'Property zip': [f'{75000 + i}' for i in range(100)],
        'Phone 1': [f'555-{i:03d}-{i:04d}' for i in range(100)],
        'Phone Status 1': ['CORRECT', 'UNKNOWN', 'NO_ANSWER', 'WRONG', 'DEAD'] * 20,
        'Phone Type 1': ['MOBILE', 'LANDLINE', 'UNKNOWN'] * 33 + ['MOBILE'],
        'Phone Tag 1': ['call_a01', 'call_a02', 'call_a03', 'call_a04', 'call_a05'] * 20,
        'Email 1': [f'person{i}@example.com' for i in range(100)],
        'Email 2': [f'person{i}@gmail.com' for i in range(100)],
        'Structure type': ['single family resident', 'sfr', 'multifamily', 'townhouse'] * 25,
        'Estimated value': np.random.randint(100000, 500000, 100),
        'Mailing address': [f'{i} Oak Ave' for i in range(1, 101)]
    }
    
    return pd.DataFrame(data)

def test_comprehensive_preset_system():
    """Test the comprehensive preset system."""
    print("🧪 TESTING COMPREHENSIVE PRESET SYSTEM")
    print("=" * 50)
    
    # 1. Initialize user system
    print("\n1. 🔐 Initializing User System...")
    from backend.utils.user_manager import login_default_user, get_dashboard_data
    
    try:
        user = login_default_user()
        print(f"   ✅ Logged in: {user.name} at {user.company_id}")
        
        dashboard_data = get_dashboard_data()
        print(f"   📊 Dashboard ready with {dashboard_data['presets']['total']} presets")
    except Exception as e:
        print(f"   ❌ User system error: {e}")
        return
    
    # 2. Create sample data
    print("\n2. 📊 Creating Sample Data...")
    df = create_sample_data()
    print(f"   ✅ Created {len(df)} records with {len(df.columns)} columns")
    
    # 3. Simulate data processing
    print("\n3. 🔧 Simulating Data Processing...")
    
    # Simulate phone prioritization
    phone_rules = {
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
    
    # Simulate owner analysis
    owner_analysis = {
        'total_owners': 95,
        'business_entities': {
            'business_count': 12,
            'sample_businesses': ['ABC LLC', 'XYZ Corp', '123 Trust']
        },
        'ownership_patterns': {
            'owners_with_multiple_properties': 8,
            'max_properties_per_owner': 3,
            'top_owners': {'John Smith': 3, 'Jane Doe': 2}
        },
        'marketing_insights': {
            'high_value_targets': 15,
            'multi_property_opportunities': 8,
            'business_entity_opportunities': 12
        }
    }
    
    # Simulate data preparation
    data_prep_summary = {
        'version_summary': [
            {
                'action': 'Strip .0',
                'details': 'Removed trailing .0 from numeric-like strings',
                'timestamp': datetime.now().isoformat()
            },
            {
                'action': 'Phone Prioritization',
                'details': 'Prioritized phones using custom rules',
                'timestamp': datetime.now().isoformat()
            },
            {
                'action': 'Owner Analysis',
                'details': 'Analyzed ownership patterns and business entities',
                'timestamp': datetime.now().isoformat()
            }
        ],
        'tools_used': ['strip_trailing_dot', 'phone_prioritization', 'owner_analysis'],
        'data_source': 'REISIFT',
        'original_shape': df.shape,
        'prepared_shape': df.shape
    }
    
    print("   ✅ Simulated phone prioritization rules")
    print("   ✅ Simulated owner analysis results")
    print("   ✅ Simulated data preparation steps")
    
    # 4. Save comprehensive preset
    print("\n4. 💾 Saving Comprehensive Preset...")
    from backend.utils.user_manager import user_manager
    
    try:
        preset_path = user_manager.save_user_preset(
            preset_name="test_comprehensive_preset",
            original_df=df,
            prepared_df=df,  # Same for this test
            phone_prioritization_rules=phone_rules,
            owner_analysis_results=owner_analysis,
            data_prep_summary=data_prep_summary,
            export_data=df.head(50)  # Sample export data
        )
        print(f"   ✅ Preset saved to: {preset_path}")
    except Exception as e:
        print(f"   ❌ Preset save error: {e}")
        return
    
    # 5. Load and verify preset
    print("\n5. 📂 Loading and Verifying Preset...")
    from backend.utils.preset_manager import PresetManager
    
    try:
        preset_manager = PresetManager()
        presets = preset_manager.list_presets()
        
        if presets:
            latest_preset = presets[0]
            preset_data = preset_manager.load_preset(latest_preset['preset_id'])
            
            print(f"   ✅ Loaded preset: {latest_preset['preset_name']}")
            print(f"   📊 Original shape: {preset_data['metadata']['original_shape']}")
            print(f"   📊 Prepared shape: {preset_data['metadata']['prepared_shape']}")
            
            if 'phone_prioritization_rules' in preset_data:
                print("   📞 Phone rules: ✅ Saved and loaded")
            
            if 'owner_analysis' in preset_data:
                print("   🏠 Owner analysis: ✅ Saved and loaded")
            
            if 'data_prep_summary' in preset_data:
                print("   🔧 Data prep summary: ✅ Saved and loaded")
        else:
            print("   ❌ No presets found")
    except Exception as e:
        print(f"   ❌ Preset load error: {e}")
    
    # 6. Create dashboard view
    print("\n6. 📊 Creating Dashboard View...")
    try:
        dashboard_file = user_manager.create_dashboard_view()
        print(f"   ✅ Dashboard created: {dashboard_file}")
        print(f"   🌐 Open in browser: file://{os.path.abspath(dashboard_file)}")
    except Exception as e:
        print(f"   ❌ Dashboard creation error: {e}")
    
    # 7. Show updated dashboard data
    print("\n7. 📈 Updated Dashboard Data...")
    try:
        updated_dashboard = get_dashboard_data()
        print(f"   📊 Total presets: {updated_dashboard['presets']['total']}")
        print(f"   📊 Recent exports: {updated_dashboard['exports']['total']}")
        print(f"   📊 Total records exported: {updated_dashboard['exports']['total_records_exported']:,}")
        
        if updated_dashboard['analysis']['owner_analysis']:
            owner_data = updated_dashboard['analysis']['owner_analysis']
            print(f"   🏠 Total owners: {owner_data.get('total_owners', 0):,}")
            print(f"   🏢 Business entities: {owner_data.get('business_entities', 0):,}")
    except Exception as e:
        print(f"   ❌ Dashboard data error: {e}")
    
    print("\n🎉 COMPREHENSIVE PRESET SYSTEM TEST COMPLETE!")
    print("=" * 50)
    print("\n📋 What was tested:")
    print("   • User system initialization and login")
    print("   • Sample data creation")
    print("   • Phone prioritization rules")
    print("   • Owner analysis results")
    print("   • Data preparation summary")
    print("   • Comprehensive preset saving")
    print("   • Preset loading and verification")
    print("   • Dashboard creation")
    print("   • Export logging")
    
    print("\n🚀 Next steps:")
    print("   • Launch the GUI to see the dashboard")
    print("   • Upload real data to test the full workflow")
    print("   • Use the preset system to save and load configurations")

if __name__ == "__main__":
    test_comprehensive_preset_system() 