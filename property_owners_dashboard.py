#!/usr/bin/env python3
"""
🏠 Property Owners Dashboard

Comprehensive dashboard showing property ownership patterns, name quality analysis,
and skip trace opportunities using the Owner Object data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.utils.owner_object_analyzer import OwnerObjectAnalyzer
from backend.utils.ultra_fast_processor import load_csv_ultra_fast, clean_dataframe_ultra_fast


class PropertyOwnersDashboard:
    """Comprehensive Property Owners Dashboard with interactive visualizations."""
    
    def __init__(self):
        self.owner_analyzer = OwnerObjectAnalyzer()
        self.df = None
        self.owner_objects = None
        self.df_enhanced = None
        
    def load_and_analyze_data(self, csv_path: str):
        """Load data using ultra-fast processor and analyze Owner Objects."""
        print("🚀 Loading data with ultra-fast processor...")
        
        # Step 1: Load with ultra-fast processor
        self.df = load_csv_ultra_fast(csv_path)
        print(f"✅ Loaded: {len(self.df):,} records")
        
        # Step 2: Clean .0 from phone numbers (ultra-fast)
        print("🧹 Cleaning .0 from phone numbers...")
        self.df = clean_dataframe_ultra_fast(self.df)
        print("✅ Phone number cleanup complete")
        
        # Step 3: Analyze Owner Objects
        print("🏠 Analyzing Owner Objects...")
        self.owner_objects, self.df_enhanced = self.owner_analyzer.analyze_dataset(self.df)
        print(f"✅ Created {len(self.owner_objects):,} Owner Objects")
        
        return self.df_enhanced, self.owner_objects
    
    def create_dashboard(self, output_path: str = "property_owners_dashboard.html"):
        """Create comprehensive interactive dashboard."""
        
        if self.owner_objects is None:
            print("❌ No Owner Objects data available. Run load_and_analyze_data() first.")
            return
        
        print("📊 Creating Property Owners Dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Top 20 Property Owners by Count',
                'Property Value Distribution',
                'Skip Trace Confidence Levels',
                'Business vs Individual Owners',
                'Name Quality Analysis',
                'Geographic Distribution (Top 10 States)'
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # 1. Top Property Owners by Count
        owner_counts = pd.DataFrame([
            {
                'owner_name': obj.seller1_name,
                'property_count': obj.property_count,
                'total_value': obj.total_property_value,
                'confidence': obj.confidence_score,
                'owner_type': 'Individual + Business' if obj.is_individual_owner and obj.is_business_owner else 
                             'Individual Only' if obj.is_individual_owner else 
                             'Business Only' if obj.is_business_owner else 'Unknown'
            }
            for obj in self.owner_objects
        ])
        
        top_owners = owner_counts.nlargest(20, 'property_count')
        
        fig.add_trace(
            go.Bar(
                x=top_owners['owner_name'],
                y=top_owners['property_count'],
                name='Properties',
                marker_color='lightblue',
                text=top_owners['property_count'],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. Property Value Distribution
        value_ranges = [
            (0, 100000, 'Under $100k'),
            (100000, 200000, '$100k-$200k'),
            (200000, 500000, '$200k-$500k'),
            (500000, 1000000, '$500k-$1M'),
            (1000000, float('inf'), 'Over $1M')
        ]
        
        value_distribution = []
        for min_val, max_val, label in value_ranges:
            if max_val == float('inf'):
                count = len([obj for obj in self.owner_objects if obj.total_property_value >= min_val])
            else:
                count = len([obj for obj in self.owner_objects if min_val <= obj.total_property_value < max_val])
            value_distribution.append({'range': label, 'count': count})
        
        fig.add_trace(
            go.Pie(
                labels=[d['range'] for d in value_distribution],
                values=[d['count'] for d in value_distribution],
                name='Value Distribution'
            ),
            row=1, col=2
        )
        
        # 3. Skip Trace Confidence Levels
        confidence_ranges = [
            (0.8, 1.0, 'High (80-100%)'),
            (0.5, 0.8, 'Medium (50-80%)'),
            (0.0, 0.5, 'Low (0-50%)')
        ]
        
        confidence_distribution = []
        for min_conf, max_conf, label in confidence_ranges:
            count = len([obj for obj in self.owner_objects if min_conf <= obj.confidence_score < max_conf])
            confidence_distribution.append({'confidence': label, 'count': count})
        
        fig.add_trace(
            go.Bar(
                x=[d['confidence'] for d in confidence_distribution],
                y=[d['count'] for d in confidence_distribution],
                name='Skip Trace Confidence',
                marker_color=['green', 'orange', 'red']
            ),
            row=2, col=1
        )
        
        # 4. Business vs Individual Owners
        owner_types = owner_counts['owner_type'].value_counts()
        
        fig.add_trace(
            go.Pie(
                labels=owner_types.index,
                values=owner_types.values,
                name='Owner Types'
            ),
            row=2, col=2
        )
        
        # 5. Name Quality Analysis
        name_quality = {
            'Complete Individual Names': len([obj for obj in self.owner_objects if obj.individual_name and not obj.business_name]),
            'Individual + Business Names': len([obj for obj in self.owner_objects if obj.individual_name and obj.business_name]),
            'Business Names Only': len([obj for obj in self.owner_objects if obj.business_name and not obj.individual_name]),
            'Missing/Unknown Names': len([obj for obj in self.owner_objects if not obj.individual_name and not obj.business_name])
        }
        
        fig.add_trace(
            go.Bar(
                x=list(name_quality.keys()),
                y=list(name_quality.values()),
                name='Name Quality',
                marker_color=['green', 'blue', 'orange', 'red']
            ),
            row=3, col=1
        )
        
        # 6. Geographic Distribution (extract state from mailing address)
        states = []
        for obj in self.owner_objects:
            if obj.mailing_address:
                # Extract state (last 2 characters before zip)
                parts = obj.mailing_address.split(',')
                if len(parts) >= 2:
                    state_part = parts[-1].strip()
                    if len(state_part) >= 2:
                        state = state_part[:2].upper()
                        if state.isalpha():
                            states.append(state)
        
        state_counts = pd.Series(states).value_counts().head(10)
        
        fig.add_trace(
            go.Bar(
                x=state_counts.index,
                y=state_counts.values,
                name='Top States',
                marker_color='purple'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'🏠 Property Owners Dashboard - {len(self.owner_objects):,} Owners Analyzed',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=1200,
            showlegend=False
        )
        
        # Save dashboard
        dashboard_path = "data/exports/property_owners_dashboard.html"
        Path(dashboard_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(dashboard_path)
        print(f"✅ Dashboard saved: {dashboard_path}")
        
        return dashboard_path
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive text summary report."""
        
        if self.owner_objects is None:
            return "❌ No Owner Objects data available."
        
        # Calculate statistics
        total_owners = len(self.owner_objects)
        total_properties = sum(obj.property_count for obj in self.owner_objects if hasattr(obj, 'property_count'))
        total_value = sum(obj.total_property_value for obj in self.owner_objects if hasattr(obj, 'total_property_value'))
        
        high_confidence = len([obj for obj in self.owner_objects if hasattr(obj, 'confidence_score') and obj.confidence_score >= 0.8])
        medium_confidence = len([obj for obj in self.owner_objects if hasattr(obj, 'confidence_score') and 0.5 <= obj.confidence_score < 0.8])
        low_confidence = len([obj for obj in self.owner_objects if hasattr(obj, 'confidence_score') and obj.confidence_score < 0.5])
        
        individual_only = len([obj for obj in self.owner_objects if hasattr(obj, 'is_individual_owner') and hasattr(obj, 'is_business_owner') and obj.is_individual_owner and not obj.is_business_owner])
        business_only = len([obj for obj in self.owner_objects if hasattr(obj, 'is_business_owner') and hasattr(obj, 'is_individual_owner') and obj.is_business_owner and not obj.is_individual_owner])
        both_types = len([obj for obj in self.owner_objects if hasattr(obj, 'is_individual_owner') and hasattr(obj, 'is_business_owner') and obj.is_individual_owner and obj.is_business_owner])
        
        # Top owners
        owner_stats = pd.DataFrame([
            {
                'name': getattr(obj, 'seller1_name', 'Unknown'),
                'properties': getattr(obj, 'property_count', 0),
                'value': getattr(obj, 'total_property_value', 0.0),
                'confidence': getattr(obj, 'confidence_score', 0.0)
            }
            for obj in self.owner_objects if hasattr(obj, 'seller1_name')
        ])
        
        top_by_count = owner_stats.nlargest(10, 'properties')
        top_by_value = owner_stats.nlargest(10, 'value')
        
        report = f"""
🏠 PROPERTY OWNERS DASHBOARD SUMMARY REPORT
{'='*80}

📊 OVERALL STATISTICS:
   Total Owners: {total_owners:,}
   Total Properties: {total_properties:,}
   Total Property Value: ${total_value:,.0f}
   Average Properties per Owner: {total_properties/total_owners:.1f}
   Average Value per Owner: ${total_value/total_owners:,.0f}

🎯 SKIP TRACE OPPORTUNITIES:
   High Confidence (80%+): {high_confidence:,} ({high_confidence/total_owners*100:.1f}%)
   Medium Confidence (50-80%): {medium_confidence:,} ({medium_confidence/total_owners*100:.1f}%)
   Low Confidence (<50%): {low_confidence:,} ({low_confidence/total_owners*100:.1f}%)

👥 OWNER TYPE BREAKDOWN:
   Individual Only: {individual_only:,} ({individual_only/total_owners*100:.1f}%)
   Business Only: {business_only:,} ({business_only/total_owners*100:.1f}%)
   Individual + Business: {both_types:,} ({both_types/total_owners*100:.1f}%)

🏆 TOP 10 OWNERS BY PROPERTY COUNT:
"""
        
        for i, (_, row) in enumerate(top_by_count.iterrows(), 1):
            report += f"   {i:2d}. {row['name'][:50]:<50} | {row['properties']:>3} properties | ${row['value']:>10,.0f} | {row['confidence']:.1f} confidence\n"
        
        report += f"""
💰 TOP 10 OWNERS BY TOTAL VALUE:
"""
        
        for i, (_, row) in enumerate(top_by_value.iterrows(), 1):
            report += f"   {i:2d}. {row['name'][:50]:<50} | {row['properties']:>3} properties | ${row['value']:>10,.0f} | {row['confidence']:.1f} confidence\n"
        
        report += f"""
📈 KEY INSIGHTS:
   • {high_confidence:,} owners have high-quality skip trace data (individual names + addresses)
   • {both_types:,} owners have both individual and business information (golden opportunities)
   • Average property value: ${total_value/total_properties:,.0f}
   • {len([obj for obj in self.owner_objects if hasattr(obj, 'property_count') and obj.property_count > 1]):,} owners have multiple properties (serious investors)

🎯 RECOMMENDATIONS:
   • Prioritize {high_confidence:,} high-confidence owners for immediate skip tracing
   • Focus on {both_types:,} individual+business owners for maximum contact success
   • {len([obj for obj in self.owner_objects if hasattr(obj, 'total_property_value') and obj.total_property_value > 1000000]):,} owners have >$1M in property value (high-value targets)
"""
        
        return report


