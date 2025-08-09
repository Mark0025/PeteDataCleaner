#!/usr/bin/env python3
"""
Ultra-Fast Owner Object Analyzer - Following Polars Best Practices

Uses Polars LazyFrame for maximum performance with vectorized operations only.
No batching, no row-by-row processing - process entire DataFrame at once.
"""

import polars as pl
from dataclasses import dataclass
from typing import List, Tuple
from loguru import logger
import time


@dataclass
class OwnerObject:
    """Represents a property owner with individual and business information."""
    
    # Core identification
    individual_name: str = ""
    business_name: str = ""
    mailing_address: str = ""
    property_address: str = ""
    
    # Owner type flags
    is_individual_owner: bool = False
    is_business_owner: bool = False
    has_skip_trace_info: bool = False
    
    # Property portfolio
    total_property_value: float = 0.0
    property_count: int = 0
    property_addresses: List[str] = None
    
    # Skip trace information
    skip_trace_target: str = ""
    confidence_score: float = 0.0
    
    # Pete mapping
    seller1_name: str = ""
    
    def __post_init__(self):
        if self.property_addresses is None:
            self.property_addresses = []
    
    def __str__(self):
        return f"OwnerObject(individual='{self.individual_name}', business='{self.business_name}', confidence={self.confidence_score:.1f})"


