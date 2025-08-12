#!/usr/bin/env python3
"""
Owner Identifier

Identifies and analyzes property ownership patterns.
"""

from typing import Dict, List, Set
import pandas as pd
from loguru import logger


class OwnerIdentifier:
    """
    Identifies and analyzes property ownership patterns.
    """
    
    def __init__(self):
        self.ownership_patterns = {}
    
    def identify_owners(self, df: pd.DataFrame) -> Dict:
        """
        Identify ownership patterns in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with ownership analysis
        """
        logger.info("🔍 Identifying ownership patterns...")
        
        # Find mailing address column
        mailing_col = self._find_mailing_address_column(df)
        if not mailing_col:
            logger.warning("No mailing address column found for ownership analysis")
            return {}
        
        # Group by mailing address
        ownership_groups = df.groupby(mailing_col)
        
        analysis = {
            'total_records': len(df),
            'unique_owners': len(ownership_groups),
            'ownership_distribution': {},
            'owners_with_multiple_properties': 0,
            'max_properties_per_owner': 0,
            'sample_owners': []
        }
        
        # Analyze each owner group
        for mailing_address, group in ownership_groups.items():
            if pd.isna(mailing_address) or str(mailing_address).strip() == '':
                continue
                
            property_count = len(group)
            analysis['ownership_distribution'][str(mailing_address)] = property_count
            
            if property_count > 1:
                analysis['owners_with_multiple_properties'] += 1
                analysis['max_properties_per_owner'] = max(
                    analysis['max_properties_per_owner'], 
                    property_count
                )
                
                # Add sample for owners with multiple properties
                if len(analysis['sample_owners']) < 5:
                    analysis['sample_owners'].append({
                        'mailing_address': str(mailing_address),
                        'property_count': property_count,
                        'properties': group['Property address'].tolist() if 'Property address' in group.columns else []
                    })
        
        logger.info(f"✅ Ownership analysis complete: {analysis['unique_owners']} unique owners identified")
        return analysis
    
    def _find_mailing_address_column(self, df: pd.DataFrame) -> str:
        """Find the mailing address column in the DataFrame."""
        mailing_cols = [
            'Mailing address', 'Mailing Address', 'Mailing_address',
            'Owner address', 'Owner Address', 'Owner_address',
            'Correspondence address', 'Correspondence Address'
        ]
        
        for col in mailing_cols:
            if col in df.columns:
                return col
        
        return None
    
    def detect_business_entities(self, df: pd.DataFrame) -> Dict:
        """
        Detect business entities in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with business entity analysis
        """
        logger.info("🏢 Detecting business entities...")
        
        # Look for business indicators in various columns
        business_indicators = [
            'LLC', 'Ltd', 'Inc', 'Corp', 'Corporation', 'Company', 'Co',
            'Trust', 'Foundation', 'Partnership', 'Associates', 'Group',
            'Real Estate', 'Properties', 'Investments', 'Holdings'
        ]
        
        business_entities = []
        business_count = 0
        
        # Check owner name columns
        name_cols = [
            'First Name', 'Last Name', 'Owner First Name', 'Owner Last Name',
            'Owner Name', 'Name'
        ]
        
        for idx, row in df.iterrows():
            is_business = False
            business_name = None
            
            # Check if any name column contains business indicators
            for col in name_cols:
                if col in row and pd.notna(row[col]):
                    name_value = str(row[col]).upper()
                    for indicator in business_indicators:
                        if indicator.upper() in name_value:
                            is_business = True
                            business_name = row[col]
                            break
                    if is_business:
                        break
            
            if is_business:
                business_count += 1
                business_entities.append({
                    'row_index': idx,
                    'business_name': business_name,
                    'mailing_address': self._get_mailing_address(row),
                    'property_address': self._get_property_address(row)
                })
        
        analysis = {
            'business_count': business_count,
            'business_percentage': (business_count / len(df)) * 100 if len(df) > 0 else 0,
            'business_entities': business_entities[:10],  # Limit to first 10
            'total_entities': len(df)
        }
        
        logger.info(f"✅ Business entity detection complete: {business_count} business entities found")
        return analysis
    
    def _get_mailing_address(self, row: pd.Series) -> str:
        """Get mailing address from row."""
        mailing_cols = [
            'Mailing address', 'Mailing Address', 'Mailing_address',
            'Owner address', 'Owner Address', 'Owner_address'
        ]
        
        for col in mailing_cols:
            if col in row and pd.notna(row[col]):
                return str(row[col])
        
        return "Unknown"
    
    def _get_property_address(self, row: pd.Series) -> str:
        """Get property address from row."""
        property_cols = [
            'Property address', 'Property Address', 'Property_address',
            'Address', 'address'
        ]
        
        for col in property_cols:
            if col in row and pd.notna(row[col]):
                return str(row[col])
        
        return "Unknown"
