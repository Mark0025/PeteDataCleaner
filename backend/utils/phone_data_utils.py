#!/usr/bin/env python3
"""
Phone Data Utilities

Utilities for handling Pete phone data structure with DRY principles.
"""

from typing import Dict, Any, Optional
from loguru import logger


class PhoneDataUtils:
    """Utilities for handling Pete phone data structure."""
    
    @staticmethod
    def format_phone_count(phone1: str, phone_status: str) -> str:
        """Format phone count using Pete structure."""
        if not phone1 or phone1 == "" or phone1 == "nan":
            return "0/0"
        
        # Count correct phones
        correct = 1 if phone_status == "CORRECT" else 0
        return f"{correct}/1"
    
    @staticmethod
    def format_phone_quality(phone_status: str, phone_type: str) -> str:
        """Format phone quality using Pete structure."""
        if not phone_status or phone_status == "nan":
            return "N/A"
        
        # Simple quality scoring based on status
        if phone_status == "CORRECT":
            return "8.0/10"
        elif phone_status == "WRONG":
            return "3.0/10"
        elif phone_status == "DEAD":
            return "1.0/10"
        else:
            return "5.0/10"
    
    @staticmethod
    def get_best_contact_method(phone1: str, phone_type: str) -> str:
        """Get best contact method using Pete structure."""
        if not phone1 or phone1 == "" or phone1 == "nan":
            return "Unknown"
        
        if phone_type == "MOBILE":
            return f"Mobile ({phone1})"
        elif phone_type == "LANDLINE":
            return f"Landline ({phone1})"
        else:
            return f"Phone ({phone1})"
    
    @staticmethod
    def validate_phone_data(phone1: str, phone_type: str, phone_status: str, phone_tags: str) -> Dict[str, Any]:
        """Validate phone data and return validation results."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate phone1
        if not phone1 or phone1 == "" or phone1 == "nan":
            validation['errors'].append("Phone number is empty")
            validation['is_valid'] = False
        
        # Validate phone_type
        valid_types = ["MOBILE", "LANDLINE", "UNKNOWN", ""]
        if phone_type and phone_type not in valid_types:
            validation['warnings'].append(f"Unknown phone type: {phone_type}")
        
        # Validate phone_status
        valid_statuses = ["CORRECT", "WRONG", "DEAD", ""]
        if phone_status and phone_status not in valid_statuses:
            validation['warnings'].append(f"Unknown phone status: {phone_status}")
        
        return validation
    
    @staticmethod
    def extract_phone_from_row(row: Dict[str, Any]) -> Dict[str, str]:
        """Extract phone data from a dataframe row using Pete structure."""
        # Map common phone column variations
        phone_columns = {
            'phone1': ['Phone1', 'Phone 1', 'phone1', 'PHONE1', 'phone_1'],
            'phone_type': ['Phone_Type', 'Phone Type', 'phone_type', 'PHONE_TYPE'],
            'phone_status': ['Phone_Status', 'Phone Status', 'phone_status', 'PHONE_STATUS'],
            'phone_tags': ['Phone_Tags', 'Phone Tags', 'phone_tags', 'PHONE_TAGS']
        }
        
        phone_data = {}
        
        for field, possible_columns in phone_columns.items():
            value = ""
            for col in possible_columns:
                if col in row:
                    value = str(row[col]) if row[col] is not None else ""
                    break
            phone_data[field] = value
        
        return phone_data
    
    @staticmethod
    def format_phone_for_display(phone_data: Dict[str, str]) -> Dict[str, str]:
        """Format phone data for display in tables."""
        phone1 = phone_data.get('phone1', '')
        phone_type = phone_data.get('phone_type', '')
        phone_status = phone_data.get('phone_status', '')
        phone_tags = phone_data.get('phone_tags', '')
        
        return {
            'phone_count': PhoneDataUtils.format_phone_count(phone1, phone_status),
            'phone_quality': PhoneDataUtils.format_phone_quality(phone_status, phone_type),
            'best_contact': PhoneDataUtils.get_best_contact_method(phone1, phone_type),
            'phone_number': phone1,
            'phone_type': phone_type,
            'phone_status': phone_status,
            'phone_tags': phone_tags
        }


class PhoneDataFormatter:
    """Formats phone data for display using Pete structure."""
    
    def __init__(self):
        self.utils = PhoneDataUtils()
    
    def format_owner_phone_data(self, owner_obj: Any) -> Dict[str, str]:
        """Format all phone data for an owner."""
        # Check if owner has phone fields (OwnerObject vs EnhancedOwnerObject)
        if hasattr(owner_obj, 'phone1'):
            # OwnerObject with Pete phone fields
            phone_data = {
                'phone1': getattr(owner_obj, 'phone1', ''),
                'phone_type': getattr(owner_obj, 'phone_type', ''),
                'phone_status': getattr(owner_obj, 'phone_status', ''),
                'phone_tags': getattr(owner_obj, 'phone_tags', '')
            }
        elif hasattr(owner_obj, 'all_phones') and owner_obj.all_phones:
            # EnhancedOwnerObject with PhoneData objects
            # Use the first phone as primary
            primary_phone = owner_obj.all_phones[0]
            phone_data = {
                'phone1': primary_phone.number,
                'phone_type': primary_phone.phone_type,
                'phone_status': primary_phone.status,
                'phone_tags': primary_phone.tags
            }
        else:
            # No phone data available
            phone_data = {
                'phone1': '',
                'phone_type': '',
                'phone_status': '',
                'phone_tags': ''
            }
        
        return self.utils.format_phone_for_display(phone_data)
    
    def format_phone_table_data(self, phone_data: Dict[str, str]) -> Dict[str, str]:
        """Format phone data for table display."""
        return self.utils.format_phone_for_display(phone_data)


class PhoneDataValidator:
    """Validates phone data using Pete structure."""
    
    def __init__(self):
        self.utils = PhoneDataUtils()
    
    def validate_owner_phone_data(self, owner_obj: Any) -> Dict[str, Any]:
        """Validate phone data for an owner."""
        if hasattr(owner_obj, 'phone1'):
            # OwnerObject with Pete phone fields
            return self.utils.validate_phone_data(
                getattr(owner_obj, 'phone1', ''),
                getattr(owner_obj, 'phone_type', ''),
                getattr(owner_obj, 'phone_status', ''),
                getattr(owner_obj, 'phone_tags', '')
            )
        elif hasattr(owner_obj, 'all_phones') and owner_obj.all_phones:
            # EnhancedOwnerObject with PhoneData objects
            primary_phone = owner_obj.all_phones[0]
            return self.utils.validate_phone_data(
                primary_phone.number,
                primary_phone.phone_type,
                primary_phone.status,
                primary_phone.tags
            )
        else:
            # No phone data
            return {
                'is_valid': False,
                'errors': ['No phone data available'],
                'warnings': []
            } 