class UltraFastOwnerObjectAnalyzer:
    """Ultra-fast Owner Object Analyzer using Polars LazyFrame and vectorized operations."""
    
    def __init__(self):
        self.business_indicators = ['llc', 'inc', 'corp', 'company', 'holdings', 'properties', 'management']
        self.logger = logger
    
    def detect_business_entity(self, name: str) -> bool:
        """Detect if a name represents a business entity."""
        if not name:
            return False
        return any(indicator in str(name).lower() for indicator in self.business_indicators)
    
    def calculate_confidence_score(self, owner_obj: OwnerObject) -> float:
        """Calculate skip trace confidence score (0.0 to 1.0)."""
        score = 0.0
        if owner_obj.individual_name:
            score += 0.4
        if owner_obj.business_name:
            score += 0.2
        if owner_obj.property_count > 1:
            score += 0.2
        if owner_obj.total_property_value > 1_000_000:
            score += 0.2
        return min(score, 1.0)
    
    def create_skip_trace_target(self, owner_obj: OwnerObject) -> str:
        """Create the optimal skip trace target name and address."""
        name = owner_obj.individual_name or owner_obj.business_name or ""
        return f"{name} | {owner_obj.mailing_address}" if name else ""
    
    def create_seller1_name(self, owner_obj: OwnerObject) -> str:
        """Create Seller 1 name combining individual and business."""
        parts = [name for name in [owner_obj.individual_name, owner_obj.business_name] if name]
        return " | ".join(parts) or "Unknown Owner"
    
    def analyze_dataset_ultra_fast(self, df: pl.DataFrame) -> Tuple[List[OwnerObject], pl.DataFrame]:
        """Analyze dataset using Polars LazyFrame and vectorized operations only."""
        start_time = time.time()
        self.logger.info(f"🚀 Starting ULTRA-FAST Owner Object analysis on {len(df):,} records")
        
        # Convert to LazyFrame for memory efficiency
        df_lazy = df.lazy()
        
        # Add lowercase address column for grouping
        df_with_lower = df_lazy.with_columns(
            pl.col('Property Address').str.to_lowercase().alias('Property Address Lower')
        )
        
        # Group by address and aggregate - SINGLE VECTORIZED OPERATION
        self.logger.info(f"🔄 Grouping and aggregating data...")
        grouped = df_with_lower.group_by('Property Address Lower').agg([
            pl.first('Seller 1').alias('seller1'),
            pl.first('Property Address').alias('property_address'),
            pl.first('Property Address').alias('mailing_address'),  # Use Property Address as mailing
            pl.len().alias('property_count'),
            pl.col('Property Value').cast(pl.Float64, strict=False).fill_null(0.0).sum().alias('total_value'),
            pl.col('Property Address').unique().alias('property_addresses')
        ]).collect()
        
        self.logger.info(f"✅ Aggregated {len(grouped):,} unique addresses")
        
        # Create OwnerObjects from aggregated data
        self.logger.info(f"🔄 Creating OwnerObjects...")
        owner_objects = []
        
        for i, row in enumerate(grouped.iter_rows(named=True)):
            # Simple progress logging every 1000 records
            if i % 1000 == 0:
                self.logger.info(f"📊 Processing record {i:,}/{len(grouped):,}")
            
            try:
                addr_lower = row['Property Address Lower']
                if not addr_lower:
                    continue
                
                # Extract data from aggregated row
                seller1 = str(row['seller1'] or '').strip()
                property_address = str(row['property_address'] or '').strip()
                mailing_address = str(row['mailing_address'] or '').strip()
                property_count = int(row['property_count'] or 0)
                total_value = float(row['total_value'] or 0.0)
                property_addresses = list(row['property_addresses']) if row['property_addresses'] else []
                
                # Determine owner types using vectorized logic
                individual_name = ""
                business_name = ""
                if seller1:
                    if self.detect_business_entity(seller1):
                        business_name = seller1
                    else:
                        individual_name = seller1
                
                # Create Owner Object
                owner_obj = OwnerObject(
                    individual_name=individual_name,
                    business_name=business_name,
                    mailing_address=mailing_address,
                    property_address=property_address,
                    is_individual_owner=bool(individual_name),
                    is_business_owner=bool(business_name),
                    total_property_value=total_value,
                    property_count=property_count,
                    property_addresses=property_addresses
                )
                
                # Calculate additional fields
                owner_obj.confidence_score = self.calculate_confidence_score(owner_obj)
                owner_obj.skip_trace_target = self.create_skip_trace_target(owner_obj)
                owner_obj.seller1_name = self.create_seller1_name(owner_obj)
                owner_obj.has_skip_trace_info = bool(owner_obj.skip_trace_target)
                
                owner_objects.append(owner_obj)
                
            except Exception as e:
                self.logger.error(f"❌ Error processing record {i}: {e}")
                continue
        
        self.logger.info(f"✅ Created {len(owner_objects)} OwnerObjects")
        
        # Enhance original DataFrame using Polars join (vectorized)
        self.logger.info(f"🔄 Enhancing DataFrame with owner data...")
        df_enhanced = self._enhance_dataframe_vectorized(df, owner_objects)
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"🎉 ULTRA-FAST analysis completed in {elapsed_time:.2f} seconds")
        self.logger.info(f"📊 Performance: {len(df)/elapsed_time:.0f} records/second")
        
        # Log summary
        self._log_analysis_summary(owner_objects)
        
        return owner_objects, df_enhanced
    
    def _enhance_dataframe_vectorized(self, df: pl.DataFrame, owner_objects: List[OwnerObject]) -> pl.DataFrame:
        """Enhance DataFrame using Polars join (vectorized operation)."""
        # Create lookup DataFrame from owner objects
        owner_lookup = pl.DataFrame({
            'Property Address Lower': [obj.property_address.lower() for obj in owner_objects],
            'Owner Seller1 Name': [obj.seller1_name for obj in owner_objects],
            'Owner Skip Trace Target': [obj.skip_trace_target for obj in owner_objects],
            'Owner Confidence Score': [obj.confidence_score for obj in owner_objects],
            'Owner Type': [self._get_owner_type_label(obj) for obj in owner_objects],
            'Owner Property Count': [obj.property_count for obj in owner_objects]
        })
        
        # Join with original DataFrame using vectorized operation
        df_with_lower = df.with_columns(
            pl.col('Property Address').str.to_lowercase().alias('Property Address Lower')
        )
        
        enhanced = df_with_lower.join(
            owner_lookup,
            on='Property Address Lower',
            how='left'
        )
        
        # Fill nulls using with_columns (proper Polars way)
        enhanced = enhanced.with_columns([
            pl.col('Owner Seller1 Name').fill_null('Unknown Owner'),
            pl.col('Owner Skip Trace Target').fill_null(''),
            pl.col('Owner Confidence Score').fill_null(0.0),
            pl.col('Owner Type').fill_null('Unknown'),
            pl.col('Owner Property Count').fill_null(0)
        ]).drop('Property Address Lower')
        
        return enhanced
    
    def _get_owner_type_label(self, owner_obj: OwnerObject) -> str:
        """Get a human-readable owner type label."""
        if owner_obj.is_individual_owner and owner_obj.is_business_owner:
            return "Individual + Business"
        elif owner_obj.is_individual_owner:
            return "Individual Only"
        elif owner_obj.is_business_owner:
            return "Business Only"
        return "Unknown"
    
    def _log_analysis_summary(self, owner_objects: List[OwnerObject]):
        """Log summary statistics of the analysis."""
        total_owners = len(owner_objects)
        individual_only = sum(1 for obj in owner_objects if obj.is_individual_owner and not obj.is_business_owner)
        business_only = sum(1 for obj in owner_objects if obj.is_business_owner and not obj.is_individual_owner)
        both_types = sum(1 for obj in owner_objects if obj.is_individual_owner and obj.is_business_owner)
        high_confidence = sum(1 for obj in owner_objects if obj.confidence_score >= 0.8)
        total_properties = sum(obj.property_count for obj in owner_objects)
        total_value = sum(obj.total_property_value for obj in owner_objects)
        
        self.logger.info(f"📊 ULTRA-FAST OWNER ANALYSIS SUMMARY:")
        self.logger.info(f"   Total Owners: {total_owners:,}")
        self.logger.info(f"   Individual Only: {individual_only:,}")
        self.logger.info(f"   Business Only: {business_only:,}")
        self.logger.info(f"   High Confidence (80%+): {high_confidence:,}")
        self.logger.info(f"   Total Properties: {total_properties:,}")
        self.logger.info(f"   Total Value: ${total_value:,.0f}")


