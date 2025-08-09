#!/usr/bin/env python3
"""
Owner Analysis Utility

Analyzes property ownership patterns, business entities, and ownership insights.
Provides comprehensive reporting for marketing and data analysis.
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from loguru import logger
import json
from datetime import datetime


@dataclass
class OwnerInsight:
    """Represents an ownership insight."""
    owner_name: str
    mailing_address: str
    property_count: int
    properties: List[str]
    is_business: bool
    business_type: Optional[str]
    total_value: Optional[float]
    avg_value: Optional[float]
    last_exported: Optional[str]
    phone_numbers: List[str]
    emails: List[str]


@dataclass
class BusinessEntity:
    """Represents a business entity."""
    name: str
    entity_type: str
    property_count: int
    total_value: Optional[float]
    properties: List[str]


class OwnerAnalyzer:
    """
    Comprehensive owner analysis utility.
    
    Features:
    - Business entity detection
    - Property ownership patterns
    - Mailing address analysis
    - Export status tracking
    - Marketing insights
    """
    
    def __init__(self):
        self.business_indicators = {
            'llc': ['llc', 'l l c', 'limited liability company'],
            'corporation': ['inc', 'corp', 'corporation', 'incorporated'],
            'company': ['company', 'co\\.', 'comp'],
            'trust': ['trust', 'estate', 'trustee'],
            'bank': ['bank', 'mortgage', 'lending'],
            'investments': ['investments', 'holdings', 'properties', 'realty'],
            'management': ['management', 'mgmt', 'real estate']
        }
        
        self.export_status = {}  # Track which owners have been exported
        
        # Import Polars for fast processing
        try:
            import polars as pl
            self.pl = pl
            self.use_polars = True
        except ImportError:
            self.use_polars = False
            logger.warning("Polars not available, falling back to pandas")
    
    def analyze_ownership(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive ownership analysis using fast processor and progress tracking.
        
        Args:
            df: DataFrame with property data
            
        Returns:
            Dictionary with analysis results
        """
        from backend.utils.progress_tracker import track_data_processing
        
        # Initialize progress tracker
        progress = track_data_processing("Owner Analysis", len(df))
        
        logger.info(f"🔍 Starting ownership analysis for {len(df):,} records")
        
        # Create owner identifier using fast processor
        progress.start_transformation()
        df_clean = self._prepare_data_fast(df)
        progress.update_progress(len(df))
        progress.end_current_step(len(df))
        
        # Use ultra-fast Polars methods for maximum performance
        if self.use_polars:
            logger.info("🚀 Using ultra-fast Polars methods for owner analysis")
            business_entities = self._detect_business_entities_fast(df_clean)
            ownership_patterns = self._analyze_ownership_patterns_fast(df_clean)
            mailing_analysis = self._analyze_mailing_addresses_fast(df_clean)
            value_analysis = self._analyze_property_values_fast(df_clean)
            marketing_insights = self._generate_marketing_insights_fast(df_clean)
            owner_insights = self._generate_owner_insights_fast(df_clean)
        else:
            logger.info("⚠️ Using pandas methods (Polars not available)")
            business_entities = self._detect_business_entities(df_clean)
            ownership_patterns = self._analyze_ownership_patterns(df_clean)
            mailing_analysis = self._analyze_mailing_addresses(df_clean)
            value_analysis = self._analyze_property_values(df_clean)
            marketing_insights = self._generate_marketing_insights(df_clean)
            owner_insights = self._generate_owner_insights(df_clean)
        
        analysis_results = {
            'total_records': len(df),
            'total_owners': df_clean['owner_name'].nunique(),
            'total_addresses': df_clean['Mailing address'].nunique() if 'Mailing address' in df_clean.columns else 0,
            'business_entities': business_entities,
            'ownership_patterns': ownership_patterns,
            'mailing_address_analysis': mailing_analysis,
            'property_value_analysis': value_analysis,
            'export_status': self._get_export_status(df_clean),
            'marketing_insights': marketing_insights,
            'owner_insights': owner_insights
        }
        
        # Complete processing
        progress.complete_processing()
        
        logger.info(f"✅ Ownership analysis complete: {analysis_results['total_owners']:,} owners analyzed")
        return analysis_results
    
    def _detect_business_entities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect and categorize business entities."""
        business_owners = []
        individual_owners = []
        entity_types = {}
        
        for owner_name in df['owner_name'].unique():
            if pd.isna(owner_name) or owner_name == '':
                continue
            
            entity_type = self._classify_entity(owner_name)
            if entity_type:
                business_owners.append(owner_name)
                entity_types[owner_name] = entity_type
            else:
                individual_owners.append(owner_name)
        
        return {
            'business_count': len(business_owners),
            'individual_count': len(individual_owners),
            'business_percentage': (len(business_owners) / len(df['owner_name'].unique())) * 100,
            'entity_types': entity_types,
            'sample_businesses': business_owners[:10],
            'sample_individuals': individual_owners[:10]
        }
    
    def _classify_entity(self, owner_name: str) -> Optional[str]:
        """Classify an owner as a business entity type."""
        owner_lower = owner_name.lower()
        
        for entity_type, indicators in self.business_indicators.items():
            for indicator in indicators:
                if re.search(rf'\b{indicator}\b', owner_lower):
                    return entity_type
        
        return None
    
    def _analyze_ownership_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze property ownership patterns."""
        owner_groups = df.groupby('owner_name')
        
        # Count properties per owner
        property_counts = owner_groups.size()
        
        # Owners with multiple properties
        multi_property_owners = property_counts[property_counts > 1]
        
        # Top property owners
        top_owners = property_counts.nlargest(10)
        
        return {
            'owners_with_multiple_properties': len(multi_property_owners),
            'owners_with_single_property': len(property_counts[property_counts == 1]),
            'max_properties_per_owner': property_counts.max(),
            'avg_properties_per_owner': property_counts.mean(),
            'top_owners': top_owners.to_dict(),
            'multi_property_examples': self._get_multi_property_examples(df, multi_property_owners.head(5))
        }
    
    def _get_multi_property_examples(self, df: pd.DataFrame, top_owners: pd.Series) -> List[Dict]:
        """Get examples of owners with multiple properties."""
        examples = []
        
        for owner_name in top_owners.index:
            owner_properties = df[df['owner_name'] == owner_name]
            
            example = {
                'owner_name': owner_name,
                'property_count': len(owner_properties),
                'properties': owner_properties['Property address'].tolist()[:5] if len(owner_properties) > 0 else [],  # First 5 properties
                'mailing_address': owner_properties['Mailing address'].iloc[0] if ('Mailing address' in owner_properties.columns and len(owner_properties) > 0) else 'N/A'
            }
            examples.append(example)
        
        return examples
    
    def _analyze_mailing_addresses(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze mailing address patterns."""
        if 'Mailing address' not in df.columns:
            return {'error': 'Mailing address column not found'}
        
        addr_groups = df.groupby('Mailing address')
        
        # Addresses with multiple owners
        multi_owner_addresses = addr_groups.filter(lambda x: len(x) > 1)
        
        return {
            'total_addresses': len(addr_groups),
            'addresses_with_multiple_owners': len(multi_owner_addresses['Mailing address'].unique()),
            'addresses_with_single_owner': len(addr_groups) - len(multi_owner_addresses['Mailing address'].unique()),
            'max_owners_per_address': addr_groups.size().max(),
            'avg_owners_per_address': addr_groups.size().mean(),
            'multi_owner_examples': self._get_multi_owner_address_examples(df, addr_groups)
        }
    
    def _get_multi_owner_address_examples(self, df: pd.DataFrame, addr_groups) -> List[Dict]:
        """Get examples of addresses with multiple owners."""
        examples = []
        
        for addr, group in list(addr_groups)[:5]:  # Limit to first 5 groups
            if len(group) > 1:
                example = {
                    'address': addr,
                    'owner_count': len(group),
                    'owners': group['owner_name'].tolist(),
                    'properties': group['Property address'].tolist()
                }
                examples.append(example)
                
                if len(examples) >= 5:  # Limit to 5 examples
                    break
        
        return examples
    
    def _analyze_property_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze property values by owner."""
        if 'Estimated value' not in df.columns:
            return {'error': 'Estimated value column not found'}
        
        # Convert to numeric, handling non-numeric values
        df['value_numeric'] = pd.to_numeric(df['Estimated value'], errors='coerce')
        
        # Group by owner and calculate value statistics
        owner_values = df.groupby('owner_name')['value_numeric'].agg(['sum', 'mean', 'count']).reset_index()
        owner_values.columns = ['owner_name', 'total_value', 'avg_value', 'property_count']
        
        return {
            'total_property_value': df['value_numeric'].sum(),
            'avg_property_value': df['value_numeric'].mean(),
            'top_value_owners': owner_values.nlargest(10, 'total_value')[['owner_name', 'total_value', 'property_count']].to_dict(orient='records'),
            'value_distribution': {
                'under_100k': len(df[df['value_numeric'] < 100000]),
                '100k_200k': len(df[(df['value_numeric'] >= 100000) & (df['value_numeric'] < 200000)]),
                '200k_500k': len(df[(df['value_numeric'] >= 200000) & (df['value_numeric'] < 500000)]),
                'over_500k': len(df[df['value_numeric'] >= 500000])
            }
        }
    
    def _get_export_status(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get export status for owners."""
        # This would typically check against a database or export log
        # For now, return placeholder data
        return {
            'exported_owners': 0,
            'pending_export': len(df['owner_name'].unique()),
            'export_percentage': 0.0
        }
    
    def _generate_marketing_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate marketing insights from ownership data."""
        insights = {
            'high_value_targets': [],
            'multi_property_opportunities': [],
            'business_entity_opportunities': [],
            'geographic_concentrations': []
        }
        
        # High value targets (owners with properties > $500k)
        if 'Estimated value' in df.columns:
            df['value_numeric'] = pd.to_numeric(df['Estimated value'], errors='coerce')
            high_value_owners = df[df['value_numeric'] > 500000]['owner_name'].unique()
            insights['high_value_targets'] = high_value_owners.tolist()[:10]
        
        # Multi-property opportunities
        owner_counts = df.groupby('owner_name').size()
        multi_property_owners = owner_counts[owner_counts > 1].index.tolist()
        insights['multi_property_opportunities'] = multi_property_owners[:10]
        
        # Business entity opportunities
        business_owners = []
        for owner_name in df['owner_name'].unique():
            if self._classify_entity(owner_name):
                business_owners.append(owner_name)
        insights['business_entity_opportunities'] = business_owners[:10]
        
        return insights
    
    def _generate_owner_insights(self, df: pd.DataFrame) -> List[OwnerInsight]:
        """Generate detailed insights for each owner."""
        insights = []
        
        for owner_name in df['owner_name'].unique():
            owner_data = df[df['owner_name'] == owner_name]
            
            # Get property addresses
            properties = owner_data['Property address'].tolist()
            
            # Get mailing address
            mailing_address = owner_data['Mailing address'].iloc[0] if 'Mailing address' in owner_data.columns else 'N/A'
            
            # Check if business entity
            is_business = bool(self._classify_entity(owner_name))
            business_type = self._classify_entity(owner_name)
            
            # Calculate values
            total_value = None
            avg_value = None
            if 'Estimated value' in owner_data.columns:
                values = pd.to_numeric(owner_data['Estimated value'], errors='coerce')
                total_value = values.sum()
                avg_value = values.mean()
            
            # Get phone numbers and emails
            phone_numbers = []
            email_addresses = []
            
            for col in owner_data.columns:
                if col.startswith('Phone ') and col.count(' ') == 1:
                    phones = owner_data[col].dropna().tolist()
                    phone_numbers.extend(phones)
                elif col.startswith('Email ') and col.count(' ') == 1:
                    emails = owner_data[col].dropna().tolist()
                    email_addresses.extend(emails)
            
            insight = OwnerInsight(
                owner_name=owner_name,
                mailing_address=mailing_address,
                property_count=len(owner_data),
                properties=properties,
                is_business=is_business,
                business_type=business_type,
                total_value=total_value,
                avg_value=avg_value,
                last_exported=None,  # Would come from export tracking
                phone_numbers=phone_numbers[:5],  # Limit to 5
                emails=email_addresses[:5]  # Limit to 5
            )
            
            insights.append(insight)
        
        return insights
    
    def _prepare_data_fast(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data using fast processor."""
        if self.use_polars:
            # Convert to Polars for fast processing
            pl_df = self.pl.from_pandas(df)
            
            # Create owner name using Polars
            pl_df = pl_df.with_columns([
                (self.pl.col('First Name').fill_null('') + 
                 self.pl.lit(' ') + 
                 self.pl.col('Last Name').fill_null('')).str.strip_chars().alias('owner_name')
            ])
            
            # Filter out empty owners
            pl_df = pl_df.filter(self.pl.col('owner_name') != '')
            
            # Convert back to pandas
            return pl_df.to_pandas()
        else:
            # Fallback to pandas
            df_clean = df.copy()
            df_clean['owner_name'] = (
                df_clean['First Name'].fillna('') + ' ' + 
                df_clean['Last Name'].fillna('')
            ).str.strip()
            return df_clean[df_clean['owner_name'] != '']
    
    def _detect_business_entities_fast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fast business entity detection using Polars."""
        if self.use_polars:
            pl_df = self.pl.from_pandas(df)
            
            # Get unique owner names
            unique_owners = pl_df.select('owner_name').unique().to_series().to_list()
            
            business_owners = []
            individual_owners = []
            entity_types = {}
            
            for owner_name in unique_owners:
                if pd.isna(owner_name) or owner_name == '':
                    continue
                
                entity_type = self._classify_entity(owner_name)
                if entity_type:
                    business_owners.append(owner_name)
                    entity_types[owner_name] = entity_type
                else:
                    individual_owners.append(owner_name)
            
            return {
                'business_count': len(business_owners),
                'individual_count': len(individual_owners),
                'business_percentage': (len(business_owners) / len(unique_owners)) * 100 if unique_owners else 0,
                'entity_types': entity_types,
                'sample_businesses': business_owners[:10],
                'sample_individuals': individual_owners[:10]
            }
        else:
            return self._detect_business_entities(df)
    
    def _analyze_ownership_patterns_fast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fast ownership pattern analysis using Polars."""
        if self.use_polars:
            pl_df = self.pl.from_pandas(df)
            
            # Group by owner and count properties
            owner_counts = pl_df.group_by('owner_name').count().sort('count', descending=True)
            
            # Convert to pandas for easier processing
            owner_counts_pd = owner_counts.to_pandas()
            
            # Owners with multiple properties
            multi_property_owners = owner_counts_pd[owner_counts_pd['count'] > 1]
            
            # Top owners
            top_owners = owner_counts_pd.head(10).set_index('owner_name')['count'].to_dict()
            
            return {
                'owners_with_multiple_properties': len(multi_property_owners),
                'owners_with_single_property': len(owner_counts_pd[owner_counts_pd['count'] == 1]),
                'max_properties_per_owner': owner_counts_pd['count'].max(),
                'avg_properties_per_owner': owner_counts_pd['count'].mean(),
                'top_owners': top_owners,
                'multi_property_examples': self._get_multi_property_examples(df, multi_property_owners.head(5))
            }
        else:
            return self._analyze_ownership_patterns(df)
    
    def _analyze_mailing_addresses_fast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fast mailing address analysis using Polars."""
        if self.use_polars and 'Mailing address' in df.columns:
            pl_df = self.pl.from_pandas(df)
            
            # Group by mailing address
            addr_counts = pl_df.group_by('Mailing address').count().sort('count', descending=True)
            addr_counts_pd = addr_counts.to_pandas()
            
            # Addresses with multiple owners
            multi_owner_addresses = addr_counts_pd[addr_counts_pd['count'] > 1]
            
            return {
                'total_addresses': len(addr_counts_pd),
                'addresses_with_multiple_owners': len(multi_owner_addresses),
                'addresses_with_single_owner': len(addr_counts_pd[addr_counts_pd['count'] == 1]),
                'max_owners_per_address': addr_counts_pd['count'].max(),
                'avg_owners_per_address': addr_counts_pd['count'].mean(),
                'multi_owner_examples': []  # Simplified for fast processing
            }
        else:
            return self._analyze_mailing_addresses(df)
    
    def _analyze_property_values_fast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fast property value analysis using Polars."""
        if self.use_polars and 'Estimated value' in df.columns:
            pl_df = self.pl.from_pandas(df)
            
            # Convert to numeric
            pl_df = pl_df.with_columns([
                self.pl.col('Estimated value').cast(self.pl.Float64, strict=False).alias('value_numeric')
            ])
            
            # Group by owner and calculate statistics
            owner_values = pl_df.group_by('owner_name').agg([
                self.pl.col('value_numeric').sum().alias('total_value'),
                self.pl.col('value_numeric').mean().alias('avg_value'),
                self.pl.col('value_numeric').count().alias('property_count')
            ]).sort('total_value', descending=True)
            
            owner_values_pd = owner_values.to_pandas()
            
            # Calculate overall statistics
            total_value = pl_df.select('value_numeric').sum().item()
            avg_value = pl_df.select('value_numeric').mean().item()
            
            return {
                'total_property_value': total_value,
                'avg_property_value': avg_value,
                'top_value_owners': owner_values_pd.head(10)[['owner_name', 'total_value', 'property_count']].to_dict('records'),
                'value_distribution': self._calculate_value_distribution_fast(pl_df)
            }
        else:
            return self._analyze_property_values(df)
    
    def _calculate_value_distribution_fast(self, pl_df) -> Dict[str, int]:
        """Calculate value distribution using Polars."""
        distribution = pl_df.select([
            (self.pl.col('value_numeric') < 100000).sum().alias('under_100k'),
            ((self.pl.col('value_numeric') >= 100000) & (self.pl.col('value_numeric') < 200000)).sum().alias('100k_200k'),
            ((self.pl.col('value_numeric') >= 200000) & (self.pl.col('value_numeric') < 500000)).sum().alias('200k_500k'),
            (self.pl.col('value_numeric') >= 500000).sum().alias('over_500k')
        ]).to_pandas().to_dict('records')[0]
        
        return distribution
    
    def _generate_marketing_insights_fast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fast marketing insights generation using Polars."""
        if self.use_polars:
            pl_df = self.pl.from_pandas(df)
            
            insights = {
                'high_value_targets': [],
                'multi_property_opportunities': [],
                'business_entity_opportunities': [],
                'geographic_concentrations': []
            }
            
            # High value targets
            if 'Estimated value' in df.columns:
                pl_df = pl_df.with_columns([
                    self.pl.col('Estimated value').cast(self.pl.Float64, strict=False).alias('value_numeric')
                ])
                high_value_owners = pl_df.filter(self.pl.col('value_numeric') > 500000).select('owner_name').unique().to_series().to_list()
                insights['high_value_targets'] = high_value_owners[:10]
            
            # Multi-property opportunities
            owner_counts = pl_df.group_by('owner_name').count().filter(self.pl.col('count') > 1)
            multi_property_owners = owner_counts.select('owner_name').to_series().to_list()
            insights['multi_property_opportunities'] = multi_property_owners[:10]
            
            # Business entity opportunities
            unique_owners = pl_df.select('owner_name').unique().to_series().to_list()
            business_owners = [owner for owner in unique_owners if self._classify_entity(owner)]
            insights['business_entity_opportunities'] = business_owners[:10]
            
            return insights
        else:
            return self._generate_marketing_insights(df)
    
    def _generate_owner_insights_fast(self, df: pd.DataFrame) -> List[OwnerInsight]:
        """Fast owner insights generation using Polars."""
        if self.use_polars:
            pl_df = self.pl.from_pandas(df)
            
            insights = []
            unique_owners = pl_df.select('owner_name').unique().to_series().to_list()
            
            for owner_name in unique_owners:
                owner_data = pl_df.filter(self.pl.col('owner_name') == owner_name)
                owner_data_pd = owner_data.to_pandas()
                
                # Get property addresses
                properties = owner_data_pd['Property address'].tolist()
                
                # Get mailing address
                mailing_address = owner_data_pd['Mailing address'].iloc[0] if 'Mailing address' in owner_data_pd.columns else 'N/A'
                
                # Check if business entity
                is_business = bool(self._classify_entity(owner_name))
                business_type = self._classify_entity(owner_name)
                
                # Calculate values
                total_value = None
                avg_value = None
                if 'Estimated value' in owner_data_pd.columns:
                    values = pd.to_numeric(owner_data_pd['Estimated value'], errors='coerce')
                    total_value = values.sum()
                    avg_value = values.mean()
                
                # Get phone numbers and emails
                phone_numbers = []
                email_addresses = []
                
                for col in owner_data_pd.columns:
                    if col.startswith('Phone ') and col.count(' ') == 1:
                        phones = owner_data_pd[col].dropna().tolist()
                        phone_numbers.extend(phones)
                    elif col.startswith('Email ') and col.count(' ') == 1:
                        emails = owner_data_pd[col].dropna().tolist()
                        email_addresses.extend(emails)
                
                insight = OwnerInsight(
                    owner_name=owner_name,
                    mailing_address=mailing_address,
                    property_count=len(owner_data_pd),
                    properties=properties,
                    is_business=is_business,
                    business_type=business_type,
                    total_value=total_value,
                    avg_value=avg_value,
                    last_exported=None,
                    phone_numbers=phone_numbers[:5],
                    emails=email_addresses[:5]
                )
                
                insights.append(insight)
            
            return insights
        else:
            return self._generate_owner_insights(df)
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive ownership analysis report."""
        report_lines = []
        
        report_lines.append("🏠 PROPERTY OWNERSHIP ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        report_lines.append("📊 SUMMARY:")
        report_lines.append(f"  Total Records: {analysis_results['total_records']:,}")
        report_lines.append(f"  Total Owners: {analysis_results['total_owners']:,}")
        report_lines.append(f"  Total Addresses: {analysis_results['total_addresses']:,}")
        report_lines.append("")
        
        # Business entities
        business = analysis_results['business_entities']
        report_lines.append("🏢 BUSINESS ENTITIES:")
        report_lines.append(f"  Business Owners: {business['business_count']:,} ({business['business_percentage']:.1f}%)")
        report_lines.append(f"  Individual Owners: {business['individual_count']:,}")
        report_lines.append("")
        
        # Ownership patterns
        patterns = analysis_results['ownership_patterns']
        report_lines.append("👤 OWNERSHIP PATTERNS:")
        report_lines.append(f"  Multi-Property Owners: {patterns['owners_with_multiple_properties']:,}")
        report_lines.append(f"  Single-Property Owners: {patterns['owners_with_single_property']:,}")
        report_lines.append(f"  Max Properties per Owner: {patterns['max_properties_per_owner']}")
        report_lines.append(f"  Avg Properties per Owner: {patterns['avg_properties_per_owner']:.1f}")
        report_lines.append("")
        
        # Top owners
        report_lines.append("🏆 TOP PROPERTY OWNERS:")
        for owner, count in list(patterns['top_owners'].items())[:5]:
            report_lines.append(f"  {owner}: {count} properties")
        report_lines.append("")
        
        # Marketing insights
        insights = analysis_results['marketing_insights']
        report_lines.append("🎯 MARKETING INSIGHTS:")
        report_lines.append(f"  High-Value Targets: {len(insights['high_value_targets'])}")
        report_lines.append(f"  Multi-Property Opportunities: {len(insights['multi_property_opportunities'])}")
        report_lines.append(f"  Business Entity Opportunities: {len(insights['business_entity_opportunities'])}")
        report_lines.append("")
        
        return "\n".join(report_lines)
    
    def export_owner_data(self, analysis_results: Dict[str, Any], output_file: str):
        """Export owner analysis data to JSON."""
        export_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_records': analysis_results['total_records'],
                'total_owners': analysis_results['total_owners'],
                'total_addresses': analysis_results['total_addresses']
            },
            'owner_insights': [
                {
                    'owner_name': insight.owner_name,
                    'mailing_address': insight.mailing_address,
                    'property_count': insight.property_count,
                    'properties': insight.properties,
                    'is_business': insight.is_business,
                    'business_type': insight.business_type,
                    'total_value': insight.total_value,
                    'avg_value': insight.avg_value,
                    'phone_numbers': insight.phone_numbers,
                    'emails': insight.emails
                }
                for insight in analysis_results['owner_insights']
            ],
            'business_entities': analysis_results['business_entities'],
            'ownership_patterns': analysis_results['ownership_patterns'],
            'marketing_insights': analysis_results['marketing_insights']
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"📁 Owner analysis exported to: {output_file}")


# Convenience functions
def analyze_ownership_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Convenience function to analyze ownership data."""
    analyzer = OwnerAnalyzer()
    return analyzer.analyze_ownership(df)


def generate_ownership_report(df: pd.DataFrame) -> str:
    """Convenience function to generate ownership report."""
    analyzer = OwnerAnalyzer()
    results = analyzer.analyze_ownership(df)
    return analyzer.generate_report(results)


if __name__ == "__main__":
    # Example usage
    print("🏠 OWNER ANALYSIS UTILITY")
    print("=" * 40)
    
    # Load sample data
    df = pd.read_csv('upload/All_RECORDS_12623 (1).csv', nrows=1000)
    
    # Analyze ownership
    analyzer = OwnerAnalyzer()
    results = analyzer.analyze_ownership(df)
    
    # Generate and print report
    report = analyzer.generate_report(results)
    print(report)
    
    # Export data
    analyzer.export_owner_data(results, 'DEV_MAN/owner_analysis_export.json') 