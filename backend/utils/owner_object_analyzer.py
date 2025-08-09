#!/usr/bin/env python3
"""
Owner Object Analyzer

Creates sophisticated Owner Objects that can identify actual people behind LLCs
for better skip tracing and Pete data mapping.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
from loguru import logger


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


class OwnerObjectAnalyzer:
    """Analyzes property data to create sophisticated Owner Objects."""
    
    def __init__(self):
        self.business_indicators = [
            'llc', 'inc', 'corp', 'company', 'holdings', 'properties', 
            'realty', 'management', 'investments', 'group', 'associates',
            'partners', 'enterprises', 'ventures', 'capital', 'fund'
        ]
        
        self.logger = logger
    
    def detect_business_entity(self, name: str) -> bool:
        """Detect if a name represents a business entity."""
        if pd.isna(name) or name == "":
            return False
        
        name_lower = str(name).lower()
        return any(indicator in name_lower for indicator in self.business_indicators)
    
    def create_owner_name(self, first_name: str, last_name: str) -> str:
        """Create a clean individual name from first and last name."""
        if pd.isna(first_name) and pd.isna(last_name):
            return ""
        
        first = str(first_name).strip() if pd.notna(first_name) else ""
        last = str(last_name).strip() if pd.notna(last_name) else ""
        
        if first and last:
            return f"{first} {last}".strip()
        elif first:
            return first
        elif last:
            return last
        else:
            return ""
    
    def analyze_address_match(self, property_addr: str, mailing_addr: str) -> bool:
        """Check if property address matches mailing address (potential individual owner)."""
        if pd.isna(property_addr) or pd.isna(mailing_addr):
            return False
        
        # Normalize addresses for comparison
        prop_norm = str(property_addr).lower().strip()
        mail_norm = str(mailing_addr).lower().strip()
        
        # Exact match
        if prop_norm == mail_norm:
            return True
        
        # Partial match (same street address)
        prop_parts = prop_norm.split()
        mail_parts = mail_norm.split()
        
        # Check if street number and name match
        if len(prop_parts) >= 2 and len(mail_parts) >= 2:
            if prop_parts[0] == mail_parts[0] and prop_parts[1] == mail_parts[1]:
                return True
        
        return False
    
    def calculate_confidence_score(self, owner_obj: OwnerObject) -> float:
        """Calculate skip trace confidence score (0.0 to 1.0)."""
        score = 0.0
        
        # Individual name present
        if owner_obj.individual_name:
            score += 0.4
        
        # Business name present
        if owner_obj.business_name:
            score += 0.2
        
        # Address match (property = mailing)
        if self.analyze_address_match(owner_obj.property_address, owner_obj.mailing_address):
            score += 0.3
        
        # Multiple properties (indicates serious investor)
        if owner_obj.property_count > 1:
            score += 0.1
        
        # High property value
        if owner_obj.total_property_value > 1000000:  # $1M+
            score += 0.1
        
        return min(score, 1.0)
    
    def create_skip_trace_target(self, owner_obj: OwnerObject) -> str:
        """Create the optimal skip trace target name and address."""
        if owner_obj.individual_name:
            # Prefer individual name for skip tracing
            return f"{owner_obj.individual_name} | {owner_obj.mailing_address}"
        elif owner_obj.business_name:
            # Fall back to business name
            return f"{owner_obj.business_name} | {owner_obj.mailing_address}"
        else:
            return ""
    
    def create_seller1_name(self, owner_obj: OwnerObject) -> str:
        """Create Pete's Seller 1 name combining individual and business."""
        parts = []
        
        if owner_obj.individual_name:
            parts.append(owner_obj.individual_name)
        
        if owner_obj.business_name:
            parts.append(owner_obj.business_name)
        
        if parts:
            return " | ".join(parts)
        else:
            return "Unknown Owner"
    
    def analyze_property_group(self, group: pd.DataFrame) -> OwnerObject:
        """Analyze a group of properties with the same mailing address."""
        
        # Get the first record for reference
        first_record = group.iloc[0]
        
        # Extract basic information
        individual_name = self.create_owner_name(
            first_record.get('First Name', ''),
            first_record.get('Last Name', '')
        )
        
        business_name = str(first_record.get('Business Name', '')).strip()
        mailing_address = str(first_record.get('Mailing address', '')).strip()
        property_address = str(first_record.get('Property address', '')).strip()
        
        # Determine owner types
        is_individual = bool(individual_name)
        is_business = self.detect_business_entity(business_name)
        
        # Check for address match (potential individual behind LLC)
        address_match = self.analyze_address_match(property_address, mailing_address)
        
        # Calculate property portfolio
        total_value = 0.0
        if 'Estimated value' in group.columns:
            values = pd.to_numeric(group['Estimated value'], errors='coerce')
            total_value = values.sum()
        
        property_addresses = group['Property address'].dropna().unique().tolist()
        
        # Create Owner Object
        owner_obj = OwnerObject(
            individual_name=individual_name,
            business_name=business_name,
            mailing_address=mailing_address,
            property_address=property_address,
            is_individual_owner=is_individual,
            is_business_owner=is_business,
            total_property_value=total_value,
            property_count=len(group),
            property_addresses=property_addresses
        )
        
        # Calculate confidence and create skip trace info
        owner_obj.confidence_score = self.calculate_confidence_score(owner_obj)
        owner_obj.skip_trace_target = self.create_skip_trace_target(owner_obj)
        owner_obj.seller1_name = self.create_seller1_name(owner_obj)
        owner_obj.has_skip_trace_info = bool(owner_obj.skip_trace_target)
        
        return owner_obj
    
    def analyze_dataset(self, df: pd.DataFrame) -> Tuple[List[OwnerObject], pd.DataFrame]:
        """Analyze entire dataset and create Owner Objects."""
        
        self.logger.info(f"🏠 Starting Owner Object analysis on {len(df):,} records")
        
        # Group by mailing address
        if 'Mailing address' not in df.columns:
            self.logger.error("❌ 'Mailing address' column not found")
            return [], df
        
        # Group properties by mailing address
        addr_groups = df.groupby('Mailing address')
        self.logger.info(f"📊 Found {len(addr_groups):,} unique mailing addresses")
        
        # Create Owner Objects
        owner_objects = []
        processed_count = 0
        
        # Track statistics for logging
        individual_count = 0
        business_count = 0
        both_count = 0
        high_confidence_count = 0
        medium_confidence_count = 0
        low_confidence_count = 0
        
        for addr, group in addr_groups:
            try:
                owner_obj = self.analyze_property_group(group)
                owner_objects.append(owner_obj)
                processed_count += 1
                
                # Update statistics
                if owner_obj.is_individual_owner and owner_obj.is_business_owner:
                    both_count += 1
                elif owner_obj.is_individual_owner:
                    individual_count += 1
                elif owner_obj.is_business_owner:
                    business_count += 1
                
                if owner_obj.confidence_score >= 0.8:
                    high_confidence_count += 1
                elif owner_obj.confidence_score >= 0.5:
                    medium_confidence_count += 1
                else:
                    low_confidence_count += 1
                
                # Log progress with metadata every 1000 owners
                if processed_count % 1000 == 0:
                    self.logger.info(f"✅ Processed {processed_count:,} owner groups")
                    self.logger.info(f"   📊 Current Stats:")
                    self.logger.info(f"      Individual Only: {individual_count:,} ({individual_count/processed_count*100:.1f}%)")
                    self.logger.info(f"      Business Only: {business_count:,} ({business_count/processed_count*100:.1f}%)")
                    self.logger.info(f"      Individual + Business: {both_count:,} ({both_count/processed_count*100:.1f}%)")
                    self.logger.info(f"      High Confidence (80%+): {high_confidence_count:,} ({high_confidence_count/processed_count*100:.1f}%)")
                    self.logger.info(f"      Medium Confidence (50-80%): {medium_confidence_count:,} ({medium_confidence_count/processed_count*100:.1f}%)")
                    self.logger.info(f"      Low Confidence (<50%): {low_confidence_count:,} ({low_confidence_count/processed_count*100:.1f}%)")
                    
                    # Show sample of recent Owner Objects
                    recent_objects = owner_objects[-5:]
                    self.logger.info(f"   🎯 Recent Owner Objects:")
                    for i, obj in enumerate(recent_objects, 1):
                        owner_type = "Individual+Business" if obj.is_individual_owner and obj.is_business_owner else \
                                   "Individual Only" if obj.is_individual_owner else \
                                   "Business Only" if obj.is_business_owner else "Unknown"
                        
                        self.logger.info(f"      {i}. {obj.seller1_name[:50]:<50} | {owner_type:<15} | {obj.confidence_score:.1f} confidence | {obj.property_count} properties")
                    
                    self.logger.info(f"   📍 Sample Address: {addr[:60]}...")
                    self.logger.info("")
                        
            except Exception as e:
                self.logger.error(f"❌ Error processing address {addr}: {e}")
                continue
        
        # Add Owner Object information to dataframe
        df_enhanced = self.enhance_dataframe_with_owners(df, owner_objects)
        
        # Log summary statistics
        self.logger.info(f"🎯 Created {len(owner_objects):,} Owner Objects")
        self._log_analysis_summary(owner_objects)
        
        return owner_objects, df_enhanced
    
    def enhance_dataframe_with_owners(self, df: pd.DataFrame, owner_objects: List[OwnerObject]) -> pd.DataFrame:
        """Add Owner Object information to the dataframe."""
        
        # Create a mapping from mailing address to owner object
        addr_to_owner = {obj.mailing_address: obj for obj in owner_objects}
        
        # Add new columns
        df_enhanced = df.copy()
        
        # Map owner information to each record
        df_enhanced['Seller_1'] = df_enhanced['Mailing address'].map(
            lambda addr: addr_to_owner.get(addr, OwnerObject()).seller1_name
        )
        
        df_enhanced['Skip_Trace_Target'] = df_enhanced['Mailing address'].map(
            lambda addr: addr_to_owner.get(addr, OwnerObject()).skip_trace_target
        )
        
        df_enhanced['Owner_Confidence'] = df_enhanced['Mailing address'].map(
            lambda addr: addr_to_owner.get(addr, OwnerObject()).confidence_score
        )
        
        df_enhanced['Owner_Type'] = df_enhanced['Mailing address'].map(
            lambda addr: self._get_owner_type_label(addr_to_owner.get(addr, OwnerObject()))
        )
        
        df_enhanced['Property_Count'] = df_enhanced['Mailing address'].map(
            lambda addr: addr_to_owner.get(addr, OwnerObject()).property_count
        )
        
        return df_enhanced
    
    def _get_owner_type_label(self, owner_obj: OwnerObject) -> str:
        """Get a human-readable owner type label."""
        if owner_obj.is_individual_owner and owner_obj.is_business_owner:
            return "Individual + Business"
        elif owner_obj.is_individual_owner:
            return "Individual Only"
        elif owner_obj.is_business_owner:
            return "Business Only"
        else:
            return "Unknown"
    
    def _log_analysis_summary(self, owner_objects: List[OwnerObject]):
        """Log summary statistics of the analysis."""
        
        total_owners = len(owner_objects)
        individual_only = sum(1 for obj in owner_objects if obj.is_individual_owner and not obj.is_business_owner)
        business_only = sum(1 for obj in owner_objects if obj.is_business_owner and not obj.is_individual_owner)
        both_types = sum(1 for obj in owner_objects if obj.is_individual_owner and obj.is_business_owner)
        
        high_confidence = sum(1 for obj in owner_objects if obj.confidence_score >= 0.8)
        medium_confidence = sum(1 for obj in owner_objects if 0.5 <= obj.confidence_score < 0.8)
        low_confidence = sum(1 for obj in owner_objects if obj.confidence_score < 0.5)
        
        total_properties = sum(obj.property_count for obj in owner_objects)
        total_value = sum(obj.total_property_value for obj in owner_objects)
        
        self.logger.info(f"📊 OWNER ANALYSIS SUMMARY:")
        self.logger.info(f"   Total Owners: {total_owners:,}")
        self.logger.info(f"   Individual Only: {individual_only:,} ({individual_only/total_owners*100:.1f}%)")
        self.logger.info(f"   Business Only: {business_only:,} ({business_only/total_owners*100:.1f}%)")
        self.logger.info(f"   Individual + Business: {both_types:,} ({both_types/total_owners*100:.1f}%)")
        self.logger.info(f"")
        self.logger.info(f"🎯 SKIP TRACE CONFIDENCE:")
        self.logger.info(f"   High Confidence (80%+): {high_confidence:,} ({high_confidence/total_owners*100:.1f}%)")
        self.logger.info(f"   Medium Confidence (50-80%): {medium_confidence:,} ({medium_confidence/total_owners*100:.1f}%)")
        self.logger.info(f"   Low Confidence (<50%): {low_confidence:,} ({low_confidence/total_owners*100:.1f}%)")
        self.logger.info(f"")
        self.logger.info(f"💰 PROPERTY PORTFOLIO:")
        self.logger.info(f"   Total Properties: {total_properties:,}")
        self.logger.info(f"   Total Value: ${total_value:,.0f}")
        self.logger.info(f"   Average per Owner: {total_properties/total_owners:.1f} properties, ${total_value/total_owners:,.0f}")