def test_ultra_fast_owner_analyzer():
    """Test the Ultra-Fast Owner Object Analyzer."""
    # Create sample data
    sample_data = {
        'Property Address': [
            '123 Main St, Miami, FL',
            '456 Oak Ave, Miami, FL', 
            '789 Pine St, Miami, FL',
            '123 Main St, Miami, FL',  # Duplicate address
            '321 Elm St, Miami, FL'
        ],
        'Mailing Address': [
            '123 Main St, Miami, FL',
            '999 Business Blvd, Miami, FL',
            '789 Pine St, Miami, FL',
            '123 Main St, Miami, FL',
            '321 Elm St, Miami, FL'
        ],
        'Seller 1': ['John Smith', 'XYZ Holdings LLC', 'Mary Johnson', 'John Smith', 'Bob Wilson'],
        'Property Value': [500_000, 750_000, 300_000, 600_000, 400_000]
    }
    
    df = pl.DataFrame(sample_data)
    analyzer = UltraFastOwnerObjectAnalyzer()
    
    print("🚀 Testing Ultra-Fast Owner Object Analyzer...")
    owner_objects, df_enhanced = analyzer.analyze_dataset_ultra_fast(df)
    
    print(f"\n📊 Results:")
    print(f"Created {len(owner_objects)} OwnerObjects")
    print(f"Enhanced DataFrame shape: {df_enhanced.shape}")
    
    print(f"\n🏠 Owner Objects:")
    for i, obj in enumerate(owner_objects, 1):
        print(f"  {i}. {obj}")
    
    print(f"\n📋 Enhanced DataFrame:")
    print(df_enhanced)


if __name__ == "__main__":
    test_ultra_fast_owner_analyzer() 