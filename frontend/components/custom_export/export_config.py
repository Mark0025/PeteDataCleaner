#!/usr/bin/env python3
"""
Export Configuration System

Defines export presets and configurations for different use cases:
- Pete CRM Export (default)
- Investor Analysis Export
- Custom Export
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ExportPreset:
    """Export preset configuration."""
    name: str
    description: str
    headers: List[str]
    filters: Dict[str, Any]
    format: str = "csv"
    include_metadata: bool = True


class ExportConfig:
    """Export configuration manager."""
    
    def __init__(self):
        self.presets = self._load_default_presets()
        self.custom_presets = self._load_custom_presets()
    
    def _load_default_presets(self) -> Dict[str, ExportPreset]:
        """Load default export presets."""
        return {
            'pete': ExportPreset(
                name="Pete CRM Export",
                description="Standard export for Pete CRM integration with prioritized phones",
                headers=[
                    'Property Address',
                    'Mailing Address', 
                    'Owner Name',
                    'Phone 1',
                    'Phone 2',
                    'Phone 3',
                    'Phone 4'
                ],
                filters={
                    'include_pete_prioritized': True,
                    'include_original_phones': False,
                    'include_phone_metadata': False
                },
                format="csv",
                include_metadata=False
            ),
            
            'investor': ExportPreset(
                name="Investor Analysis",
                description="Comprehensive analysis for investment decisions with all phone data",
                headers=[
                    'Property Address',
                    'Mailing Address',
                    'Owner Name',
                    'Owner Type',
                    'Phone 1 (Pete)',
                    'Phone 2 (Pete)', 
                    'Phone 3 (Pete)',
                    'Phone 4 (Pete)',
                    'Phone 5 (Original)',
                    'Phone 6 (Original)',
                    'Phone 7 (Original)',
                    'Phone 8 (Original)',
                    'Phone Status 1',
                    'Phone Status 2',
                    'Phone Status 3',
                    'Phone Status 4',
                    'Phone Type 1',
                    'Phone Type 2',
                    'Phone Type 3',
                    'Phone Type 4',
                    'Phone Tags 1',
                    'Phone Tags 2',
                    'Phone Tags 3',
                    'Phone Tags 4',
                    'Phone Quality Score',
                    'Best Contact Method',
                    'Skip Trace Target',
                    'Property Count',
                    'Total Property Value',
                    'LLC Analysis',
                    'Contact Quality'
                ],
                filters={
                    'include_pete_prioritized': True,
                    'include_original_phones': True,
                    'include_phone_metadata': True,
                    'include_analysis': True
                },
                format="excel",
                include_metadata=True
            ),
            
            'skip_trace': ExportPreset(
                name="Skip Trace Targets",
                description="High-quality skip trace opportunities with verified contact info",
                headers=[
                    'Property Address',
                    'Mailing Address',
                    'Owner Name',
                    'Best Phone Number',
                    'Phone Status',
                    'Phone Type',
                    'Phone Quality Score',
                    'Skip Trace Target',
                    'Contact Quality',
                    'Property Count',
                    'Total Property Value'
                ],
                filters={
                    'include_pete_prioritized': False,
                    'include_original_phones': False,
                    'include_phone_metadata': True,
                    'include_analysis': True,
                    'min_phone_quality': 0.7,
                    'phone_status_filter': ['CORRECT', 'UNKNOWN']
                },
                format="csv",
                include_metadata=True
            ),
            
            'llc_analysis': ExportPreset(
                name="LLC Analysis",
                description="Business entity analysis with contact information",
                headers=[
                    'Property Address',
                    'Mailing Address',
                    'Business Name',
                    'Business Type',
                    'Contact Person',
                    'Best Phone Number',
                    'Phone Status',
                    'Contact Quality',
                    'Property Count',
                    'Total Property Value',
                    'LLC Analysis'
                ],
                filters={
                    'include_pete_prioritized': False,
                    'include_original_phones': False,
                    'include_phone_metadata': True,
                    'include_analysis': True,
                    'owner_type_filter': ['Business']
                },
                format="excel",
                include_metadata=True
            ),
            
            'custom': ExportPreset(
                name="Custom Export",
                description="User-defined header selection",
                headers=[],
                filters={},
                format="csv",
                include_metadata=False
            )
        }
    
    def _load_custom_presets(self) -> Dict[str, ExportPreset]:
        """Load custom presets from file."""
        custom_presets_file = Path("data/users/preferences/custom_export_presets.json")
        
        if custom_presets_file.exists():
            try:
                with open(custom_presets_file, 'r') as f:
                    data = json.load(f)
                
                custom_presets = {}
                for key, preset_data in data.items():
                    custom_presets[key] = ExportPreset(**preset_data)
                
                return custom_presets
            except Exception as e:
                print(f"Warning: Could not load custom presets: {e}")
        
        return {}
    
    def save_custom_preset(self, name: str, preset: ExportPreset) -> bool:
        """Save a custom export preset."""
        try:
            # Add to custom presets
            self.custom_presets[name] = preset
            
            # Save to file
            custom_presets_file = Path("data/users/preferences/custom_export_presets.json")
            custom_presets_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict for JSON serialization
            preset_dict = {
                'name': preset.name,
                'description': preset.description,
                'headers': preset.headers,
                'filters': preset.filters,
                'format': preset.format,
                'include_metadata': preset.include_metadata
            }
            
            # Load existing presets
            existing_presets = {}
            if custom_presets_file.exists():
                with open(custom_presets_file, 'r') as f:
                    existing_presets = json.load(f)
            
            # Add new preset
            existing_presets[name] = preset_dict
            
            # Save back to file
            with open(custom_presets_file, 'w') as f:
                json.dump(existing_presets, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving custom preset: {e}")
            return False
    
    def get_preset(self, preset_name: str) -> Optional[ExportPreset]:
        """Get a preset by name."""
        # Check default presets first
        if preset_name in self.presets:
            return self.presets[preset_name]
        
        # Check custom presets
        if preset_name in self.custom_presets:
            return self.custom_presets[preset_name]
        
        return None
    
    def list_presets(self) -> Dict[str, ExportPreset]:
        """List all available presets."""
        all_presets = {}
        all_presets.update(self.presets)
        all_presets.update(self.custom_presets)
        return all_presets
    
    def get_available_headers(self) -> List[str]:
        """Get list of all available headers for selection."""
        return [
            # Core property data
            'Property Address',
            'Mailing Address',
            'Property Value',
            'Property Type',
            
            # Owner information
            'Owner Name',
            'First Name',
            'Last Name',
            'Owner Type',
            'Business Name',
            
            # Pete prioritized phones
            'Phone 1 (Pete)',
            'Phone 2 (Pete)',
            'Phone 3 (Pete)',
            'Phone 4 (Pete)',
            
            # Original phones (up to 30)
            'Phone 5 (Original)',
            'Phone 6 (Original)',
            'Phone 7 (Original)',
            'Phone 8 (Original)',
            'Phone 9 (Original)',
            'Phone 10 (Original)',
            
            # Phone metadata
            'Phone Status 1',
            'Phone Status 2',
            'Phone Status 3',
            'Phone Status 4',
            'Phone Type 1',
            'Phone Type 2',
            'Phone Type 3',
            'Phone Type 4',
            'Phone Tags 1',
            'Phone Tags 2',
            'Phone Tags 3',
            'Phone Tags 4',
            
            # Analysis data
            'Phone Quality Score',
            'Best Contact Method',
            'Skip Trace Target',
            'Property Count',
            'Total Property Value',
            'LLC Analysis',
            'Contact Quality',
            'Confidence Score',
            
            # Additional metadata
            'Tags',
            'Status',
            'Notes'
        ]
    
    def get_header_categories(self) -> Dict[str, List[str]]:
        """Get headers organized by category."""
        return {
            'Property Data': [
                'Property Address',
                'Mailing Address',
                'Property Value',
                'Property Type'
            ],
            'Owner Information': [
                'Owner Name',
                'First Name',
                'Last Name',
                'Owner Type',
                'Business Name'
            ],
            'Pete Phones': [
                'Phone 1 (Pete)',
                'Phone 2 (Pete)',
                'Phone 3 (Pete)',
                'Phone 4 (Pete)'
            ],
            'Original Phones': [
                'Phone 5 (Original)',
                'Phone 6 (Original)',
                'Phone 7 (Original)',
                'Phone 8 (Original)',
                'Phone 9 (Original)',
                'Phone 10 (Original)'
            ],
            'Phone Metadata': [
                'Phone Status 1',
                'Phone Status 2',
                'Phone Status 3',
                'Phone Status 4',
                'Phone Type 1',
                'Phone Type 2',
                'Phone Type 3',
                'Phone Type 4',
                'Phone Tags 1',
                'Phone Tags 2',
                'Phone Tags 3',
                'Phone Tags 4'
            ],
            'Analysis': [
                'Phone Quality Score',
                'Best Contact Method',
                'Skip Trace Target',
                'Property Count',
                'Total Property Value',
                'LLC Analysis',
                'Contact Quality',
                'Confidence Score'
            ],
            'Additional': [
                'Tags',
                'Status',
                'Notes'
            ]
        }


def test_export_config():
    """Test the export configuration system."""
    print("🧪 Testing Export Configuration System")
    print("=" * 50)
    
    config = ExportConfig()
    
    # Test preset loading
    print("📋 Available Presets:")
    for name, preset in config.list_presets().items():
        print(f"  {name}: {preset.name} - {preset.description}")
        print(f"    Headers: {len(preset.headers)}")
        print(f"    Format: {preset.format}")
        print()
    
    # Test header categories
    print("📊 Header Categories:")
    categories = config.get_header_categories()
    for category, headers in categories.items():
        print(f"  {category}: {len(headers)} headers")
    
    # Test preset retrieval
    print("\n🔍 Testing Preset Retrieval:")
    pete_preset = config.get_preset('pete')
    if pete_preset:
        print(f"✅ Pete preset loaded: {pete_preset.name}")
        print(f"   Headers: {pete_preset.headers}")
    
    # Test custom preset saving
    print("\n💾 Testing Custom Preset Saving:")
    custom_preset = ExportPreset(
        name="Test Custom Preset",
        description="Test custom preset",
        headers=['Property Address', 'Owner Name', 'Phone 1'],
        filters={'test': True},
        format="csv"
    )
    
    success = config.save_custom_preset('test_custom', custom_preset)
    print(f"   Save result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test custom preset loading
    loaded_preset = config.get_preset('test_custom')
    if loaded_preset:
        print(f"   Load result: ✅ Success - {loaded_preset.name}")
    
    print("\n✅ Export configuration system test complete!")


if __name__ == "__main__":
    test_export_config() 