def test_owner_object_analyzer():
    """Test the Owner Object Analyzer with sample data."""
    
    # Create sample data
    sample_data = {
        'Property address': [
            '123 Main St, Miami, FL',
            '456 Oak Ave, Miami, FL', 
            '789 Pine St, Miami, FL',
            '123 Main St, Miami, FL',  # Same as first (multiple properties)
            '321 Elm St, Miami, FL'
        ],
        'Mailing address': [
            '123 Main St, Miami, FL',  # Same as property (individual)
            '999 Business Blvd, Miami, FL',  # Different (business)
            '789 Pine St, Miami, FL',  # Same as property (individual)
            '123 Main St, Miami, FL',  # Same as property (individual)
            '321 Elm St, Miami, FL'  # Same as property (individual)
        ],
        'First Name': ['John', '', 'Mary', 'John', 'Bob'],
        'Last Name': ['Smith', '', 'Johnson', 'Smith', 'Wilson'],
        'Business Name': ['ABC Properties LLC', 'XYZ Holdings LLC', '', 'ABC Properties LLC', ''],
        'Estimated value': [500000, 750000, 300000, 600000, 400000]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Analyze
    analyzer = OwnerObjectAnalyzer()
    owner_objects, df_enhanced = analyzer.analyze_dataset(df)
    
    # Display results
    print("\n🏠 OWNER OBJECT ANALYSIS RESULTS:")
    print("=" * 60)
    
    for i, obj in enumerate(owner_objects, 1):
        print(f"\nOwner {i}:")
        print(f"  Individual: '{obj.individual_name}'")
        print(f"  Business: '{obj.business_name}'")
        print(f"  Seller 1: '{obj.seller1_name}'")
        print(f"  Skip Trace: '{obj.skip_trace_target}'")
        print(f"  Confidence: {obj.confidence_score:.1f}")
        print(f"  Properties: {obj.property_count}")
        print(f"  Total Value: ${obj.total_property_value:,.0f}")
    
    print(f"\n📊 ENHANCED DATAFRAME COLUMNS:")
    print(f"   {list(df_enhanced.columns)}")
    
    return owner_objects, df_enhanced


if __name__ == "__main__":
    test_owner_object_analyzer() 