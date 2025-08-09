#!/usr/bin/env python3
"""
Enhanced Data Standardizer

Provides utilities for data concatenation and standardization that can be used
in the app's frontend and backend components.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger

class DataStandardizerEnhanced:
    """
    Enhanced data standardizer with concatenation and standardization features.
    """
    
    def __init__(self):
        self.standardization_rules = {
            'property_type': {
                'single_family': [
                    'single family', 'sfr', 'single family residence', 'single family residential',
                    'single family home', 'single family house', 'sf', 'single fam'
                ],
                'multifamily': [
                    'duplex', 'duplex (2 units, any combination)', 'multifamily', 'multi family', 
                    'multi-family', 'multi family residential', 'apartment', 'condo', 'condominium', 
                    'townhouse', 'town house'
                ],
                'mobile': [
                    'mobile/manufactured home', 'mobile home', 'manufactured home'
                ],
                'commercial': [
                    'retail stores', 'commercial', 'business', 'office', 'industrial'
                ],
                'vacant': [
                    'residential - vacant land', 'residential-vacant land', 'vacant land', 'vacant'
                ]
            }
        }
    
    def concatenate_columns(self, df: pd.DataFrame, source_cols: List[str], 
                          target_col: str, separator: str = ' ', 
                          remove_empty: bool = True) -> pd.DataFrame:
        """
        Concatenate multiple columns into one.
        
        Args:
            df: Input DataFrame
            source_cols: List of source column names
            target_col: Target column name
            separator: Separator between values
            remove_empty: Whether to remove empty values
            
        Returns:
            DataFrame with concatenated column
        """
        if not source_cols:
            logger.warning("No source columns provided for concatenation")
            return df
        
        # Check which columns exist
        existing_cols = [col for col in source_cols if col in df.columns]
        if not existing_cols:
            logger.warning(f"None of the source columns {source_cols} exist in DataFrame")
            return df
        
        # Concatenate values
        concatenated_data = []
        for _, row in df.iterrows():
            values = []
            for col in existing_cols:
                if pd.notna(row[col]) and str(row[col]).strip():
                    values.append(str(row[col]).strip())
            
            if values:
                concatenated_data.append(separator.join(values))
            else:
                concatenated_data.append(None)
        
        # Add to DataFrame
        df_copy = df.copy()
        df_copy[target_col] = concatenated_data
        
        logger.info(f"✅ Concatenated {len(existing_cols)} columns into '{target_col}': {existing_cols}")
        return df_copy
    
    def concatenate_emails(self, df: pd.DataFrame, email_cols: List[str], 
                          target_col: str = 'Email', max_emails: int = 5) -> pd.DataFrame:
        """
        Concatenate multiple email columns into one with semicolon separation.
        
        Args:
            df: Input DataFrame
            email_cols: List of email column names
            target_col: Target column name
            max_emails: Maximum number of emails to include
            
        Returns:
            DataFrame with concatenated email column
        """
        if not email_cols:
            logger.warning("No email columns provided")
            return df
        
        # Check which columns exist
        existing_cols = [col for col in email_cols if col in df.columns]
        if not existing_cols:
            logger.warning(f"None of the email columns {email_cols} exist in DataFrame")
            return df
        
        # Concatenate emails
        email_data = []
        for _, row in df.iterrows():
            emails = []
            for email_col in existing_cols[:max_emails]:
                if pd.notna(row[email_col]) and str(row[email_col]).strip():
                    emails.append(str(row[email_col]).strip())
            email_data.append('; '.join(emails) if emails else None)
        
        # Add to DataFrame
        df_copy = df.copy()
        df_copy[target_col] = email_data
        
        logger.info(f"✅ Concatenated {len(existing_cols)} email columns into '{target_col}'")
        return df_copy
    
    def standardize_property_type(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Standardize property type values in a column.
        
        Args:
            df: Input DataFrame
            column: Column name to standardize
            
        Returns:
            DataFrame with standardized property type column
        """
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in DataFrame")
            return df
        
        df_copy = df.copy()
        series = df_copy[column]
        
        # Apply standardization rules
        single_family_patterns = self.standardization_rules['property_type']['single_family']
        multifamily_patterns = self.standardization_rules['property_type']['multifamily']
        mobile_patterns = self.standardization_rules['property_type']['mobile']
        commercial_patterns = self.standardization_rules['property_type']['commercial']
        vacant_patterns = self.standardization_rules['property_type']['vacant']
        
        # Apply standardization
        for pattern in single_family_patterns:
            mask = series.str.lower().str.contains(pattern, na=False)
            series[mask] = 'Single Family Residential'
        
        for pattern in multifamily_patterns:
            mask = series.str.lower().str.contains(pattern, na=False)
            series[mask] = 'Multifamily'
        
        for pattern in mobile_patterns:
            mask = series.str.lower().str.contains(pattern, na=False)
            series[mask] = 'Mobile/Manufactured Home'
        
        for pattern in commercial_patterns:
            mask = series.str.lower().str.contains(pattern, na=False)
            series[mask] = 'Commercial'
        
        for pattern in vacant_patterns:
            mask = series.str.lower().str.contains(pattern, na=False)
            series[mask] = 'Vacant Land'
        
        df_copy[column] = series
        
        logger.info(f"✅ Standardized property type column '{column}'")
        return df_copy
    
    def analyze_property_types(self, df: pd.DataFrame, column: str) -> Dict[str, int]:
        """
        Analyze property type values in a column.
        
        Args:
            df: Input DataFrame
            column: Column name to analyze
            
        Returns:
            Dictionary with property type counts
        """
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in DataFrame")
            return {}
        
        # Get unique values and counts
        value_counts = df[column].value_counts().to_dict()
        
        logger.info(f"📊 Property type analysis for '{column}': {len(value_counts)} unique values")
        return value_counts
    
    def suggest_standardization(self, df: pd.DataFrame, column: str) -> Dict[str, List[str]]:
        """
        Suggest standardization rules based on current values.
        
        Args:
            df: Input DataFrame
            column: Column name to analyze
            
        Returns:
            Dictionary with suggested standardization rules
        """
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in DataFrame")
            return {}
        
        # Get unique values
        unique_values = df[column].dropna().unique()
        
        # Analyze for property type patterns
        suggestions = {
            'single_family': [],
            'multifamily': [],
            'other': []
        }
        
        for value in unique_values:
            value_lower = str(value).lower()
            
            # Check for single family patterns
            if any(pattern in value_lower for pattern in ['single', 'sfr', 'sf']):
                suggestions['single_family'].append(str(value))
            # Check for multifamily patterns
            elif any(pattern in value_lower for pattern in ['multi', 'apartment', 'condo', 'townhouse']):
                suggestions['multifamily'].append(str(value))
            else:
                suggestions['other'].append(str(value))
        
        logger.info(f"📊 Standardization suggestions for '{column}': {len(unique_values)} unique values")
        return suggestions


# Convenience functions for easy integration
def concatenate_name_fields(df: pd.DataFrame, first_name_col: str = 'First Name', 
                           last_name_col: str = 'Last Name', target_col: str = 'Seller') -> pd.DataFrame:
    """Concatenate first and last name fields."""
    standardizer = DataStandardizerEnhanced()
    return standardizer.concatenate_columns(df, [first_name_col, last_name_col], target_col)


def concatenate_email_fields(df: pd.DataFrame, email_cols: List[str], 
                           target_col: str = 'Email') -> pd.DataFrame:
    """Concatenate multiple email fields."""
    standardizer = DataStandardizerEnhanced()
    return standardizer.concatenate_emails(df, email_cols, target_col)


def standardize_property_types(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Standardize property type values."""
    standardizer = DataStandardizerEnhanced()
    return standardizer.standardize_property_type(df, column)


def analyze_property_types(df: pd.DataFrame, column: str) -> Dict[str, int]:
    """Analyze property type values."""
    standardizer = DataStandardizerEnhanced()
    return standardizer.analyze_property_types(df, column)


if __name__ == "__main__":
    # Example usage
    print("🔧 Enhanced Data Standardizer - Example Usage")
    print("Use the convenience functions for easy integration in the app") 