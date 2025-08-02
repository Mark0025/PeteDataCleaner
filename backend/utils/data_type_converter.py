"""
Data Type Converter - Backend Utility

Utility class for converting data types with advanced options and logging.
Supports conversion for individual columns or entire DataFrames.

This is the authoritative backend implementation.
Frontend components should import and use this module.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional
from loguru import logger

class DataTypeConverter:
    """
    Utility class for converting data types with advanced options and logging.
    Supports conversion for individual columns or entire DataFrames.
    """
    
    @staticmethod
    def infer_type(series: pd.Series) -> str:
        """
        Intelligently infer the most appropriate data type for a series.
        
        Args:
            series (pd.Series): Input pandas Series to analyze
        
        Returns:
            str: Recommended data type ('int', 'float', 'datetime', 'category', 'string')
        """
        # Remove NaN values for type inference
        clean_series = series.dropna()
        
        if clean_series.empty:
            return 'string'  # Default to string if no non-null values
        
        # Check for datetime
        try:
            pd.to_datetime(clean_series)
            return 'datetime'
        except (ValueError, TypeError):
            pass
        
        # Check for integer
        try:
            converted = pd.to_numeric(clean_series, errors='raise')
            if np.all(converted.apply(float.is_integer)):
                return 'int'
        except (ValueError, TypeError):
            pass
        
        # Check for float
        try:
            pd.to_numeric(clean_series, errors='raise')
            return 'float'
        except (ValueError, TypeError):
            pass
        
        # Check for categorical (limited unique values)
        if len(clean_series.unique()) < min(len(clean_series) // 2, 20):
            return 'category'
        
        return 'string'
    
    @staticmethod
    def convert_column(
        series: pd.Series, 
        target_type: str, 
        errors: str = 'coerce', 
        format: Optional[str] = None
    ) -> pd.Series:
        """
        Convert a single column to a specified data type.
        
        Args:
            series (pd.Series): Input series to convert
            target_type (str): Target data type ('int', 'float', 'datetime', 'category', 'string')
            errors (str, optional): How to handle conversion errors. Defaults to 'coerce'.
            format (str, optional): Format for datetime parsing. Defaults to None.
        
        Returns:
            pd.Series: Converted series
        """
        logger.info(f"Converting column to {target_type}")
        
        try:
            if target_type == 'int':
                return pd.to_numeric(series, errors=errors).astype('Int64')  # Nullable integer
            
            elif target_type == 'float':
                return pd.to_numeric(series, errors=errors)
            
            elif target_type == 'datetime':
                return pd.to_datetime(series, errors=errors, format=format)
            
            elif target_type == 'category':
                return series.astype('category')
            
            elif target_type == 'string':
                return series.astype(str)
            
            else:
                logger.warning(f"Unsupported type: {target_type}. Returning original series.")
                return series
        
        except Exception as e:
            logger.error(f"Error converting column: {e}")
            if errors == 'raise':
                raise
            return series
    
    @staticmethod
    def convert_dataframe(
        df: pd.DataFrame, 
        column_types: Dict[str, str], 
        errors: str = 'coerce'
    ) -> pd.DataFrame:
        """
        Convert multiple columns in a DataFrame to specified types.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column_types (Dict[str, str]): Mapping of column names to target types
            errors (str, optional): How to handle conversion errors. Defaults to 'coerce'.
        
        Returns:
            pd.DataFrame: DataFrame with converted columns
        """
        logger.info(f"Converting DataFrame columns: {column_types}")
        
        converted_df = df.copy()
        for column, target_type in column_types.items():
            if column in converted_df.columns:
                converted_df[column] = DataTypeConverter.convert_column(
                    converted_df[column], 
                    target_type, 
                    errors=errors
                )
        
        return converted_df
    
    @staticmethod
    def filter_empty_columns(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
        """
        Remove columns that are mostly NaN or empty.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            threshold (float, optional): Percentage of NaN/empty values to consider for removal. 
                                         Defaults to 0.9 (90% empty).
        
        Returns:
            pd.DataFrame: DataFrame with empty columns removed
        """
        logger.info(f"Filtering columns with more than {threshold*100}% NaN/empty values")
        
        # Calculate percentage of NaN/empty values for each column
        nan_percentages = df.isna().mean()
        
        # Columns to keep (those below the threshold)
        columns_to_keep = nan_percentages[nan_percentages < threshold].index.tolist()
        
        # Log removed columns
        removed_columns = list(set(df.columns) - set(columns_to_keep))
        if removed_columns:
            logger.info(f"Removed empty columns: {removed_columns}")
        
        return df[columns_to_keep]

    @staticmethod
    def suggest_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """
        Suggest data types for all columns in a DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            Dict[str, str]: Mapping of column names to suggested types
        """
        return {col: DataTypeConverter.infer_type(df[col]) for col in df.columns}

    @staticmethod
    def suggest_column_types_with_filtering(df: pd.DataFrame, threshold: float = 0.9) -> Dict[str, str]:
        """
        Suggest column types after filtering out empty columns.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            threshold (float, optional): Percentage of NaN/empty values to consider for removal. 
                                         Defaults to 0.9 (90% empty).
        
        Returns:
            Dict[str, str]: Mapping of column names to suggested types
        """
        filtered_df = DataTypeConverter.filter_empty_columns(df, threshold)
        return {col: DataTypeConverter.infer_type(filtered_df[col]) for col in filtered_df.columns}

# Example usage
if __name__ == "__main__":
    print("✅ DataTypeConverter backend utility loaded successfully")
    print("🔄 This module provides data type conversion and filtering functionality")
    print("🎯 Use from frontend: from backend.utils.data_type_converter import DataTypeConverter")