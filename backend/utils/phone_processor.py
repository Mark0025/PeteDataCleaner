"""
Phone Processor - Backend Utility

Advanced phone number processing utility for cleaning, validation, and priority-based allocation.
Handles conversion from float64 to clean phone format and prioritizes based on status indicators.

Features:
- Clean float64 phone numbers (remove .0 suffixes)
- Parse phone status indicators ("correct number", "verified", etc.)
- Prioritize phone allocation based on status confidence
- Reorder Phone 1, Phone 2, Phone 3 columns by priority
- Integration with existing data processing pipeline

This is the authoritative backend implementation.
Frontend components should import and use this module.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class PhoneStatus(Enum):
    """Phone number status classification - Based on real data values"""
    CORRECT = "CORRECT"        # Confirmed good number - HIGHEST PRIORITY
    UNKNOWN = "UNKNOWN"        # Unverified but could be good
    NO_ANSWER = "NO_ANSWER"    # Number works but no answer
    DEAD = "DEAD"              # Disconnected number - LOW PRIORITY
    WRONG = "WRONG"            # Wrong number - LOW PRIORITY
    DNC = "DNC"                # Do Not Call - EXCLUDE

class PhoneType(Enum):
    """Phone type classification - Based on real data values"""
    MOBILE = "MOBILE"      # Mobile phones - HIGHER PRIORITY
    LANDLINE = "LANDLINE"  # Landline phones - LOWER PRIORITY
    UNKNOWN = "UNKNOWN"    # Unknown type

@dataclass
class PhoneEntry:
    """Data class for phone number with metadata"""
    number: str
    original_value: Any
    status: PhoneStatus
    phone_type: PhoneType
    confidence: float
    source_column: str
    priority_score: float

class PhoneProcessor:
    """
    Utility for cleaning and prioritizing phone numbers based on status indicators.
    
    Features:
    - Clean float64 phone numbers (remove .0)
    - Parse phone status indicators
    - Prioritize "correct number" entries
    - Reorder phone columns by priority
    """
    
    # Exact status values from real data
    STATUS_VALUES = {
        PhoneStatus.CORRECT: "CORRECT",      # Confirmed good number
        PhoneStatus.UNKNOWN: "UNKNOWN",      # Unverified
        PhoneStatus.NO_ANSWER: "NO_ANSWER",  # Works but no answer
        PhoneStatus.DEAD: "DEAD",            # Disconnected
        PhoneStatus.WRONG: "WRONG",          # Wrong number
        PhoneStatus.DNC: "DNC"               # Do Not Call
    }
    
    # Priority scoring weights (CORRECT = highest, DEAD/WRONG = lowest)
    PRIORITY_WEIGHTS = {
        PhoneStatus.CORRECT: 10.0,    # Highest priority - confirmed good
        PhoneStatus.UNKNOWN: 5.0,     # Medium priority - might be good
        PhoneStatus.NO_ANSWER: 3.0,   # Lower priority - works but no answer
        PhoneStatus.DEAD: 1.0,        # Very low priority - disconnected
        PhoneStatus.WRONG: 1.0,       # Very low priority - wrong number
        PhoneStatus.DNC: 0.1          # Lowest priority - do not call
    }
    
    # Phone type priority weights (MOBILE = higher priority)
    TYPE_WEIGHTS = {
        PhoneType.MOBILE: 2.0,     # Mobile phones preferred
        PhoneType.LANDLINE: 1.0,   # Landline phones lower
        PhoneType.UNKNOWN: 1.5     # Unknown type medium
    }
    
    def __init__(self, phone_columns: Optional[List[str]] = None, status_columns: Optional[List[str]] = None):
        """
        Initialize PhoneProcessor with column configuration.
        
        Args:
            phone_columns: List of phone number column names (auto-detect if None)
            status_columns: List of status column names (auto-detect if None)
        """
        self.phone_columns = phone_columns or []
        self.status_columns = status_columns or []
        logger.info("PhoneProcessor initialized")
    
    def clean_phone_number(self, phone_value: Any) -> str:
        """
        Clean a single phone number value.
        
        Args:
            phone_value: Raw phone number (could be float, string, etc.)
            
        Returns:
            str: Cleaned phone number string
        """
        if pd.isna(phone_value):
            return ""
        
        # Convert to string and handle float .0 issue
        phone_str = str(phone_value)
        
        # Remove .0 suffix if present (handles float64 conversion)
        if phone_str.endswith('.0'):
            phone_str = phone_str[:-2]
        
        # Remove all non-digit characters for cleaning
        digits_only = re.sub(r'[^\d]', '', phone_str)
        
        # Validate length (US phone numbers are typically 10 digits)
        if len(digits_only) == 10:
            # Format as standard US phone number
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # Handle +1 country code
            return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        elif len(digits_only) >= 7:
            # Return as-is for other valid lengths
            return digits_only
        else:
            # Return original string if too short
            return phone_str
    
    def detect_phone_status(self, row_data: pd.Series, phone_column: str) -> PhoneStatus:
        """
        Detect phone status from row data by examining related status columns.
        
        Args:
            row_data: Pandas Series containing row data
            phone_column: Name of the phone column being analyzed (e.g., "Phone 1")
            
        Returns:
            PhoneStatus: Detected status for the phone number
        """
        # Extract phone number (e.g., "1" from "Phone 1")
        phone_num = phone_column.replace("Phone", "").strip()
        status_column = f"Phone Status {phone_num}"
        
        # Look for exact status column
        if status_column in row_data.index:
            status_value = str(row_data[status_column]).upper() if pd.notna(row_data[status_column]) else ""
            
            # Match exact status values from real data
            for status, expected_value in self.STATUS_VALUES.items():
                if status_value == expected_value:
                    logger.debug(f"Detected status {status.value} for {phone_column} from {status_column}: {status_value}")
                    return status
        
        # Default to UNKNOWN if no explicit status found
        return PhoneStatus.UNKNOWN
    
    def detect_phone_type(self, row_data: pd.Series, phone_column: str) -> PhoneType:
        """
        Detect phone type from row data by examining related type columns.
        
        Args:
            row_data: Pandas Series containing row data
            phone_column: Name of the phone column being analyzed (e.g., "Phone 1")
            
        Returns:
            PhoneType: Detected type for the phone number
        """
        # Extract phone number (e.g., "1" from "Phone 1")
        phone_num = phone_column.replace("Phone", "").strip()
        type_column = f"Phone Type {phone_num}"
        
        # Look for exact type column
        if type_column in row_data.index:
            type_value = str(row_data[type_column]).upper() if pd.notna(row_data[type_column]) else ""
            
            # Match exact type values from real data
            if type_value == "MOBILE":
                return PhoneType.MOBILE
            elif type_value == "LANDLINE":
                return PhoneType.LANDLINE
            
        # Default to UNKNOWN if no explicit type found
        return PhoneType.UNKNOWN
    
    def calculate_priority_score(self, phone_entry: PhoneEntry) -> float:
        """
        Calculate priority score for a phone entry based on status and type.
        
        Args:
            phone_entry: PhoneEntry object
            
        Returns:
            float: Priority score (higher = better priority)
        """
        # Exclude empty or invalid numbers
        if not phone_entry.number or phone_entry.number.strip() == "":
            return 0.0
        
        # Get base scores from status and type
        status_score = self.PRIORITY_WEIGHTS.get(phone_entry.status, 5.0)
        type_score = self.TYPE_WEIGHTS.get(phone_entry.phone_type, 1.0)
        
        # Calculate combined score (status is more important than type)
        priority_score = status_score * type_score
        
        # Boost score for valid phone format (10+ digits)
        if len(re.sub(r'[^\d]', '', phone_entry.number)) >= 10:
            priority_score += 1.0
        
        logger.debug(f"Priority calculation: Status={phone_entry.status.value}({status_score}) × Type={phone_entry.phone_type.value}({type_score}) = {priority_score:.2f}")
        
        return priority_score
    
    def detect_phone_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Auto-detect phone number columns in a DataFrame.
        Handles the specific pattern: "Phone 1", "Phone 2", etc.
        
        Args:
            df: Input DataFrame
            
        Returns:
            List[str]: List of detected phone column names (sorted by number)
        """
        detected_columns = []
        
        # Look for numbered phone columns first (Phone 1, Phone 2, etc.)
        for i in range(1, 31):  # Check up to Phone 30
            phone_col = f"Phone {i}"
            if phone_col in df.columns:
                detected_columns.append(phone_col)
        
        # Also look for other phone-related columns
        phone_keywords = ['phone', 'tel', 'telephone', 'mobile', 'cell']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in phone_keywords):
                if col not in detected_columns and 'status' not in col_lower and 'type' not in col_lower and 'tag' not in col_lower:
                    detected_columns.append(col)
        
        logger.info(f"Auto-detected phone columns: {detected_columns[:10]}{'...' if len(detected_columns) > 10 else ''} (Total: {len(detected_columns)})")
        return detected_columns
    
    def analyze_phone_data(self, df: pd.DataFrame, phone_columns: Optional[List[str]] = None) -> List[PhoneEntry]:
        """
        Analyze phone data in DataFrame and create PhoneEntry objects.
        
        Args:
            df: Input DataFrame
            phone_columns: List of phone columns (auto-detect if None)
            
        Returns:
            List[PhoneEntry]: List of phone entries with metadata
        """
        if phone_columns is None:
            phone_columns = self.detect_phone_columns(df)
        
        phone_entries = []
        
        for index, row in df.iterrows():
            for phone_col in phone_columns:
                if phone_col in row.index:
                    # Clean the phone number
                    original_value = row[phone_col]
                    cleaned_number = self.clean_phone_number(original_value)
                    
                    # Detect status and type
                    status = self.detect_phone_status(row, phone_col)
                    phone_type = self.detect_phone_type(row, phone_col)
                    
                    # Create phone entry
                    phone_entry = PhoneEntry(
                        number=cleaned_number,
                        original_value=original_value,
                        status=status,
                        phone_type=phone_type,
                        confidence=0.8,  # Default confidence
                        source_column=phone_col,
                        priority_score=0.0  # Will be calculated
                    )
                    
                    # Calculate priority score
                    phone_entry.priority_score = self.calculate_priority_score(phone_entry)
                    
                    phone_entries.append(phone_entry)
                    
                    logger.debug(f"Row {index}, Column {phone_col}: {original_value} -> {cleaned_number} (Status: {status.value}, Priority: {phone_entry.priority_score:.2f})")
        
        return phone_entries
    
    def reorder_phone_allocation(self, df: pd.DataFrame, phone_columns: Optional[List[str]] = None, max_phones: int = 5) -> pd.DataFrame:
        """
        Reorder phone columns based on priority scores.
        
        Args:
            df: Input DataFrame
            phone_columns: List of phone columns (auto-detect if None)
            max_phones: Maximum number of phones to keep (Pete accepts 5 max)
            
        Returns:
            pd.DataFrame: DataFrame with reordered phone allocation
        """
        if df.empty:
            return df
        
        logger.info("Starting phone allocation reordering")
        
        if phone_columns is None:
            phone_columns = self.detect_phone_columns(df)
        
        if not phone_columns:
            logger.warning("No phone columns detected for reordering")
            return df
        
        # Create a copy of the DataFrame
        result_df = df.copy()
        
        # Process each row
        for index, row in df.iterrows():
            # Collect phone entries for this row
            row_phone_entries = []
            
            for phone_col in phone_columns:
                if phone_col in row.index and pd.notna(row[phone_col]):
                    # Clean the phone number
                    original_value = row[phone_col]
                    cleaned_number = self.clean_phone_number(original_value)
                    
                    # Skip empty numbers
                    if not cleaned_number or cleaned_number.strip() == "":
                        continue
                    
                    # Detect status and type
                    status = self.detect_phone_status(row, phone_col)
                    phone_type = self.detect_phone_type(row, phone_col)
                    
                    # Create phone entry
                    phone_entry = PhoneEntry(
                        number=cleaned_number,
                        original_value=original_value,
                        status=status,
                        phone_type=phone_type,
                        confidence=0.8,
                        source_column=phone_col,
                        priority_score=0.0
                    )
                    
                    # Calculate priority score
                    phone_entry.priority_score = self.calculate_priority_score(phone_entry)
                    row_phone_entries.append(phone_entry)
            
            # Sort by priority score (highest first)
            row_phone_entries.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Clear existing phone columns
            for phone_col in phone_columns:
                if phone_col in result_df.columns:
                    result_df.at[index, phone_col] = ""
            
            # Assign phones to columns based on priority (limit to max_phones for Pete)
            phones_to_assign = min(len(row_phone_entries), max_phones, len(phone_columns))
            for i in range(phones_to_assign):
                phone_entry = row_phone_entries[i]
                target_column = phone_columns[i]
                result_df.at[index, target_column] = phone_entry.number
                logger.debug(f"Row {index}: Assigned {phone_entry.number} to {target_column} (Priority: {phone_entry.priority_score:.2f}, Status: {phone_entry.status.value}, Type: {phone_entry.phone_type.value})")
        
        logger.success(f"Phone allocation reordering completed for {len(df)} rows")
        return result_df
    
    def process_dataframe(self, df: pd.DataFrame, phone_columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process entire DataFrame for phone number cleaning and prioritization.
        
        Args:
            df: Input DataFrame
            phone_columns: List of phone columns (auto-detect if None)
            
        Returns:
            Tuple[pd.DataFrame, Dict]: Processed DataFrame and processing statistics
        """
        logger.info("Starting phone processing for DataFrame")
        
        if df.empty:
            return df, {"processed_rows": 0, "phone_columns": []}
        
        # Auto-detect phone columns if not provided
        if phone_columns is None:
            phone_columns = self.detect_phone_columns(df)
        
        if not phone_columns:
            logger.warning("No phone columns detected")
            return df, {"processed_rows": 0, "phone_columns": []}
        
        # Process the DataFrame
        processed_df = self.reorder_phone_allocation(df, phone_columns)
        
        # Generate statistics
        stats = {
            "processed_rows": len(df),
            "phone_columns": phone_columns,
            "total_phones_processed": len(df) * len(phone_columns),
            "processing_method": "priority_reallocation"
        }
        
        logger.success(f"Phone processing completed. Processed {stats['processed_rows']} rows with {len(phone_columns)} phone columns")
        
        return processed_df, stats


# Convenience functions for easy import and use
def clean_phone_dataframe(df: pd.DataFrame, phone_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Convenience function to process a DataFrame with phone number enhancement.
    
    Args:
        df: Input DataFrame
        phone_columns: List of phone columns (auto-detect if None)
        
    Returns:
        pd.DataFrame: Processed DataFrame with cleaned and prioritized phones
    """
    processor = PhoneProcessor(phone_columns=phone_columns)
    processed_df, _ = processor.process_dataframe(df, phone_columns)
    return processed_df


def clean_single_phone(phone_value: Any) -> str:
    """
    Convenience function to clean a single phone number.
    
    Args:
        phone_value: Raw phone number value
        
    Returns:
        str: Cleaned phone number
    """
    processor = PhoneProcessor()
    return processor.clean_phone_number(phone_value)