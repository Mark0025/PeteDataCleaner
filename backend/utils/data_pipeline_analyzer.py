#!/usr/bin/env python3
"""
🔍 Data Pipeline Analyzer - Comprehensive Dataset Analysis

Analyzes the full dataset in uploads/, tests phone prioritization,
creates matplotlib funnel visualizations, and captures before/after metrics.

Features:
- Full dataset analysis with phone prioritization testing
- Matplotlib funnel visualization of data pipeline stages
- Comprehensive before/after metrics using loguru
- Integration with whatsworking for reporting
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import json

# Import our utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils import trailing_dot_cleanup as tdc
from backend.utils import phone_prioritizer as pp
from backend.utils.phone_prioritizer.stats import *

# Setup loguru for comprehensive logging
from loguru import logger
import sys

# Configure loguru
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("DEV_MAN/logs/pipeline_analysis.log", rotation="10 MB", level="DEBUG")

class DataPipelineAnalyzer:
    """Comprehensive analyzer for the full dataset pipeline"""
    
    def __init__(self, upload_dir: str = "upload"):
        self.upload_dir = Path(upload_dir)
        self.results = {}
        self.before_metrics = {}
        self.after_metrics = {}
        self.visualization_data = {}
        
    def find_largest_csv(self) -> Optional[Path]:
        """Find the largest CSV file in uploads directory"""
        csv_files = list(self.upload_dir.glob("*.csv"))
        if not csv_files:
            logger.warning("No CSV files found in upload directory")
            return None
            
        largest_file = max(csv_files, key=lambda f: f.stat().st_size)
        logger.info(f"Found largest CSV file: {largest_file} ({largest_file.stat().st_size / 1024 / 1024:.1f} MB)")
        return largest_file
    
    def load_and_analyze_dataset(self, filepath: Path) -> pd.DataFrame:
        """Load dataset and perform initial analysis"""
        logger.info(f"Loading dataset: {filepath}")
        
        try:
            # Load the dataset
            df = pd.read_csv(filepath)
            logger.info(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Analyze before cleaning
            self.before_metrics = self._analyze_before_cleaning(df)
            logger.info("Before cleaning analysis completed")
            
            # Apply automatic cleaning
            df_cleaned = tdc.clean_dataframe(df)
            logger.info("Applied automatic .0 cleanup")
            
            # Analyze after cleaning
            self.after_metrics = self._analyze_after_cleaning(df_cleaned)
            logger.info("After cleaning analysis completed")
            
            return df_cleaned
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def _analyze_before_cleaning(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset before any cleaning"""
        metrics = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'phone_columns': [],
            'phone_status_columns': [],
            'phone_type_columns': [],
            'phone_tag_columns': [],
            'trailing_dot_count': 0,
            'sample_phone_numbers': [],
            'column_types': {}
        }
        
        # Find phone-related columns
        for col in df.columns:
            col_lower = col.lower()
            if 'phone' in col_lower and 'status' not in col_lower and 'type' not in col_lower and 'tag' not in col_lower:
                metrics['phone_columns'].append(col)
            elif 'phone' in col_lower and 'status' in col_lower:
                metrics['phone_status_columns'].append(col)
            elif 'phone' in col_lower and 'type' in col_lower:
                metrics['phone_type_columns'].append(col)
            elif 'phone' in col_lower and 'tag' in col_lower:
                metrics['phone_tag_columns'].append(col)
        
        # Count trailing .0 in phone numbers
        for col in metrics['phone_columns']:
            if col in df.columns:
                # Sample some phone numbers
                sample_phones = df[col].dropna().head(5).tolist()
                metrics['sample_phone_numbers'].extend([str(phone) for phone in sample_phones])
                
                # Count trailing .0
                trailing_dot_count = df[col].astype(str).str.endswith('.0').sum()
                metrics['trailing_dot_count'] += trailing_dot_count
        
        # Analyze column types
        for col in df.columns:
            metrics['column_types'][col] = str(df[col].dtype)
        
        logger.info(f"Before cleaning: {metrics['trailing_dot_count']} phone numbers with trailing .0")
        return metrics
    
    def _analyze_after_cleaning(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset after cleaning"""
        metrics = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'phone_prioritization_results': {},
            'status_distribution': {},
            'type_distribution': {},
            'call_history_distribution': {},
            'prioritization_effectiveness': {}
        }
        
        # Test phone prioritization
        try:
            from backend.utils.phone_prioritizer import prioritize
            prioritized_df, meta = prioritize(df)
            metrics['phone_prioritization_results'] = meta
            
            # Store the processed DataFrame for export
            self.processed_df = prioritized_df.copy()
            
            # Analyze status distribution
            status_counts = get_status_distribution(df)
            metrics['status_distribution'] = status_counts
            
            # Analyze type distribution
            type_counts = get_type_distribution(df)
            metrics['type_distribution'] = type_counts
            
            # Analyze call history
            call_counts = get_call_count_distribution(df)
            metrics['call_history_distribution'] = call_counts
            
            # Calculate prioritization effectiveness
            effectiveness = self._calculate_prioritization_effectiveness(df, prioritized_df)
            metrics['prioritization_effectiveness'] = effectiveness
            
            logger.info(f"Phone prioritization completed: {len(prioritized_df)} rows processed")
            
        except Exception as e:
            logger.error(f"Phone prioritization failed: {e}")
            metrics['phone_prioritization_results'] = {'error': str(e)}
        
        return metrics
    
    def _calculate_prioritization_effectiveness(self, original_df: pd.DataFrame, prioritized_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate how effective the prioritization was"""
        effectiveness = {
            'correct_numbers_selected': 0,
            'mobile_numbers_selected': 0,
            'low_call_count_selected': 0,
            'wrong_numbers_excluded': 0,
            'selection_quality_score': 0.0
        }
        
        # Count how many CORRECT numbers were selected
        for i in range(1, 6):  # Phone 1-5
            phone_col = f'Phone {i}'
            status_col = f'Phone Status {i}'
            
            if phone_col in prioritized_df.columns and status_col in prioritized_df.columns:
                correct_count = (prioritized_df[status_col] == 'CORRECT').sum()
                effectiveness['correct_numbers_selected'] += correct_count
                
                # Count mobile numbers
                type_col = f'Phone Type {i}'
                if type_col in prioritized_df.columns:
                    mobile_count = (prioritized_df[type_col] == 'MOBILE').sum()
                    effectiveness['mobile_numbers_selected'] += mobile_count
        
        # Calculate quality score (higher is better)
        total_selected = effectiveness['correct_numbers_selected'] + effectiveness['mobile_numbers_selected']
        if total_selected > 0:
            effectiveness['selection_quality_score'] = (effectiveness['correct_numbers_selected'] / total_selected) * 100
        
        return effectiveness
    
    def create_funnel_visualization(self) -> str:
        """Create a comprehensive matplotlib funnel visualization"""
        logger.info("Creating funnel visualization")
        
        # Create figure with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('📊 Pete Data Cleaner - Full Pipeline Analysis', fontsize=20, fontweight='bold')
        
        # 1. Main Data Pipeline Funnel
        self._create_main_funnel(ax1)
        
        # 2. Phone Status Distribution
        self._create_status_distribution(ax2)
        
        # 3. Phone Type Distribution
        self._create_type_distribution(ax3)
        
        # 4. Call History Analysis
        self._create_call_history_analysis(ax4)
        
        plt.tight_layout()
        
        # Save the visualization
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"DEV_MAN/whatsworking/pipeline_funnel_{timestamp}.png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Funnel visualization saved: {filename}")
        return filename
    
    def _create_main_funnel(self, ax):
        """Create the main data pipeline funnel"""
        ax.set_title('🔄 Data Pipeline Funnel', fontsize=16, fontweight='bold')
        
        # Pipeline stages
        stages = [
            ('📁 Raw Upload', self.before_metrics.get('total_rows', 0)),
            ('🧹 .0 Cleanup', self.before_metrics.get('total_rows', 0)),  # Same count, but cleaned
            ('📞 Phone Analysis', self.before_metrics.get('total_rows', 0)),
            ('🎯 Prioritization', self.after_metrics.get('prioritization_effectiveness', {}).get('correct_numbers_selected', 0)),
            ('✅ Pete Ready', self.after_metrics.get('prioritization_effectiveness', {}).get('correct_numbers_selected', 0))
        ]
        
        # Create funnel
        y_positions = np.linspace(0, 1, len(stages))
        widths = [stage[1] for stage in stages]
        max_width = max(widths)
        normalized_widths = [w/max_width for w in widths]
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        
        for i, ((stage_name, count), width, color) in enumerate(zip(stages, normalized_widths, colors)):
            # Create funnel segment
            rect = FancyBboxPatch(
                (0.5 - width/2, y_positions[i] - 0.1),
                width, 0.15,
                boxstyle="round,pad=0.01",
                facecolor=color,
                edgecolor='black',
                linewidth=1
            )
            ax.add_patch(rect)
            
            # Add text
            ax.text(0.5, y_positions[i], f'{stage_name}\n{count:,}', 
                   ha='center', va='center', fontsize=12, fontweight='bold')
            
            # Add percentage if not first stage
            if i > 0:
                percentage = (count / stages[0][1]) * 100
                ax.text(0.5, y_positions[i] - 0.15, f'{percentage:.1f}%', 
                       ha='center', va='center', fontsize=10, color='gray')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.2, 1.2)
        ax.axis('off')
    
    def _create_status_distribution(self, ax):
        """Create phone status distribution chart"""
        ax.set_title('📊 Phone Status Distribution', fontsize=16, fontweight='bold')
        
        status_data = self.after_metrics.get('status_distribution', {})
        if not status_data:
            ax.text(0.5, 0.5, 'No status data available', ha='center', va='center')
            return
        
        statuses = list(status_data.keys())
        counts = list(status_data.values())
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e']
        
        wedges, texts, autotexts = ax.pie(counts, labels=statuses, autopct='%1.1f%%', 
                                          colors=colors[:len(statuses)], startangle=90)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _create_type_distribution(self, ax):
        """Create phone type distribution chart"""
        ax.set_title('📱 Phone Type Distribution', fontsize=16, fontweight='bold')
        
        type_data = self.after_metrics.get('type_distribution', {})
        if not type_data:
            ax.text(0.5, 0.5, 'No type data available', ha='center', va='center')
            return
        
        types = list(type_data.keys())
        counts = list(type_data.values())
        colors = ['#3498db', '#e67e22', '#1abc9c', '#95a5a6']
        
        bars = ax.bar(types, counts, color=colors[:len(types)])
        ax.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _create_call_history_analysis(self, ax):
        """Create call history analysis chart"""
        ax.set_title('📞 Call History Analysis', fontsize=16, fontweight='bold')
        
        call_data = self.after_metrics.get('call_history_distribution', {})
        if not call_data:
            ax.text(0.5, 0.5, 'No call history data available', ha='center', va='center')
            return
        
        calls = list(call_data.keys())
        counts = list(call_data.values())
        
        # Create horizontal bar chart
        y_pos = np.arange(len(calls))
        bars = ax.barh(y_pos, counts, color='#e74c3c')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(calls)
        ax.set_xlabel('Count')
        
        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                   f'{count:,}', ha='left', va='center', fontweight='bold')
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report"""
        logger.info("Generating comprehensive analysis report")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            "# 🔍 Data Pipeline Analysis Report",
            "",
            f"**Generated:** {timestamp}",
            f"**Dataset:** {self.upload_dir}",
            "",
            "---",
            "",
            "## 📊 Before vs After Analysis",
            ""
        ]
        
        # Before cleaning summary
        report_lines.extend([
            "### 🚫 Before Cleaning:",
            f"- **Total Rows:** {self.before_metrics.get('total_rows', 0):,}",
            f"- **Total Columns:** {self.before_metrics.get('total_columns', 0)}",
            f"- **Phone Columns:** {len(self.before_metrics.get('phone_columns', []))}",
            f"- **Trailing .0 Count:** {self.before_metrics.get('trailing_dot_count', 0):,}",
            f"- **Sample Phone Numbers:** {', '.join(self.before_metrics.get('sample_phone_numbers', [])[:3])}",
            ""
        ])
        
        # After cleaning summary
        effectiveness = self.after_metrics.get('prioritization_effectiveness', {})
        report_lines.extend([
            "### ✅ After Cleaning & Prioritization:",
            f"- **Total Rows:** {self.after_metrics.get('total_rows', 0):,}",
            f"- **Correct Numbers Selected:** {effectiveness.get('correct_numbers_selected', 0):,}",
            f"- **Mobile Numbers Selected:** {effectiveness.get('mobile_numbers_selected', 0):,}",
            f"- **Selection Quality Score:** {effectiveness.get('selection_quality_score', 0):.1f}%",
            ""
        ])
        
        # Status distribution
        status_data = self.after_metrics.get('status_distribution', {})
        if status_data:
            report_lines.extend([
                "### 📊 Phone Status Distribution:",
                "| Status | Count | Percentage |",
                "|--------|-------|------------|"
            ])
            total_status = sum(status_data.values())
            for status, count in status_data.items():
                percentage = (count / total_status * 100) if total_status > 0 else 0
                report_lines.append(f"| {status} | {count:,} | {percentage:.1f}% |")
            report_lines.append("")
        
        # Type distribution
        type_data = self.after_metrics.get('type_distribution', {})
        if type_data:
            report_lines.extend([
                "### 📱 Phone Type Distribution:",
                "| Type | Count | Percentage |",
                "|------|-------|------------|"
            ])
            total_type = sum(type_data.values())
            for phone_type, count in type_data.items():
                percentage = (count / total_type * 100) if total_type > 0 else 0
                report_lines.append(f"| {phone_type} | {count:,} | {percentage:.1f}% |")
            report_lines.append("")
        
        # Call history
        call_data = self.after_metrics.get('call_history_distribution', {})
        if call_data:
            report_lines.extend([
                "### 📞 Call History Distribution:",
                "| Call Count | Count | Percentage |",
                "|------------|-------|------------|"
            ])
            total_calls = sum(call_data.values())
            for call_count, count in call_data.items():
                percentage = (count / total_calls * 100) if total_calls > 0 else 0
                report_lines.append(f"| {call_count} | {count:,} | {percentage:.1f}% |")
            report_lines.append("")
        
        # Key improvements
        report_lines.extend([
            "## 🎯 Key Improvements Achieved",
            "",
            "### ⚡ Performance Improvements:",
            f"- **Trailing .0 Cleanup:** {self.before_metrics.get('trailing_dot_count', 0):,} phone numbers cleaned",
            f"- **Data Quality:** {effectiveness.get('selection_quality_score', 0):.1f}% quality score for phone selection",
            f"- **Efficiency:** Automated prioritization of {effectiveness.get('correct_numbers_selected', 0):,} correct numbers",
            ""
        ])
        
        # Technical details
        report_lines.extend([
            "## 🔧 Technical Details",
            "",
            "### Data Processing Pipeline:",
            "1. **Raw Upload** → Load CSV/Excel file",
            "2. **Automatic .0 Cleanup** → Strip trailing .0 from phone numbers",
            "3. **Phone Analysis** → Analyze status, type, and call history",
            "4. **Smart Prioritization** → Select best 5 phones based on criteria",
            "5. **Pete Ready** → Clean, prioritized data for Pete",
            ""
        ])
        
        # Save report
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"DEV_MAN/whatsworking/pipeline_analysis_{timestamp}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Comprehensive report saved: {filename}")
        return filename
    
    def export_processed_data(self) -> str:
        """Export the processed data to Excel format."""
        try:
            # Get the processed DataFrame (after phone prioritization)
            if not hasattr(self, 'processed_df') or self.processed_df is None:
                logger.warning("No processed data available for export")
                return ""
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"DEV_MAN/whatsworking/processed_data_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Export to Excel
            self.processed_df.to_excel(filename, index=False, engine='openpyxl')
            
            logger.info(f"Processed data exported to Excel: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export processed data: {e}")
            return ""
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis pipeline"""
        logger.info("Starting full data pipeline analysis")
        
        try:
            # Find the largest CSV file
            largest_file = self.find_largest_csv()
            if not largest_file:
                logger.error("No suitable CSV file found")
                return {}
            
            # Load and analyze dataset
            df = self.load_and_analyze_dataset(largest_file)
            
            # Create visualization
            viz_filename = self.create_funnel_visualization()
            
            # Generate comprehensive report
            report_filename = self.generate_comprehensive_report()
            
            # Export processed data to Excel
            excel_filename = self.export_processed_data()
            
            # Compile results
            results = {
                'dataset_file': str(largest_file),
                'before_metrics': self.before_metrics,
                'after_metrics': self.after_metrics,
                'visualization_file': viz_filename,
                'report_file': report_filename,
                'excel_export_file': excel_filename,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Save results as JSON
            results_filename = f"DEV_MAN/whatsworking/pipeline_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            os.makedirs(os.path.dirname(results_filename), exist_ok=True)
            
            with open(results_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.success(f"Full analysis completed successfully")
            logger.info(f"Results saved: {results_filename}")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

def main():
    """Main entry point for data pipeline analysis"""
    try:
        analyzer = DataPipelineAnalyzer()
        results = analyzer.run_full_analysis()
        
        print(f"\n🎯 Data Pipeline Analysis Complete!")
        print(f"📊 Dataset analyzed: {results.get('dataset_file', 'Unknown')}")
        print(f"📈 Before metrics: {results.get('before_metrics', {}).get('total_rows', 0):,} rows")
        print(f"✅ After metrics: {results.get('after_metrics', {}).get('total_rows', 0):,} rows")
        print(f"📊 Visualization: {results.get('visualization_file', 'Not created')}")
        print(f"📋 Report: {results.get('report_file', 'Not created')}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

if __name__ == '__main__':
    main() 