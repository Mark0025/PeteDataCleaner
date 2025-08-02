"""
Data Standardizer - Backend Utility

This module contains the core data standardization logic for mapping
upload data to Pete template format with support for:
- Fuzzy column matching
- Explicit mapping rules  
- Field concatenation (e.g., FirstName + LastName → Seller)
- Export to standardized Excel format

This is the authoritative backend implementation.
Frontend components should import and use this module.
"""

import os
import json
import pandas as pd
from backend.utils import trailing_dot_cleanup as tdc
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rapidfuzz import process
from backend.sheets_client import SheetsClient
from datetime import datetime
import re
from loguru import logger
import numpy as np

console = Console()

MAPPINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'DEV_MAN', 'mappings'))
RULES_PATH = os.path.join(MAPPINGS_DIR, 'mapping_rules.json')
os.makedirs(MAPPINGS_DIR, exist_ok=True)

class DataStandardizer:
    """
    Core data standardization utility for mapping upload data to Pete format.
    
    Features:
    - Load Pete template headers from Google Sheets
    - Smart column mapping with fuzzy matching
    - Field concatenation (FirstName + LastName → Seller)
    - Configurable mapping rules
    - Export to Excel format
    """
    
    def __init__(self, pete_headers: Optional[List[str]] = None, rules: Optional[Dict[str, Any]] = None):
        self.pete_headers = pete_headers or []
        self.rules = rules or self.load_rules()
        
        # Default configuration for empty column filtering
        self.empty_column_config = {
            'filter_empty_columns': True,  # Enable filtering by default
            'empty_column_threshold': 0.9  # 90% NaN/empty threshold
        }
        
        # Update with any user-provided configuration
        if 'empty_column_config' in self.rules:
            self.empty_column_config.update(self.rules['empty_column_config'])

    @staticmethod
    def load_pete_headers_from_sheet(sheet_id: str, tab_name: str) -> List[str]:
        """Load Pete template headers from Google Sheet"""
        client = SheetsClient()
        client.set_sheet_id(sheet_id)
        headers = client.get_headers(tab_name)
        return headers

    def load_upload_file(self, filepath: str) -> pd.DataFrame:
        """Load upload file with optional empty column filtering"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.csv':
            df = pd.read_csv(filepath, low_memory=False)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Apply empty column filtering if enabled
        if self.empty_column_config.get('filter_empty_columns', True):
            threshold = self.empty_column_config.get('empty_column_threshold', 0.9)
            df = df.loc[:, df.isnull().mean() < threshold]
            logger.info(f"Filtered columns with more than {threshold*100}% NaN/empty values")

        # Auto strip trailing .0 from numeric-like strings
        df = tdc.clean_dataframe(df)
        return df

    @staticmethod
    def load_rules() -> dict:
        """Load mapping rules from JSON file"""
        if os.path.exists(RULES_PATH):
            with open(RULES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def propose_mapping(self, upload_columns: List[str]) -> Dict[str, Tuple[Optional[str], float, str]]:
        """
        Propose mapping between upload columns and Pete headers
        
        Returns: Dict[upload_col] = (pete_header, confidence_score, rule_reason)
        """
        pete_headers_norm = [h.strip().lower() for h in self.pete_headers]
        never_map = set(s.strip().lower() for s in self.rules.get('never_map', []))
        explicit_map = {k.strip().lower(): v for k, v in self.rules.get('explicit_map', {}).items()}
        concat_fields = self.rules.get('concat_fields', {})
        
        fuzzy_threshold = self.rules.get('fuzzy_threshold', 80)
        disable_fuzzy = self.rules.get('disable_fuzzy', False)
        used_pete = set()
        result = {}

        # 1. Never map rules
        for col in upload_columns:
            col_norm = col.strip().lower()
            for nm in never_map:
                if nm in col_norm:
                    result[col] = (None, 0.0, f'Config: Never map ({nm})')
                    break

        # 2. Explicit mapping rules
        for col in upload_columns:
            col_norm = col.strip().lower()
            if col in result:
                continue
            if col_norm in explicit_map:
                pete = explicit_map[col_norm]
                if pete in self.pete_headers and pete not in used_pete:
                    result[col] = (pete, 100.0, f'Config: Explicit map ({col}->{pete})')
                    used_pete.add(pete)
                else:
                    result[col] = (None, 0.0, f'Config: Explicit map target not available')

        # 3. Concatenation fields
        for pete, concat_cols in concat_fields.items():
            if pete in self.pete_headers and pete not in used_pete:
                available_cols = [col for col in upload_columns 
                                if col.strip().lower() in [c.strip().lower() for c in concat_cols]]
                if len(available_cols) == len(concat_cols):
                    for col in available_cols:
                        result[col] = (f'(used in {pete})', 100.0, f'Config: Concat for {pete}')
                    used_pete.add(pete)

        # 4. Exact match (case-insensitive)
        for col in upload_columns:
            col_norm = col.strip().lower()
            if col in result:
                continue
            if col_norm in pete_headers_norm:
                idx = pete_headers_norm.index(col_norm)
                pete = self.pete_headers[idx]
                if pete not in used_pete:
                    result[col] = (pete, 100.0, "Exact match (case-insensitive)")
                    used_pete.add(pete)

        # 5. Fuzzy match (if enabled)
        for col in upload_columns:
            col_norm = col.strip().lower()
            if col in result or disable_fuzzy:
                continue

            available_pete = [h for h in self.pete_headers if h not in used_pete]
            available_pete_norm = [h.strip().lower() for h in available_pete]
            
            if not available_pete:
                result[col] = (None, 0.0, "No match (all Pete headers mapped)")
                continue

            match, score, _ = process.extractOne(col_norm, available_pete_norm)
            
            if score >= fuzzy_threshold:
                idx = available_pete_norm.index(match)
                pete = available_pete[idx]
                result[col] = (pete, score, f"Fuzzy ({score:.0f})")
                used_pete.add(pete)
            else:
                result[col] = (None, 0.0, f"No match (below threshold {fuzzy_threshold})")

        return result

    def transform_data(self, df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
        """Transform data according to mapping rules"""
        concat_fields = self.rules.get('concat_fields', {})
        concat_separator = self.rules.get('concat_separator', ' ')
        
        output_data = {}
        
        # Process each Pete header
        for pete_header in self.pete_headers:
            # Check if this header is a concatenation target
            if pete_header in concat_fields:
                source_columns = concat_fields[pete_header]
                matched_cols = [col for col in df.columns 
                              if col in source_columns or 
                                 col.lower() in [sc.lower() for sc in source_columns]]
                
                if len(matched_cols) == len(source_columns):
                    # Concatenate the columns
                    output_data[pete_header] = df[matched_cols].apply(
                        lambda row: concat_separator.join(str(val) for val in row if pd.notna(val)), 
                        axis=1
                    )
                else:
                    output_data[pete_header] = pd.Series([np.nan] * len(df))
            else:
                # Regular mapping
                mapped_col = next((col for col, pete_col in mapping.items() if pete_col == pete_header), None)
                if mapped_col and mapped_col in df.columns:
                    output_data[pete_header] = df[mapped_col]
                else:
                    output_data[pete_header] = pd.Series([np.nan] * len(df))
        
        return pd.DataFrame(output_data)

    def generate_report(self, mapping: Dict[str, Optional[str]], output_excel: str, unmapped_excel: str) -> str:
        """Generate mapping report in markdown format"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mapped = {k: v for k, v in mapping.items() if v}
        unmapped = [k for k, v in mapping.items() if v is None]
        
        mapped_pete = set(v for v in mapping.values() if v)
        not_available = [h for h in self.pete_headers if h not in mapped_pete]
        
        report = f"""# Pete Upload Standardization Report

**Date:** {now}

## Mapping Summary

| Upload Column | Pete Header |
|---------------|-------------|
"""
        for k, v in mapping.items():
            report += f"| {k} | {v if v else 'NOT MAPPED'} |\n"
            
        if not_available:
            report += f"\n## Pete Headers Not Available in Upload\n\n"
            for h in not_available:
                report += f"- {h}\n"
                
        report += f"\n## Output Files\n\n- [Standardized Excel]({output_excel})\n- [Unmapped Excel]({unmapped_excel})\n\n"
        
        if unmapped:
            report += f"## Unmapped Columns\n\n"
            for col in unmapped:
                report += f"- {col}\n"
        else:
            report += "All columns mapped!\n"
            
        return report

# Example usage
if __name__ == "__main__":
    print("✅ DataStandardizer backend utility loaded successfully")
    print("📊 This module provides core data mapping and standardization functionality")
    print("🎯 Use from frontend: from backend.utils.data_standardizer import DataStandardizer")