#!/usr/bin/env python3
"""
Owner Dashboard Utils

Comprehensive utilities for sorting, filtering, and exporting owner data
with optimized performance for large datasets.
"""

from typing import List, Dict, Any, Callable, Optional, Tuple
import pandas as pd
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import json
import csv
from datetime import datetime

from backend.utils.efficient_table_manager import SortOrder
from backend.utils.phone_data_utils import PhoneDataUtils


class OwnerDataSorter:
    """Handles efficient sorting of owner data."""
    
    def __init__(self):
        self.sort_cache = {}
        self.last_sort_key = None
        self.last_sort_order = None
    
    def sort_owners(self, owners: List[Any], column: int, order: SortOrder, 
                   column_configs: List[Dict[str, Any]]) -> List[Any]:
        """
        Sort owners efficiently with caching.
        
        Args:
            owners: List of owner objects
            column: Column index to sort by
            order: Sort order (ASCENDING/DESCENDING)
            column_configs: Column configuration
            
        Returns:
            Sorted list of owners
        """
        if not owners:
            return owners
        
        # Check if we can use cached sort
        cache_key = (column, order, len(owners))
        if cache_key in self.sort_cache:
            logger.debug(f"Using cached sort for column {column}")
            return self.sort_cache[cache_key]
        
        # Get sort configuration
        if column >= len(column_configs):
            logger.warning(f"Column {column} out of range")
            return owners
        
        config = column_configs[column]
        sort_key = config.get('sort_key', config['key'])
        
        # Create sort key function
        if callable(sort_key):
            key_func = sort_key
        else:
            key_func = lambda x: getattr(x, sort_key, '')
        
        # Sort with error handling
        try:
            sorted_owners = sorted(owners, key=key_func, 
                                 reverse=(order == SortOrder.DESCENDING))
            
            # Cache the result (limit cache size)
            if len(self.sort_cache) > 10:
                self.sort_cache.clear()
            self.sort_cache[cache_key] = sorted_owners
            
            logger.debug(f"Sorted {len(owners)} owners by column {column} ({order.name})")
            return sorted_owners
            
        except Exception as e:
            logger.error(f"Sorting failed for column {column}: {e}")
            return owners
    
    def clear_cache(self):
        """Clear sort cache to free memory."""
        self.sort_cache.clear()
        logger.debug("Sort cache cleared")


class OwnerDataFilter:
    """Handles efficient filtering of owner data."""
    
    def __init__(self):
        self.filter_cache = {}
        self.active_filters = {}
    
    def apply_filters(self, owners: List[Any], filters: Dict[str, Any]) -> List[Any]:
        """
        Apply multiple filters efficiently.
        
        Args:
            owners: List of owner objects
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of owners
        """
        if not filters:
            return owners
        
        # Check cache
        filter_key = json.dumps(filters, sort_keys=True)
        if filter_key in self.filter_cache:
            logger.debug("Using cached filter result")
            return self.filter_cache[filter_key]
        
        filtered_owners = owners.copy()
        
        # Apply each filter
        for filter_type, filter_value in filters.items():
            if filter_value:  # Skip empty filters
                filtered_owners = self._apply_single_filter(filtered_owners, filter_type, filter_value)
        
        # Cache result
        if len(self.filter_cache) > 5:  # Limit cache size
            self.filter_cache.clear()
        self.filter_cache[filter_key] = filtered_owners
        
        logger.info(f"Applied {len(filters)} filters: {len(owners)} -> {len(filtered_owners)} owners")
        return filtered_owners
    
    def _apply_single_filter(self, owners: List[Any], filter_type: str, filter_value: Any) -> List[Any]:
        """Apply a single filter."""
        if filter_type == 'owner_type':
            return [o for o in owners if self._matches_owner_type(o, filter_value)]
        elif filter_type == 'search_term':
            return [o for o in owners if self._matches_search(o, filter_value)]
        elif filter_type == 'confidence_min':
            return [o for o in owners if getattr(o, 'confidence_score', 0) >= filter_value]
        elif filter_type == 'property_count_min':
            return [o for o in owners if getattr(o, 'property_count', 0) >= filter_value]
        elif filter_type == 'value_min':
            return [o for o in owners if getattr(o, 'total_property_value', 0) >= filter_value]
        
        return owners
    
    def _matches_owner_type(self, owner: Any, owner_type: str) -> bool:
        """Check if owner matches type filter."""
        if owner_type == "All Owners":
            return True
        elif owner_type == "Business Entities":
            return getattr(owner, 'is_business_owner', False)
        elif owner_type == "Individual Owners":
            return not getattr(owner, 'is_business_owner', False)
        elif owner_type == "Multi-Property":
            return getattr(owner, 'property_count', 0) > 1
        elif owner_type == "High Confidence":
            return getattr(owner, 'confidence_score', 0) >= 0.8
        return True
    
    def _matches_search(self, owner: Any, search_term: str) -> bool:
        """Check if owner matches search term."""
        if not search_term:
            return True
        
        search_lower = search_term.lower()
        
        # Search in owner name
        owner_name = getattr(owner, 'owner_name', '') or getattr(owner, 'name', '')
        if search_lower in str(owner_name).lower():
            return True
        
        # Search in mailing address
        mailing_address = getattr(owner, 'mailing_address', '')
        if search_lower in str(mailing_address).lower():
            return True
        
        # Search in property addresses
        if hasattr(owner, 'property_addresses') and owner.property_addresses:
            for addr in owner.property_addresses:
                if search_lower in str(addr).lower():
                    return True
        
        return False
    
    def clear_cache(self):
        """Clear filter cache."""
        self.filter_cache.clear()
        logger.debug("Filter cache cleared")


