#!/usr/bin/env python3
"""
Seller Structure Builder

Creates Pete-ready Seller 1-5 structure from owner groups.
"""

from typing import Dict, List, Optional
import pandas as pd
from loguru import logger


class SellerStructureBuilder:
    """
    Builds Seller 1-5 structure for Pete export.
    """
    
    def __init__(self):
        self.seller_structure = {}
    
    def build_seller_structure(self, owner_groups: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Build Seller 1-5 structure from owner groups.
        
        Args:
            owner_groups: Dictionary of mailing address -> DataFrame groups
            
        Returns:
            DataFrame with Seller 1-5 structure
        """
        logger.info("🏗️ Building Seller 1-5 structure...")
        
        result_rows = []
        
        for mailing_address, group in owner_groups.items():
            if len(group) == 1:
                # Single property - create basic seller structure
                seller_row = self._create_single_seller_row(group.iloc[0], mailing_address)
                result_rows.append(seller_row)
            else:
                # Multiple properties - create Seller 1-5 structure
                seller_row = self._create_multi_seller_row(group, mailing_address)
                result_rows.append(seller_row)
        
        result_df = pd.DataFrame(result_rows)
        logger.info(f"✅ Seller structure built: {len(result_df)} rows created")
        
        return result_df
    
    def _create_single_seller_row(self, row: pd.Series, mailing_address: str) -> Dict:
        """Create seller row for single property owner."""
        seller_row = {
            'Mailing Address': mailing_address,
            'Seller 1': self._get_owner_name(row),
            'Seller 1 Phone': self._get_best_phone(row),
            'Seller 1 Email': self._get_emails(row),
            'Property 1': self._get_property_address(row),
            'Phone 1': self._get_best_phone(row),
            'Phone 2': self._get_second_phone(row),
            'Phone 3': self._get_third_phone(row),
            'Phone 4': self._get_fourth_phone(row),
            'Phone 5': self._get_fifth_phone(row)
        }
        
        # Add additional property information
        property_info = self._extract_property_info(row)
        seller_row.update(property_info)
        
        return seller_row
    
    def _create_multi_seller_row(self, group: pd.DataFrame, mailing_address: str) -> Dict:
        """Create Seller 1-5 row for owner with multiple properties."""
        seller_row = {
            'Mailing Address': mailing_address,
            'Owner Name': self._get_owner_name(group.iloc[0])
        }
        
        # Create Seller 1-5 from different properties
        for i, (idx, property_data) in enumerate(group.iterrows(), 1):
            if i > 5:  # Max 5 sellers
                break
                
            seller_row[f'Seller {i}'] = self._get_owner_name(property_data)
            seller_row[f'Seller {i} Phone'] = self._get_best_phone(property_data)
            seller_row[f'Seller {i} Email'] = self._get_emails(property_data)
            seller_row[f'Property {i}'] = self._get_property_address(property_data)
            
            # Add phones for this seller
            seller_row[f'Phone {i}'] = self._get_best_phone(property_data)
        
        # Add property information from first property
        property_info = self._extract_property_info(group.iloc[0])
        seller_row.update(property_info)
        
        return seller_row
    
    def _get_owner_name(self, row: pd.Series) -> str:
        """Extract owner name from row."""
        name_parts = []
        
        # Try different name column combinations
        if 'First Name' in row and pd.notna(row['First Name']):
            name_parts.append(str(row['First Name']))
        if 'Last Name' in row and pd.notna(row['Last Name']):
            name_parts.append(str(row['Last Name']))
        
        if not name_parts:
            # Fallback to owner columns
            if 'Owner First Name' in row and pd.notna(row['Owner First Name']):
                name_parts.append(str(row['Owner First Name']))
            if 'Owner Last Name' in row and pd.notna(row['Owner Last Name']):
                name_parts.append(str(row['Owner Last Name']))
        
        return ' '.join(name_parts) if name_parts else "Unknown Owner"
    
    def _get_best_phone(self, row: pd.Series) -> str:
        """Get the best phone number from row."""
        phone_cols = [col for col in row.index if 'Phone' in col and col.count(' ') == 1]
        
        for i in range(1, 6):
            phone_col = f'Phone {i}'
            if phone_col in phone_cols and pd.notna(row[phone_col]):
                return str(row[phone_col])
        
        return ""
    
    def _get_second_phone(self, row: pd.Series) -> str:
        """Get the second best phone number."""
        return self._get_phone_by_position(row, 2)
    
    def _get_third_phone(self, row: pd.Series) -> str:
        """Get the third best phone number."""
        return self._get_phone_by_position(row, 3)
    
    def _get_fourth_phone(self, row: pd.Series) -> str:
        """Get the fourth best phone number."""
        return self._get_phone_by_position(row, 4)
    
    def _get_fifth_phone(self, row: pd.Series) -> str:
        """Get the fifth best phone number."""
        return self._get_phone_by_position(row, 5)
    
    def _get_phone_by_position(self, row: pd.Series, position: int) -> str:
        """Get phone number by position."""
        phone_col = f'Phone {position}'
        if phone_col in row and pd.notna(row[phone_col]):
            return str(row[phone_col])
        return ""
    
    def _get_emails(self, row: pd.Series) -> str:
        """Extract and concatenate emails from row."""
        email_cols = [col for col in row.index if 'Email' in col and col.count(' ') == 1]
        emails = []
        
        for email_col in email_cols[:5]:  # Max 5 emails
            email_value = row[email_col]
            if pd.notna(email_value) and str(email_value).strip():
                emails.append(str(email_value).strip())
        
        return '; '.join(emails) if emails else ""
    
    def _get_property_address(self, row: pd.Series) -> str:
        """Get property address from row."""
        property_cols = [
            'Property address', 'Property Address', 'Property_address',
            'Address', 'address'
        ]
        
        for col in property_cols:
            if col in row and pd.notna(row[col]):
                return str(row[col])
        
        return "Unknown Property"
    
    def _extract_property_info(self, row: pd.Series) -> Dict:
        """Extract additional property information."""
        property_info = {}
        
        # Property details
        property_cols = [
            'Structure type', 'Bedrooms', 'Bathrooms', 'Sqft', 'Lot size',
            'Year', 'Estimated value', 'Property city', 'Property state', 'Property zip'
        ]
        
        for col in property_cols:
            if col in row and pd.notna(row[col]):
                property_info[col] = row[col]
        
        return property_info
    
    def validate_seller_structure(self, df: pd.DataFrame) -> Dict:
        """
        Validate the Seller 1-5 structure.
        
        Args:
            df: DataFrame with Seller structure
            
        Returns:
            Validation results
        """
        logger.info("🔍 Validating Seller structure...")
        
        validation = {
            'total_rows': len(df),
            'rows_with_seller_1': 0,
            'rows_with_multiple_sellers': 0,
            'missing_phone_numbers': 0,
            'missing_emails': 0,
            'validation_errors': []
        }
        
        for idx, row in df.iterrows():
            # Check Seller 1
            if 'Seller 1' in row and pd.notna(row['Seller 1']):
                validation['rows_with_seller_1'] += 1
            else:
                validation['validation_errors'].append(f"Row {idx}: Missing Seller 1")
            
            # Check for multiple sellers
            seller_count = 0
            for i in range(1, 6):
                seller_col = f'Seller {i}'
                if seller_col in row and pd.notna(row[seller_col]):
                    seller_count += 1
            
            if seller_count > 1:
                validation['rows_with_multiple_sellers'] += 1
            
            # Check phone numbers
            if 'Phone 1' in row and pd.notna(row['Phone 1']):
                pass  # Has at least one phone
            else:
                validation['missing_phone_numbers'] += 1
                validation['validation_errors'].append(f"Row {idx}: Missing Phone 1")
            
            # Check emails
            if 'Seller 1 Email' in row and pd.notna(row['Seller 1 Email']):
                pass  # Has at least one email
            else:
                validation['missing_emails'] += 1
                validation['validation_errors'].append(f"Row {idx}: Missing Seller 1 Email")
        
        logger.info(f"✅ Validation complete: {validation['rows_with_seller_1']} valid seller rows")
        return validation
