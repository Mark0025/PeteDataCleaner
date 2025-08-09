#!/usr/bin/env python3
"""
Smart Seller Creator

Creates Seller 1-5 from address duplicates while applying phone prioritization.
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
from loguru import logger

from backend.utils.high_performance_processor import prioritize_phones_fast
from backend.utils.progress_tracker import track_smart_seller_creation


class SmartSellerCreator:
    """
    Creates smart seller groups from address duplicates.
    
    Logic:
    1. Group by Property Address
    2. For each group:
       - If identical rows → DEDUPE
       - If different sellers → CREATE Seller 1,2,3,4,5
       - Apply phone prioritization to each seller
    3. Return Pete-ready DataFrame
    """
    
    def __init__(self):
        self.stats = {
            'total_records': 0,
            'address_groups': 0,
            'full_duplicates_removed': 0,
            'seller_groups_created': 0,
            'properties_with_multiple_sellers': 0
        }
    
    def create_seller_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create seller groups from address duplicates.

        Args:
            df: Input DataFrame with property data

        Returns:
            DataFrame with Seller 1-5 structure
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided to SmartSellerCreator")
            return df

        self.stats['total_records'] = len(df)
        
        # Initialize progress tracker
        progress = track_smart_seller_creation(len(df))
        
        logger.info(f"🔄 Starting smart seller creation for {len(df):,} records")
        
        # Step 1: Group by Property Address
        address_groups = self._group_by_address(df)
        self.stats['address_groups'] = len(address_groups)
        
        # Step 2: Process each address group
        processed_groups = []
        for address, group in address_groups.items():
            processed_group = self._process_address_group(address, group)
            processed_groups.append(processed_group)
        
        # Step 3: Combine all processed groups
        result_df = pd.concat(processed_groups, ignore_index=True)
        
        logger.info(f"✅ Smart seller creation complete:")
        logger.info(f"   📊 Total records: {self.stats['total_records']:,}")
        logger.info(f"   🏠 Address groups: {self.stats['address_groups']:,}")
        logger.info(f"   🗑️  Full duplicates removed: {self.stats['full_duplicates_removed']:,}")
        logger.info(f"   👤 Seller groups created: {self.stats['seller_groups_created']:,}")
        logger.info(f"   🏘️  Properties with multiple sellers: {self.stats['properties_with_multiple_sellers']:,}")
        
        return result_df
    
    def _group_by_address(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Group DataFrame by Property Address."""
        if 'Property address' not in df.columns:
            logger.warning("Property address column not found, using Property Address")
            address_col = 'Property Address'
        else:
            address_col = 'Property address'
        
        groups = {}
        for address, group in df.groupby(address_col):
            if pd.isna(address) or str(address).strip() == '':
                continue
            groups[str(address)] = group
        
        return groups
    
    def _process_address_group(self, address: str, group: pd.DataFrame) -> pd.DataFrame:
        """
        Process a single address group.
        
        Args:
            address: Property address
            group: DataFrame group for this address
            
        Returns:
            Processed DataFrame with Seller 1-5 structure
        """
        if len(group) == 1:
            # Single record - no processing needed
            return group
        
        # Check if these are full duplicates (same seller + same phones)
        if self._are_full_duplicates(group):
            # Remove duplicates, keep first
            self.stats['full_duplicates_removed'] += len(group) - 1
            logger.debug(f"🗑️  Removed {len(group) - 1} full duplicates for address: {address}")
            return group.head(1)
        
        # Different sellers at same address - create Seller 1-5
        self.stats['properties_with_multiple_sellers'] += 1
        return self._create_seller_group(address, group)
    
    def _are_full_duplicates(self, group: pd.DataFrame) -> bool:
        """
        Check if all rows in group are identical (same seller + same phones).
        
        Args:
            group: DataFrame group to check
            
        Returns:
            True if all rows are identical
        """
        # Create seller identifier
        group_copy = group.copy()
        group_copy['seller_id'] = (
            group_copy['First Name'].fillna('') + ' ' + 
            group_copy['Last Name'].fillna('')
        ).str.strip()
        
        # Get phone columns
        phone_cols = [col for col in group_copy.columns if 'Phone' in col and col.count(' ') == 1]
        
        # Create comparison key
        comparison_cols = ['seller_id'] + phone_cols[:5]  # First 5 phones
        
        # Check if all rows are identical
        return group_copy[comparison_cols].duplicated().all()
    
    def _create_seller_group(self, address: str, group: pd.DataFrame) -> pd.DataFrame:
        """
        Create Seller 1-5 from address group with different sellers.
        
        Args:
            address: Property address
            group: DataFrame group with different sellers
            
        Returns:
            DataFrame with Seller 1-5 structure
        """
        logger.debug(f"👤 Creating seller group for address: {address} ({len(group)} sellers)")
        
        # Create seller identifier for each row
        group_copy = group.copy()
        group_copy['seller_id'] = (
            group_copy['First Name'].fillna('') + ' ' + 
            group_copy['Last Name'].fillna('')
        ).str.strip()
        
        # Get unique sellers
        unique_sellers = group_copy['seller_id'].unique()
        
        # Create result DataFrame with Seller 1-5 structure
        result_df = pd.DataFrame()
        
        # Copy property information from first row
        property_cols = [
            'Property address', 'Property city', 'Property state', 'Property zip',
            'Structure type', 'Bedrooms', 'Bathrooms', 'Sqft', 'Lot size', 'Year', 'Estimated value'
        ]
        
        first_row = group_copy.iloc[0]
        for col in property_cols:
            if col in first_row:
                result_df[col] = [first_row[col]]
        
        # Create Seller 1-5
        for i, seller_id in enumerate(unique_sellers[:5], 1):  # Max 5 sellers
            seller_data = group_copy[group_copy['seller_id'] == seller_id].iloc[0]
            
            # Create seller name
            result_df[f'Seller {i}'] = [seller_id]
            
            # Apply phone prioritization for this seller
            seller_phones = self._prioritize_seller_phones(seller_data)
            for phone_num, phone_value in seller_phones.items():
                result_df[phone_num] = [phone_value]
            
            # Concatenate emails for this seller
            seller_emails = self._concatenate_seller_emails(seller_data)
            result_df[f'Seller {i} Email'] = [seller_emails]
            
            # Use best phone as seller phone
            best_phone = seller_phones.get('Phone 1', '')
            result_df[f'Seller {i} Phone'] = [best_phone]
        
        self.stats['seller_groups_created'] += 1
        return result_df
    
    def _prioritize_seller_phones(self, seller_data: pd.Series) -> Dict[str, str]:
        """
        Prioritize phones for a single seller using existing phone prioritizer.
        
        Args:
            seller_data: Series containing seller's phone data
            
        Returns:
            Dict mapping Phone 1-5 to prioritized phone numbers
        """
        # Create a single-row DataFrame for phone prioritization
        phone_df = pd.DataFrame([seller_data])
        
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
            logger.warning(f"Phone prioritization failed for seller: {e}")
            # Fallback: use first 5 phones
            result = {}
            for i in range(1, 6):
                phone_col = f'Phone {i}'
                if phone_col in seller_data:
                    result[phone_col] = seller_data[phone_col]
                else:
                    result[phone_col] = ''
            return result
    
    def _concatenate_seller_emails(self, seller_data: pd.Series) -> str:
        """
        Concatenate emails for a single seller.
        
        Args:
            seller_data: Series containing seller's email data
            
        Returns:
            Concatenated email string
        """
        email_cols = [col for col in seller_data.index if 'Email' in col and col.count(' ') == 1]
        emails = []
        
        for email_col in email_cols[:5]:  # Max 5 emails
            email_value = seller_data[email_col]
            if pd.notna(email_value) and str(email_value).strip():
                emails.append(str(email_value).strip())
        
        return '; '.join(emails) if emails else ''
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.stats.copy()


def create_seller_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to create seller groups.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with Seller 1-5 structure
    """
    creator = SmartSellerCreator()
    return creator.create_seller_groups(df) 