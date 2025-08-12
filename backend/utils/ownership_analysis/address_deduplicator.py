#!/usr/bin/env python3
"""
Address Deduplicator

Groups records by Mailing Address to identify same owners with multiple properties.
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
from loguru import logger

from backend.utils.high_performance_processor import prioritize_phones_fast
from backend.utils.progress_tracker import track_smart_seller_creation


class AddressDeduplicator:
    """
    Deduplicates and groups records by Mailing Address.
    
    Logic:
    1. Group by Mailing Address (same owner, multiple properties)
    2. For each group:
       - If identical rows → DEDUPE
       - If different properties → CREATE Seller 1,2,3,4,5
       - Apply phone prioritization to each owner
    3. Return Pete-ready DataFrame
    """
    
    def __init__(self):
        self.stats = {
            'total_records': 0,
            'mailing_address_groups': 0,
            'full_duplicates_removed': 0,
            'owner_groups_created': 0,
            'owners_with_multiple_properties': 0
        }
    
    def deduplicate_by_mailing_address(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicate and group by Mailing Address.
        
        Args:
            df: Input DataFrame with property data
            
        Returns:
            DataFrame with Seller 1-5 structure grouped by owner
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided to AddressDeduplicator")
            return df
        
        self.stats['total_records'] = len(df)
        
        # Initialize progress tracker
        progress = track_smart_seller_creation(len(df))
        
        logger.info(f"🔄 Starting mailing address deduplication for {len(df):,} records")
        
        # Step 1: Group by Mailing Address (not Property Address!)
        mailing_groups = self._group_by_mailing_address(df)
        self.stats['mailing_address_groups'] = len(mailing_groups)
        
        # Step 2: Process each mailing address group
        processed_groups = []
        for mailing_address, group in mailing_groups.items():
            processed_group = self._process_mailing_group(mailing_address, group)
            processed_groups.append(processed_group)
        
        # Step 3: Combine all processed groups
        result_df = pd.concat(processed_groups, ignore_index=True)
        
        logger.info(f"✅ Mailing address deduplication complete:")
        logger.info(f"   📊 Total records: {self.stats['total_records']:,}")
        logger.info(f"   📮 Mailing address groups: {self.stats['mailing_address_groups']:,}")
        logger.info(f"   🗑️  Full duplicates removed: {self.stats['full_duplicates_removed']:,}")
        logger.info(f"   👤 Owner groups created: {self.stats['owner_groups_created']:,}")
        logger.info(f"   🏘️  Owners with multiple properties: {self.stats['owners_with_multiple_properties']:,}")
        
        return result_df
    
    def _group_by_mailing_address(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Group DataFrame by Mailing Address (not Property Address!)."""
        # Look for mailing address columns
        mailing_cols = [
            'Mailing address', 'Mailing Address', 'Mailing_address',
            'Owner address', 'Owner Address', 'Owner_address',
            'Correspondence address', 'Correspondence Address'
        ]
        
        mailing_col = None
        for col in mailing_cols:
            if col in df.columns:
                mailing_col = col
                break
        
        if mailing_col is None:
            logger.warning("No mailing address column found, using Property address as fallback")
            mailing_col = 'Property address'
        
        logger.info(f"📮 Grouping by mailing address column: {mailing_col}")
        
        groups = {}
        for address, group in df.groupby(mailing_col):
            if pd.isna(address) or str(address).strip() == '':
                continue
            groups[str(address)] = group
        
        return groups
    
    def _process_mailing_group(self, mailing_address: str, group: pd.DataFrame) -> pd.DataFrame:
        """
        Process a single mailing address group.
        
        Args:
            mailing_address: Mailing address (owner identifier)
            group: DataFrame group for this mailing address
            
        Returns:
            Processed DataFrame with Seller 1-5 structure
        """
        if len(group) == 1:
            # Single property - no processing needed
            return group
        
        # Check if these are full duplicates (same property + same owner + same phones)
        if self._are_full_duplicates(group):
            # Remove duplicates, keep first
            self.stats['full_duplicates_removed'] += len(group) - 1
            logger.debug(f"🗑️  Removed {len(group) - 1} full duplicates for mailing address: {mailing_address}")
            return group.head(1)
        
        # Different properties at same mailing address - create Seller 1-5
        self.stats['owners_with_multiple_properties'] += 1
        return self._create_owner_group(mailing_address, group)
    
    def _are_full_duplicates(self, group: pd.DataFrame) -> bool:
        """
        Check if all rows in group are identical (same property + same owner + same phones).
        
        Args:
            group: DataFrame group to check
            
        Returns:
            True if all rows are identical
        """
        # Create property identifier
        group_copy = group.copy()
        
        # Look for property address columns
        property_cols = [
            'Property address', 'Property Address', 'Property_address',
            'Address', 'address'
        ]
        
        property_col = None
        for col in property_cols:
            if col in group_copy.columns:
                property_col = col
                break
        
        if property_col is None:
            logger.warning("No property address column found for duplicate detection")
            return False
        
        # Create comparison key: property address + owner name + first few phones
        group_copy['property_id'] = group_copy[property_col].astype(str)
        
        # Get phone columns
        phone_cols = [col for col in group_copy.columns if 'Phone' in col and col.count(' ') == 1]
        
        # Create comparison key
        comparison_cols = ['property_id'] + phone_cols[:3]  # First 3 phones
        
        # Check if all rows are identical
        return group_copy[comparison_cols].duplicated().all()
    
    def _create_owner_group(self, mailing_address: str, group: pd.DataFrame) -> pd.DataFrame:
        """
        Create Seller 1-5 from mailing address group with different properties.
        
        Args:
            mailing_address: Mailing address (owner identifier)
            group: DataFrame group with different properties
            
        Returns:
            DataFrame with Seller 1-5 structure
        """
        logger.debug(f"👤 Creating owner group for mailing address: {mailing_address} ({len(group)} properties)")
        
        # Create result DataFrame with Seller 1-5 structure
        result_df = pd.DataFrame()
        
        # Copy mailing address information from first row
        mailing_cols = [
            'Mailing address', 'Mailing Address', 'Mailing_address',
            'Owner address', 'Owner Address', 'Owner_address',
            'Correspondence address', 'Correspondence Address'
        ]
        
        first_row = group.iloc[0]
        for col in mailing_cols:
            if col in first_row:
                result_df[col] = [first_row[col]]
        
        # Copy owner name information
        owner_cols = [
            'First Name', 'Last Name', 'Owner First Name', 'Owner Last Name',
            'Owner First', 'Owner Last'
        ]
        
        for col in owner_cols:
            if col in first_row:
                result_df[col] = [first_row[col]]
        
        # Create Seller 1-5 from different properties
        for i, (idx, property_data) in enumerate(group.iterrows(), 1):
            if i > 5:  # Max 5 sellers
                break
                
            # Create seller name
            seller_name = self._create_seller_name(property_data)
            result_df[f'Seller {i}'] = [seller_name]
            
            # Apply phone prioritization for this property
            property_phones = self._prioritize_property_phones(property_data)
            for phone_num, phone_value in property_phones.items():
                result_df[phone_num] = [phone_value]
            
            # Concatenate emails for this property
            property_emails = self._concatenate_property_emails(property_data)
            result_df[f'Seller {i} Email'] = [property_emails]
            
            # Use best phone as seller phone
            best_phone = property_phones.get('Phone 1', '')
            result_df[f'Seller {i} Phone'] = [best_phone]
            
            # Add property address for this seller
            property_cols = [
                'Property address', 'Property Address', 'Property_address',
                'Address', 'address'
            ]
            
            for col in property_cols:
                if col in property_data:
                    result_df[f'Seller {i} Property'] = [property_data[col]]
                    break
        
        self.stats['owner_groups_created'] += 1
        return result_df
    
    def _create_seller_name(self, property_data: pd.Series) -> str:
        """Create seller name from property data."""
        name_parts = []
        
        # Try different name column combinations
        if 'First Name' in property_data and pd.notna(property_data['First Name']):
            name_parts.append(str(property_data['First Name']))
        if 'Last Name' in property_data and pd.notna(property_data['Last Name']):
            name_parts.append(str(property_data['Last Name']))
        
        if not name_parts:
            # Fallback to owner columns
            if 'Owner First Name' in property_data and pd.notna(property_data['Owner First Name']):
                name_parts.append(str(property_data['Owner First Name']))
            if 'Owner Last Name' in property_data and pd.notna(property_data['Owner Last Name']):
                name_parts.append(str(property_data['Owner Last Name']))
        
        return ' '.join(name_parts) if name_parts else f"Owner {property_data.name}"
    
    def _prioritize_property_phones(self, property_data: pd.Series) -> Dict[str, str]:
        """
        Prioritize phones for a single property using fast processor.
        
        Args:
            property_data: Series containing property's phone data
            
        Returns:
            Dict mapping Phone 1-5 to prioritized phone numbers
        """
        # Create a single-row DataFrame for phone prioritization
        phone_df = pd.DataFrame([property_data])
        
        try:
            # Apply fast phone prioritization
            prioritized_df, _ = prioritize_phones_fast(phone_df, max_phones=5)
            
            # Extract Phone 1-5
            result = {}
            for i in range(1, 6):
                phone_col = f'Phone {i}'
                if phone_col in prioritized_df.columns and len(prioritized_df) > 0:
                    result[phone_col] = prioritized_df[phone_col].iloc[0]
                else:
                    result[phone_col] = ''
            
            return result
        except Exception as e:
            logger.warning(f"Phone prioritization failed for property: {e}")
            # Fallback: use first 5 phones
            result = {}
            for i in range(1, 6):
                phone_col = f'Phone {i}'
                if phone_col in property_data:
                    result[phone_col] = property_data[phone_col]
                else:
                    result[phone_col] = ''
            return result
    
    def _concatenate_property_emails(self, property_data: pd.Series) -> str:
        """
        Concatenate emails for a single property.
        
        Args:
            property_data: Series containing property's email data
            
        Returns:
            Concatenated email string
        """
        email_cols = [col for col in property_data.index if 'Email' in col and col.count(' ') == 1]
        emails = []
        
        for email_col in email_cols[:5]:  # Max 5 emails
            email_value = property_data[email_col]
            if pd.notna(email_value) and str(email_value).strip():
                emails.append(str(email_value).strip())
        
        return '; '.join(emails) if emails else ''
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.stats.copy()


def deduplicate_by_mailing_address(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to deduplicate by mailing address.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with Seller 1-5 structure grouped by owner
    """
    deduplicator = AddressDeduplicator()
    return deduplicator.deduplicate_by_mailing_address(df)
