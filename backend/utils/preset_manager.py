#!/usr/bin/env python3
"""
Preset Manager - Comprehensive Data Export and Reference System

Saves all analysis data, phone prioritization rules, owner insights, and export logs
for future reference and reproducibility.
"""

import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import shutil


class PresetManager:
    """
    Comprehensive preset manager for saving and referencing data analysis results.
    
    Features:
    - Save phone prioritization rules and results
    - Save owner analysis insights
    - Create export logs with timestamps
    - Generate reference views for data exploration
    - Track all data transformations and configurations
    """
    
    def __init__(self, base_dir: str = "DEV_MAN/presets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.presets_dir = self.base_dir / "saved_presets"
        self.exports_dir = self.base_dir / "exports"
        self.logs_dir = self.base_dir / "logs"
        self.views_dir = self.base_dir / "views"
        
        for dir_path in [self.presets_dir, self.exports_dir, self.logs_dir, self.views_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def save_comprehensive_preset(self, 
                                preset_name: str,
                                data_source: str,
                                original_df: pd.DataFrame,
                                prepared_df: pd.DataFrame,
                                phone_prioritization_rules: Optional[Dict] = None,
                                owner_analysis_results: Optional[Dict] = None,
                                data_prep_summary: Optional[Dict] = None,
                                export_data: Optional[pd.DataFrame] = None) -> str:
        """
        Save a comprehensive preset with all analysis data and configurations.
        
        Args:
            preset_name: Name for the preset
            data_source: Source of the data (e.g., "REISIFT")
            original_df: Original data before processing
            prepared_df: Data after all transformations
            phone_prioritization_rules: Custom phone prioritization rules
            owner_analysis_results: Owner analysis results
            data_prep_summary: Summary of data preparation steps
            export_data: Final export data for Pete
            
        Returns:
            Path to saved preset directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        preset_id = f"{preset_name}_{timestamp}"
        preset_dir = self.presets_dir / preset_id
        preset_dir.mkdir(exist_ok=True)
        
        logger.info(f"💾 Saving comprehensive preset: {preset_id}")
        
        # 1. Save preset metadata
        metadata = {
            'preset_name': preset_name,
            'preset_id': preset_id,
            'data_source': data_source,
            'created_at': datetime.now().isoformat(),
            'original_shape': original_df.shape,
            'prepared_shape': prepared_df.shape,
            'export_shape': export_data.shape if export_data is not None else None,
            'summary': {
                'total_records': len(original_df),
                'total_columns': len(original_df.columns),
                'prepared_records': len(prepared_df),
                'prepared_columns': len(prepared_df.columns),
                'export_records': len(export_data) if export_data is not None else 0,
                'export_columns': len(export_data.columns) if export_data is not None else 0
            }
        }
        
        with open(preset_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # 2. Save phone prioritization rules
        if phone_prioritization_rules:
            with open(preset_dir / "phone_prioritization_rules.json", 'w') as f:
                json.dump(phone_prioritization_rules, f, indent=2)
        
        # 3. Save owner analysis results
        if owner_analysis_results:
            with open(preset_dir / "owner_analysis.json", 'w') as f:
                json.dump(owner_analysis_results, f, indent=2, default=str)
        
        # 4. Save data preparation summary
        if data_prep_summary:
            with open(preset_dir / "data_prep_summary.json", 'w') as f:
                json.dump(data_prep_summary, f, indent=2, default=str)
        
        # 5. Save data samples (first 1000 rows for reference)
        original_sample = original_df.head(1000)
        prepared_sample = prepared_df.head(1000)
        
        original_sample.to_csv(preset_dir / "original_data_sample.csv", index=False)
        prepared_sample.to_csv(preset_dir / "prepared_data_sample.csv", index=False)
        
        if export_data is not None:
            export_sample = export_data.head(1000)
            export_sample.to_csv(preset_dir / "export_data_sample.csv", index=False)
        
        # 6. Create reference views
        self._create_reference_views(preset_dir, original_df, prepared_df, export_data)
        
        # 7. Generate comprehensive report
        report = self._generate_preset_report(metadata, phone_prioritization_rules, 
                                            owner_analysis_results, data_prep_summary)
        
        with open(preset_dir / "preset_report.md", 'w') as f:
            f.write(report)
        
        # 8. Save export log
        self._save_export_log(preset_id, metadata, export_data)
        
        logger.info(f"✅ Comprehensive preset saved: {preset_dir}")
        return str(preset_dir)
    
    def _create_reference_views(self, preset_dir: Path, original_df: pd.DataFrame, 
                               prepared_df: pd.DataFrame, export_data: Optional[pd.DataFrame]):
        """Create reference views for data exploration."""
        
        # Create column comparison view
        column_comparison = {
            'original_columns': list(original_df.columns),
            'prepared_columns': list(prepared_df.columns),
            'export_columns': list(export_data.columns) if export_data is not None else [],
            'removed_columns': list(set(original_df.columns) - set(prepared_df.columns)),
            'added_columns': list(set(prepared_df.columns) - set(original_df.columns))
        }
        
        with open(preset_dir / "column_comparison.json", 'w') as f:
            json.dump(column_comparison, f, indent=2)
        
        # Create data quality view
        data_quality = {
            'original_data_quality': {
                'null_counts': original_df.isnull().sum().to_dict(),
                'duplicate_rows': original_df.duplicated().sum(),
                'unique_values_per_column': {col: original_df[col].nunique() for col in original_df.columns[:20]}
            },
            'prepared_data_quality': {
                'null_counts': prepared_df.isnull().sum().to_dict(),
                'duplicate_rows': prepared_df.duplicated().sum(),
                'unique_values_per_column': {col: prepared_df[col].nunique() for col in prepared_df.columns[:20]}
            }
        }
        
        with open(preset_dir / "data_quality.json", 'w') as f:
            json.dump(data_quality, f, indent=2, default=str)
    
    def _generate_preset_report(self, metadata: Dict, phone_rules: Optional[Dict], 
                               owner_analysis: Optional[Dict], data_prep: Optional[Dict]) -> str:
        """Generate a comprehensive markdown report for the preset."""
        
        report_lines = [
            f"# 📊 Data Processing Preset Report",
            f"**Preset Name:** {metadata['preset_name']}",
            f"**Preset ID:** {metadata['preset_id']}",
            f"**Data Source:** {metadata['data_source']}",
            f"**Created:** {metadata['created_at']}",
            "",
            "## 📈 Data Summary",
            f"- **Original Data:** {metadata['original_shape'][0]:,} rows × {metadata['original_shape'][1]} columns",
            f"- **Prepared Data:** {metadata['prepared_shape'][0]:,} rows × {metadata['prepared_shape'][1]} columns",
            f"- **Export Data:** {metadata['export_shape'][0]:,} rows × {metadata['export_shape'][1]} columns" if metadata['export_shape'] else "- **Export Data:** Not available",
            "",
            "## 📞 Phone Prioritization",
        ]
        
        if phone_rules:
            report_lines.extend([
                "### Status Weights:",
                "```json",
                json.dumps(phone_rules.get('status_weights', {}), indent=2),
                "```",
                "",
                "### Type Weights:",
                "```json",
                json.dumps(phone_rules.get('type_weights', {}), indent=2),
                "```",
                "",
                "### Tag Weights:",
                "```json",
                json.dumps(phone_rules.get('tag_weights', {}), indent=2),
                "```",
                ""
            ])
        else:
            report_lines.append("No custom phone prioritization rules applied.")
        
        report_lines.append("## 🏠 Owner Analysis")
        
        if owner_analysis:
            report_lines.extend([
                f"- **Total Owners:** {owner_analysis.get('total_owners', 0):,}",
                f"- **Business Entities:** {owner_analysis.get('business_entities', {}).get('business_count', 0):,}",
                f"- **Multi-Property Owners:** {owner_analysis.get('ownership_patterns', {}).get('owners_with_multiple_properties', 0):,}",
                ""
            ])
        else:
            report_lines.append("No owner analysis performed.")
        
        report_lines.append("## 🔧 Data Preparation Steps")
        
        if data_prep:
            report_lines.extend([
                "### Version History:",
                "```json",
                json.dumps(data_prep.get('version_summary', []), indent=2),
                "```",
                ""
            ])
        else:
            report_lines.append("No data preparation summary available.")
        
        report_lines.extend([
            "## 📁 Files Included",
            "- `metadata.json` - Preset metadata and summary",
            "- `phone_prioritization_rules.json` - Custom phone prioritization rules",
            "- `owner_analysis.json` - Owner analysis results",
            "- `data_prep_summary.json` - Data preparation steps",
            "- `original_data_sample.csv` - Sample of original data",
            "- `prepared_data_sample.csv` - Sample of prepared data",
            "- `export_data_sample.csv` - Sample of export data",
            "- `column_comparison.json` - Column mapping comparison",
            "- `data_quality.json` - Data quality metrics",
            "- `preset_report.md` - This report",
            "",
            "## 🔍 How to Use This Preset",
            "1. Load the preset using the preset manager",
            "2. Apply the same phone prioritization rules",
            "3. Reference the owner analysis for marketing insights",
            "4. Use the data quality metrics for validation",
            "5. Compare column mappings for consistency",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _save_export_log(self, preset_id: str, metadata: Dict, export_data: Optional[pd.DataFrame]):
        """Save export log for tracking and reference."""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'preset_id': preset_id,
            'data_source': metadata['data_source'],
            'export_records': len(export_data) if export_data is not None else 0,
            'export_columns': len(export_data.columns) if export_data is not None else 0,
            'export_summary': {
                'total_owners': metadata['summary']['export_records'],
                'total_properties': metadata['summary']['export_records'],
                'pete_ready': True if export_data is not None else False
            }
        }
        
        # Append to export log
        log_file = self.logs_dir / "export_log.json"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {'exports': []}
        
        log_data['exports'].append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        # Save export data if provided
        if export_data is not None:
            export_file = self.exports_dir / f"{preset_id}_export.csv"
            export_data.to_csv(export_file, index=False)
            logger.info(f"📁 Export data saved: {export_file}")
    
    def load_preset(self, preset_id: str) -> Dict[str, Any]:
        """Load a saved preset."""
        preset_dir = self.presets_dir / preset_id
        
        if not preset_dir.exists():
            raise FileNotFoundError(f"Preset {preset_id} not found")
        
        preset_data = {}
        
        # Load metadata
        with open(preset_dir / "metadata.json", 'r') as f:
            preset_data['metadata'] = json.load(f)
        
        # Load phone prioritization rules
        rules_file = preset_dir / "phone_prioritization_rules.json"
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                preset_data['phone_prioritization_rules'] = json.load(f)
        
        # Load owner analysis
        analysis_file = preset_dir / "owner_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                preset_data['owner_analysis'] = json.load(f)
        
        # Load data prep summary
        prep_file = preset_dir / "data_prep_summary.json"
        if prep_file.exists():
            with open(prep_file, 'r') as f:
                preset_data['data_prep_summary'] = json.load(f)
        
        # Load data samples
        original_sample_file = preset_dir / "original_data_sample.csv"
        if original_sample_file.exists():
            preset_data['original_sample'] = pd.read_csv(original_sample_file)
        
        prepared_sample_file = preset_dir / "prepared_data_sample.csv"
        if prepared_sample_file.exists():
            preset_data['prepared_sample'] = pd.read_csv(prepared_sample_file)
        
        export_sample_file = preset_dir / "export_data_sample.csv"
        if export_sample_file.exists():
            preset_data['export_sample'] = pd.read_csv(export_sample_file)
        
        return preset_data
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """List all available presets."""
        presets = []
        
        for preset_dir in self.presets_dir.iterdir():
            if preset_dir.is_dir():
                metadata_file = preset_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    presets.append({
                        'preset_id': metadata['preset_id'],
                        'preset_name': metadata['preset_name'],
                        'data_source': metadata['data_source'],
                        'created_at': metadata['created_at'],
                        'summary': metadata['summary']
                    })
        
        # Sort by creation date (newest first)
        presets.sort(key=lambda x: x['created_at'], reverse=True)
        return presets
    
    def create_data_view(self, view_name: str, data: pd.DataFrame, 
                        description: str = "", filters: Optional[Dict] = None) -> str:
        """Create a reference view of data for future analysis."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        view_id = f"{view_name}_{timestamp}"
        view_dir = self.views_dir / view_id
        view_dir.mkdir(exist_ok=True)
        
        # Save view metadata
        view_metadata = {
            'view_name': view_name,
            'view_id': view_id,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'data_shape': data.shape,
            'filters': filters,
            'summary_stats': {
                'null_counts': data.isnull().sum().to_dict(),
                'unique_counts': {col: data[col].nunique() for col in data.columns[:10]},
                'sample_values': {col: data[col].dropna().head(5).tolist() for col in data.columns[:5]}
            }
        }
        
        with open(view_dir / "view_metadata.json", 'w') as f:
            json.dump(view_metadata, f, indent=2, default=str)
        
        # Save data sample
        data_sample = data.head(1000)
        data_sample.to_csv(view_dir / "data_sample.csv", index=False)
        
        # Generate view report
        report = f"""# 📊 Data View: {view_name}

**View ID:** {view_id}
**Created:** {view_metadata['created_at']}
**Description:** {description}

## 📈 Data Summary
- **Shape:** {data.shape[0]:,} rows × {data.shape[1]} columns
- **Memory Usage:** {data.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB

## 🔍 Sample Data
First 5 rows of key columns:

"""
        
        for col in data.columns[:5]:
            report += f"### {col}\n"
            sample_values = data[col].dropna().head(5).tolist()
            for val in sample_values:
                report += f"- {val}\n"
            report += "\n"
        
        with open(view_dir / "view_report.md", 'w') as f:
            f.write(report)
        
        logger.info(f"📊 Data view created: {view_dir}")
        return str(view_dir)


# Convenience functions
def save_preset(preset_name: str, data_source: str, original_df: pd.DataFrame, 
                prepared_df: pd.DataFrame, **kwargs) -> str:
    """Convenience function to save a preset."""
    manager = PresetManager()
    return manager.save_comprehensive_preset(preset_name, data_source, original_df, prepared_df, **kwargs)


def load_preset(preset_id: str) -> Dict[str, Any]:
    """Convenience function to load a preset."""
    manager = PresetManager()
    return manager.load_preset(preset_id)


def list_presets() -> List[Dict[str, Any]]:
    """Convenience function to list all presets."""
    manager = PresetManager()
    return manager.list_presets()


if __name__ == "__main__":
    # Example usage
    print("💾 PRESET MANAGER")
    print("=" * 40)
    
    manager = PresetManager()
    
    # List existing presets
    presets = manager.list_presets()
    print(f"Found {len(presets)} existing presets:")
    for preset in presets[:3]:  # Show first 3
        print(f"  • {preset['preset_name']} ({preset['data_source']}) - {preset['created_at']}")
    
    print("\n✅ Preset manager ready for use!") 