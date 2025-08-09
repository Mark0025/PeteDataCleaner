#!/usr/bin/env python3
"""
🎯 Pete Header Mapper

Utility to map processed data to Pete's expected headers and validate exports.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from loguru import logger

class PeteHeaderMapper:
    """
    Maps processed data to Pete's expected headers and validates exports.
    """
    
    # Pete's expected headers (you can update this based on your template)
    PETE_HEADERS = [
        "Seller 1",
        "Seller 1 Phone",
        "Seller 1 Email",
        "Seller 2", 
        "Seller 2 Phone",
        "Seller 2 Email",
        "Property Address", 
        "Property City",
        "Property State", 
        "Property Zip",
        "Phone 1",
        "Phone 2", 
        "Phone 3",
        "Phone 4",
        "Phone 5",
        "Property Type",
        "Bedrooms",
        "Bathrooms",
        "Square Feet",
        "Lot Size",
        "Year Built",
        "Property Value",
        "Notes"
    ]
    
    def __init__(self):
        self.mapping_rules = {}
        self.validation_results = {}
    
    def analyze_data_headers(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Analyze the headers in your processed data.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dict with analysis of headers
        """
        current_headers = list(df.columns)
        
        analysis = {
            'total_columns': len(current_headers),
            'phone_columns': [col for col in current_headers if 'phone' in col.lower()],
            'address_columns': [col for col in current_headers if 'address' in col.lower() or 'street' in col.lower()],
            'property_columns': [col for col in current_headers if 'property' in col.lower()],
            'contact_columns': [col for col in current_headers if any(word in col.lower() for word in ['email', 'phone', 'contact'])],
            'all_headers': current_headers
        }
        
        return analysis
    
    def suggest_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Suggest mapping from current headers to Pete headers.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dict mapping current headers to Pete headers
        """
        current_headers_lower = [col.lower() for col in df.columns]
        mapping = {}
        
        # Phone mapping
        phone_cols = [col for col in df.columns if 'phone' in col.lower() and col.count(' ') == 1]
        for i, pete_phone in enumerate(['Phone 1', 'Phone 2', 'Phone 3', 'Phone 4', 'Phone 5']):
            if i < len(phone_cols):
                mapping[phone_cols[i]] = pete_phone
        
        # Address mapping - find the actual column name
        if 'property address' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'property address'][0]
            mapping[actual_col] = 'Property Address'
        elif 'mailing address' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'mailing address'][0]
            mapping[actual_col] = 'Property Address'
        
        # City mapping
        if 'property city' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'property city'][0]
            mapping[actual_col] = 'Property City'
        
        # State mapping
        if 'property state' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'property state'][0]
            mapping[actual_col] = 'Property State'
        
        # Zip mapping
        if 'property zip' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'property zip'][0]
            mapping[actual_col] = 'Property Zip'
        elif 'property zip5' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'property zip5'][0]
            mapping[actual_col] = 'Property Zip'
        
        # Contact mapping - find email and phone columns for sellers
        email_cols = [col for col in df.columns if 'email' in col.lower() and col.count(' ') == 1]
        phone_cols = [col for col in df.columns if 'phone' in col.lower() and col.count(' ') == 1]
        
        if email_cols:
            mapping['email_concatenated'] = 'Seller 1 Email'  # Will be handled in create_pete_ready_dataframe
        
        if phone_cols:
            mapping['phone_concatenated'] = 'Seller 1 Phone'  # Will be handled in create_pete_ready_dataframe
        
        # Property Type mapping
        if 'structure type' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'structure type'][0]
            mapping[actual_col] = 'Property Type'
        
        # Bedrooms mapping
        if 'bedrooms' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'bedrooms'][0]
            mapping[actual_col] = 'Bedrooms'
        
        # Bathrooms mapping
        if 'bathrooms' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'bathrooms'][0]
            mapping[actual_col] = 'Bathrooms'
        
        # Square Feet mapping
        if 'sqft' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'sqft'][0]
            mapping[actual_col] = 'Square Feet'
        
        # Lot Size mapping
        if 'lot size' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'lot size'][0]
            mapping[actual_col] = 'Lot Size'
        
        # Year Built mapping
        if 'year' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'year'][0]
            mapping[actual_col] = 'Year Built'
        
        # Property Value mapping
        if 'estimated value' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'estimated value'][0]
            mapping[actual_col] = 'Property Value'
        
        # Notes mapping
        if 'messages' in current_headers_lower:
            actual_col = [col for col in df.columns if col.lower() == 'messages'][0]
            mapping[actual_col] = 'Notes'
        
        return mapping
    
    def create_pete_ready_dataframe(self, df: pd.DataFrame, mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Create a Pete-ready DataFrame with correct headers.
        
        Args:
            df: Processed DataFrame
            mapping: Optional custom mapping
            
        Returns:
            Pete-ready DataFrame
        """
        if mapping is None:
            mapping = self.suggest_mapping(df)
        
        # Create new DataFrame with Pete headers
        pete_df = pd.DataFrame(columns=self.PETE_HEADERS)
        
        # Handle special concatenation cases
        # 1. Seller 1 = First Name + Last Name
        if 'First Name' in df.columns and 'Last Name' in df.columns:
            pete_df['Seller 1'] = df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')
            pete_df['Seller 1'] = pete_df['Seller 1'].str.strip()
            print(f"✅ Concatenated Seller 1: First Name + Last Name ({len(pete_df['Seller 1'].dropna())} values)")
        
        # 2. Seller 1 Email = Email 1 + Email 2 + Email 3 + Email 4 + Email 5
        email_cols = [col for col in df.columns if 'email' in col.lower() and col.count(' ') == 1]
        if email_cols:
            email_data = []
            for _, row in df.iterrows():
                emails = []
                for email_col in email_cols[:5]:  # Max 5 emails
                    if pd.notna(row[email_col]) and str(row[email_col]).strip():
                        emails.append(str(row[email_col]).strip())
                email_data.append('; '.join(emails) if emails else None)
            pete_df['Seller 1 Email'] = email_data
            print(f"✅ Concatenated Seller 1 Email: {len(email_cols)} email columns ({len(pete_df['Seller 1 Email'].dropna())} values)")
        
        # 3. Seller 1 Phone = Best phone from Phone 1-5
        phone_cols = [col for col in df.columns if 'phone' in col.lower() and col.count(' ') == 1]
        if phone_cols:
            # Use Phone 1 as the primary seller phone
            pete_df['Seller 1 Phone'] = df['Phone 1'] if 'Phone 1' in df.columns else None
            print(f"✅ Mapped Seller 1 Phone: Phone 1 ({len(pete_df['Seller 1 Phone'].dropna())} values)")
        
        # Map data from original DataFrame
        for current_col, pete_col in mapping.items():
            if current_col in df.columns and pete_col in self.PETE_HEADERS:
                pete_df[pete_col] = df[current_col]
                print(f"✅ Mapped {current_col} ({len(df[current_col].dropna())} values) → {pete_col}")
        
        # Standardize Property Type
        if 'Property Type' in pete_df.columns:
            from backend.utils.data_standardizer_enhanced import standardize_property_types
            pete_df = standardize_property_types(pete_df, 'Property Type')
            print(f"✅ Standardized Property Type")
        
        # Fill remaining Pete headers with empty columns
        for pete_col in self.PETE_HEADERS:
            if pete_col not in pete_df.columns:
                pete_df[pete_col] = None
        
        return pete_df
    

    
    def validate_pete_export(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate that DataFrame is ready for Pete import.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validation results
        """
        validation = {
            'has_required_headers': True,
            'missing_headers': [],
            'phone_validation': {},
            'data_quality': {},
            'ready_for_pete': True
        }
        
        # Check required headers
        current_headers = list(df.columns)
        missing_headers = [header for header in self.PETE_HEADERS if header not in current_headers]
        validation['missing_headers'] = missing_headers
        
        if missing_headers:
            validation['has_required_headers'] = False
            validation['ready_for_pete'] = False
        
        # Validate phone columns
        phone_cols = [col for col in current_headers if col.startswith('Phone ')]
        validation['phone_validation'] = {
            'phone_columns_found': len(phone_cols),
            'phone_columns_expected': 5,
            'phone_data_count': sum(len(df[col].dropna()) for col in phone_cols if col in df.columns)
        }
        
        # Data quality checks
        validation['data_quality'] = {
            'total_rows': len(df),
            'rows_with_address': len(df['Property Address'].dropna()) if 'Property Address' in df.columns else 0,
            'rows_with_phones': len(df[phone_cols].dropna(how='all')) if phone_cols else 0,
            'rows_with_email': len(df['Email'].dropna()) if 'Email' in df.columns else 0
        }
        
        return validation
    
    def export_for_pete(self, df: pd.DataFrame, filename: str, format: str = 'xlsx') -> str:
        """
        Export DataFrame in Pete-ready format.
        
        Args:
            df: DataFrame to export
            filename: Output filename
            format: 'xlsx' or 'csv'
            
        Returns:
            Path to exported file
        """
        # Validate first
        validation = self.validate_pete_export(df)
        
        if not validation['ready_for_pete']:
            logger.warning(f"Data not ready for Pete: {validation['missing_headers']}")
        
        # Export
        if format.lower() == 'xlsx':
            try:
                df.to_excel(filename, index=False, engine='openpyxl')
                logger.info(f"✅ Pete-ready Excel export: {filename}")
            except Exception as e:
                logger.error(f"Excel export failed: {e}")
                # Fallback to CSV
                csv_filename = filename.replace('.xlsx', '.csv')
                df.to_csv(csv_filename, index=False)
                logger.info(f"✅ Pete-ready CSV export: {csv_filename}")
                return csv_filename
        else:
            df.to_csv(filename, index=False)
            logger.info(f"✅ Pete-ready CSV export: {filename}")
        
        return filename
    
    def print_validation_report(self, validation: Dict[str, any]):
        """Print a detailed validation report."""
        print("\n" + "="*60)
        print("🎯 PETE IMPORT VALIDATION REPORT")
        print("="*60)
        
        if validation['ready_for_pete']:
            print("✅ Data is ready for Pete import!")
        else:
            print("❌ Data needs adjustments before Pete import")
            print(f"   Missing headers: {validation['missing_headers']}")
        
        print(f"\n📊 Data Quality:")
        quality = validation['data_quality']
        print(f"   Total rows: {quality['total_rows']:,}")
        print(f"   Rows with address: {quality['rows_with_address']:,}")
        print(f"   Rows with phones: {quality['rows_with_phones']:,}")
        print(f"   Rows with email: {quality['rows_with_email']:,}")
        
        print(f"\n📞 Phone Validation:")
        phone_val = validation['phone_validation']
        print(f"   Phone columns found: {phone_val['phone_columns_found']}/5")
        print(f"   Phone data entries: {phone_val['phone_data_count']:,}")
        
        print("="*60)


# Convenience functions
def analyze_headers(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Analyze headers in DataFrame."""
    mapper = PeteHeaderMapper()
    return mapper.analyze_data_headers(df)


def create_pete_ready_export(df: pd.DataFrame, filename: str) -> str:
    """Create Pete-ready export with validation."""
    mapper = PeteHeaderMapper()
    
    # Analyze current headers
    analysis = mapper.analyze_data_headers(df)
    print(f"📊 Found {analysis['total_columns']} columns")
    print(f"📱 Phone columns: {len(analysis['phone_columns'])}")
    print(f"🏠 Address columns: {len(analysis['address_columns'])}")
    
    # Show address columns found
    if analysis['address_columns']:
        print(f"🏠 Address columns found: {analysis['address_columns']}")
    
    # Suggest mapping
    mapping = mapper.suggest_mapping(df)
    print(f"🗺️  Suggested mapping: {len(mapping)} columns")
    
    # Show the actual mapping
    if mapping:
        print(f"🗺️  Mapping details:")
        for source, target in mapping.items():
            print(f"   {source} → {target}")
    
    # Create Pete-ready DataFrame
    pete_df = mapper.create_pete_ready_dataframe(df, mapping)
    
    # Validate
    validation = mapper.validate_pete_export(pete_df)
    mapper.print_validation_report(validation)
    
    # Export
    return mapper.export_for_pete(pete_df, filename)


if __name__ == "__main__":
    # Example usage
    print("🎯 Pete Header Mapper - Example Usage")
    print("Use create_pete_ready_export() to process your data for Pete import") 