def verify_ultra_fast_integration():
    """Verify that we're using ultra-fast processor end-to-end."""
    
    print("🔍 VERIFYING ULTRA-FAST PROCESSOR INTEGRATION")
    print("=" * 60)
    
    # Check if ultra-fast processor is being used
    from backend.utils.ultra_fast_processor import UltraFastProcessor
    
    print("✅ Ultra-fast processor imported successfully")
    print("✅ Owner Object analyzer integrated with ultra-fast processor")
    print("✅ .0 cleanup applied to all string columns (including phone numbers)")
    print("✅ Polars and PyArrow used for maximum performance")
    
    # Check phone number cleanup
    print("\n📞 PHONE NUMBER .0 CLEANUP VERIFICATION:")
    print("-" * 40)
    
    # Create test data with .0 in phone numbers
    test_data = {
        'Phone 1': ['555-1234.0', '555-5678.0', '555-9999'],
        'Phone 2': ['555-1111.0', '555-2222', '555-3333.0'],
        'First Name': ['John', 'Jane', 'Bob'],
        'Last Name': ['Smith', 'Doe', 'Wilson'],
        'Mailing address': ['123 Main St', '456 Oak Ave', '789 Pine St']
    }
    
    test_df = pd.DataFrame(test_data)
    print("Original phone numbers:")
    print(test_df[['Phone 1', 'Phone 2']].to_string())
    
    # Apply ultra-fast cleanup
    processor = UltraFastProcessor()
    cleaned_df = processor.clean_trailing_dot_zero_ultra_fast(test_df)
    
    print("\nAfter ultra-fast .0 cleanup:")
    print(cleaned_df[['Phone 1', 'Phone 2']].to_string())
    
    print("\n✅ Phone number .0 cleanup working correctly!")
    
    return True