class OwnerDataExporter:
    """Handles exporting owner data to various formats."""
    
    def __init__(self):
        self.export_formats = ['csv', 'xlsx', 'json']
        self.export_history = []
    
    def export_data(self, owners: List[Any], format_type: str, 
                   column_configs: List[Dict[str, Any]], parent_widget=None) -> bool:
        """
        Export owner data to specified format.
        
        Args:
            owners: List of owner objects to export
            format_type: Export format (csv, xlsx, json)
            column_configs: Column configuration for formatting
            parent_widget: Parent widget for file dialog
            
        Returns:
            True if export successful, False otherwise
        """
        if not owners:
            QMessageBox.warning(parent_widget, "Export", "No data to export!")
            return False
        
        # Get file path
        file_path = self._get_export_path(format_type, parent_widget)
        if not file_path:
            return False
        
        try:
            # Convert to DataFrame
            df = self._owners_to_dataframe(owners, column_configs)
            
            # Export based on format
            if format_type == 'csv':
                df.to_csv(file_path, index=False)
            elif format_type == 'xlsx':
                df.to_excel(file_path, index=False, engine='openpyxl')
            elif format_type == 'json':
                df.to_json(file_path, orient='records', indent=2)
            
            # Log export
            self._log_export(file_path, len(owners), format_type)
            
            QMessageBox.information(parent_widget, "Export Success", 
                                  f"Exported {len(owners):,} owners to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(parent_widget, "Export Error", f"Export failed: {str(e)}")
            return False
    
    def _owners_to_dataframe(self, owners: List[Any], column_configs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert owner objects to pandas DataFrame."""
        data = []
        
        for owner in owners:
            row = {}
            for config in column_configs:
                key = config['key']
                name = config['name']
                
                # Get value
                if callable(key):
                    value = key(owner)
                else:
                    value = getattr(owner, key, '')
                
                # Apply formatter
                formatter = config.get('formatter')
                if formatter:
                    value = formatter(value, owner)
                
                row[name] = value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _get_export_path(self, format_type: str, parent_widget) -> Optional[str]:
        """Get export file path from user."""
        if format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Export to CSV", 
                f"owner_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
        elif format_type == 'xlsx':
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Export to Excel", 
                f"owner_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
        elif format_type == 'json':
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Export to JSON", 
                f"owner_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
        else:
            return None
        
        return file_path if file_path else None
    
    def _log_export(self, file_path: str, record_count: int, format_type: str):
        """Log export operation."""
        export_info = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'record_count': record_count,
            'format': format_type
        }
        
        self.export_history.append(export_info)
        
        # Keep only last 10 exports
        if len(self.export_history) > 10:
            self.export_history.pop(0)
        
        logger.info(f"Exported {record_count:,} records to {file_path} ({format_type})")
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get export history."""
        return self.export_history.copy()


class OwnerDataAnalyzer:
    """Analyzes owner data for insights and statistics."""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_owners(self, owners: List[Any]) -> Dict[str, Any]:
        """
        Analyze owner data for insights.
        
        Args:
            owners: List of owner objects
            
        Returns:
            Dictionary with analysis results
        """
        if not owners:
            return {}
        
        # Check cache
        cache_key = len(owners)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        analysis = {
            'total_owners': len(owners),
            'total_properties': sum(getattr(o, 'property_count', 0) for o in owners),
            'total_value': sum(getattr(o, 'total_property_value', 0) for o in owners),
            'owner_types': self._analyze_owner_types(owners),
            'confidence_distribution': self._analyze_confidence(owners),
            'property_distribution': self._analyze_property_distribution(owners),
            'value_distribution': self._analyze_value_distribution(owners),
            'phone_quality': self._analyze_phone_quality(owners)
        }
        
        # Cache result
        if len(self.analysis_cache) > 5:
            self.analysis_cache.clear()
        self.analysis_cache[cache_key] = analysis
        
        return analysis
    
    def _analyze_owner_types(self, owners: List[Any]) -> Dict[str, int]:
        """Analyze distribution of owner types."""
        types = {}
        for owner in owners:
            owner_type = getattr(owner, 'owner_type', 'Unknown')
            types[owner_type] = types.get(owner_type, 0) + 1
        return types
    
    def _analyze_confidence(self, owners: List[Any]) -> Dict[str, int]:
        """Analyze confidence score distribution."""
        confidence_ranges = {
            'High (0.8+)': 0,
            'Medium (0.5-0.8)': 0,
            'Low (<0.5)': 0
        }
        
        for owner in owners:
            score = getattr(owner, 'confidence_score', 0)
            if score >= 0.8:
                confidence_ranges['High (0.8+)'] += 1
            elif score >= 0.5:
                confidence_ranges['Medium (0.5-0.8)'] += 1
            else:
                confidence_ranges['Low (<0.5)'] += 1
        
        return confidence_ranges
    
    def _analyze_property_distribution(self, owners: List[Any]) -> Dict[str, int]:
        """Analyze property count distribution."""
        property_ranges = {
            '1 Property': 0,
            '2-5 Properties': 0,
            '6-10 Properties': 0,
            '10+ Properties': 0
        }
        
        for owner in owners:
            count = getattr(owner, 'property_count', 0)
            if count == 1:
                property_ranges['1 Property'] += 1
            elif count <= 5:
                property_ranges['2-5 Properties'] += 1
            elif count <= 10:
                property_ranges['6-10 Properties'] += 1
            else:
                property_ranges['10+ Properties'] += 1
        
        return property_ranges
    
    def _analyze_value_distribution(self, owners: List[Any]) -> Dict[str, int]:
        """Analyze property value distribution."""
        value_ranges = {
            '$0-$50K': 0,
            '$50K-$100K': 0,
            '$100K-$250K': 0,
            '$250K-$500K': 0,
            '$500K+': 0
        }
        
        for owner in owners:
            value = getattr(owner, 'total_property_value', 0)
            if value <= 50000:
                value_ranges['$0-$50K'] += 1
            elif value <= 100000:
                value_ranges['$50K-$100K'] += 1
            elif value <= 250000:
                value_ranges['$100K-$250K'] += 1
            elif value <= 500000:
                value_ranges['$250K-$500K'] += 1
            else:
                value_ranges['$500K+'] += 1
        
        return value_ranges
    
    def _analyze_phone_quality(self, owners: List[Any]) -> Dict[str, int]:
        """Analyze phone quality distribution."""
        phone_quality = {
            'High Quality': 0,
            'Medium Quality': 0,
            'Low Quality': 0,
            'No Phones': 0
        }
        
        for owner in owners:
            # This would need to be implemented based on your phone quality logic
            phone_quality['Medium Quality'] += 1  # Placeholder
        
        return phone_quality
    
    def clear_cache(self):
        """Clear analysis cache."""
        self.analysis_cache.clear()
        logger.debug("Analysis cache cleared")


# Convenience functions
def get_owner_dashboard_utils():
    """Get all owner dashboard utilities."""
    return {
        'sorter': OwnerDataSorter(),
        'filter': OwnerDataFilter(),
        'exporter': OwnerDataExporter(),
        'analyzer': OwnerDataAnalyzer()
    }