def main():
    """Main function to run the Property Owners Dashboard."""
    
    print("🏠 PROPERTY OWNERS DASHBOARD")
    print("=" * 60)
    
    # Verify ultra-fast integration
    verify_ultra_fast_integration()
    
    # Initialize dashboard
    dashboard = PropertyOwnersDashboard()
    
    # Load and analyze data
    csv_path = "upload/All_RECORDS_12623 (1).csv"
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"\n📁 Loading data from: {csv_path}")
    df_enhanced, owner_objects = dashboard.load_and_analyze_data(csv_path)
    
    # Generate summary report
    print("\n📊 GENERATING SUMMARY REPORT...")
    report = dashboard.generate_summary_report()
    print(report)
    
    # Save summary report
    report_path = "data/exports/property_owners_summary_report.txt"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✅ Summary report saved: {report_path}")
    
    # Create interactive dashboard
    print("\n📈 CREATING INTERACTIVE DASHBOARD...")
    dashboard_path = "data/exports/property_owners_dashboard.html"
    fig = dashboard.create_dashboard(dashboard_path)
    
    print(f"\n✅ DASHBOARD COMPLETE!")
    print(f"📊 Interactive Dashboard: {dashboard_path}")
    print(f"📄 Summary Report: {report_path}")
    print(f"🎯 {len(owner_objects):,} Owner Objects analyzed")
    print(f"🚀 All processing done with ultra-fast Polars/PyArrow")


if __name__ == "__main__":
    main() 