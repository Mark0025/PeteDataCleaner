#!/usr/bin/env python3
"""
Enhanced Owner Object Analyzer

Creates sophisticated Owner Objects with comprehensive phone data
for investor analysis and dashboard visualization.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import re
from loguru import logger


@dataclass
class PhoneData:
    """Individual phone number with comprehensive metadata."""
    number: str = ""
    original_column: str = ""  # "Phone 1", "Phone 2", etc.
    status: str = ""           # "CORRECT", "WRONG", "DEAD", etc.
    phone_type: str = ""       # "MOBILE", "LANDLINE", "UNKNOWN"
    tags: str = ""             # "call_a01", "call_a02", etc.
    priority_score: float = 0.0
    is_pete_prioritized: bool = False
    confidence: float = 0.0
    
    def __str__(self):
        return f"PhoneData({self.number}, {self.status}, {self.phone_type}, priority={self.priority_score})"


@dataclass
class PropertyDetail:
    """Detailed property information for portfolio analysis."""
    property_address: str = ""
    mailing_address: str = ""
    owner_name: str = ""
    owner_type: str = ""       # "Individual", "LLC", "Corporation"
    property_value: float = 0.0
    phone_numbers: List[PhoneData] = field(default_factory=list)
    
    def __str__(self):
        return f"PropertyDetail({self.property_address}, {self.owner_name}, ${self.property_value:,.0f})"


@dataclass
class EnhancedOwnerObject:
    """Enhanced Owner Object with comprehensive phone data and analysis."""
    
    # Core identification
    individual_name: str = ""
    business_name: str = ""
    mailing_address: str = ""
    property_address: str = ""
    
    # Owner type flags
    is_individual_owner: bool = False
    is_business_owner: bool = False
    has_skip_trace_info: bool = False
    
    # Property portfolio
    total_property_value: float = 0.0
    property_count: int = 0
    property_addresses: List[str] = field(default_factory=list)
    
    # Enhanced phone data
    all_phones: List[PhoneData] = field(default_factory=list)
    pete_prioritized_phones: List[PhoneData] = field(default_factory=list)
    phone_quality_score: float = 0.0
    best_contact_method: str = ""
    
    # Skip trace information
    skip_trace_target: str = ""
    confidence_score: float = 0.0
    
    # Pete mapping
    seller1_name: str = ""
    
    # Property portfolio details
    property_details: List[PropertyDetail] = field(default_factory=list)
    
    # LLC analysis
    llc_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"EnhancedOwnerObject(individual='{self.individual_name}', business='{self.business_name}', phones={len(self.all_phones)}, quality={self.phone_quality_score:.1f})"
    
    def get_best_phone(self) -> Optional[PhoneData]:
        """Get the best quality phone number."""
        if not self.all_phones:
            return None
        
        # Sort by priority score and return the best
        sorted_phones = sorted(self.all_phones, key=lambda x: x.priority_score, reverse=True)
        return sorted_phones[0]
    
    def get_pete_phones(self) -> List[PhoneData]:
        """Get phones prioritized for Pete CRM."""
        return [phone for phone in self.all_phones if phone.is_pete_prioritized]
    
    def get_correct_phones(self) -> List[PhoneData]:
        """Get phones with CORRECT status."""
        return [phone for phone in self.all_phones if phone.status == "CORRECT"]
    
    def get_phone_quality_summary(self) -> Dict[str, int]:
        """Get summary of phone quality distribution."""
        summary = {}
        for phone in self.all_phones:
            status = phone.status
            summary[status] = summary.get(status, 0) + 1
        return summary


class EnhancedOwnerAnalyzer:
    """Analyzes property data to create enhanced Owner Objects with phone data."""
    
    def __init__(self):
        self.business_indicators = [
            'llc', 'inc', 'corp', 'company', 'holdings', 'properties', 
            'realty', 'management', 'investments', 'group', 'associates',
            'partners', 'enterprises', 'ventures', 'capital', 'fund'
        ]
        
        self.logger = logger
    
    def detect_business_entity(self, name: str) -> bool:
        """Detect if a name represents a business entity."""
        if pd.isna(name) or name == "":
            return False
        
        name_lower = str(name).lower()
        return any(indicator in name_lower for indicator in self.business_indicators)
    
    def create_owner_name(self, first_name: str, last_name: str) -> str:
        """Create a clean individual name from first and last name."""
        if pd.isna(first_name) and pd.isna(last_name):
            return ""
        
        first = str(first_name).strip() if pd.notna(first_name) else ""
        last = str(last_name).strip() if pd.notna(last_name) else ""
        
        if first and last:
            return f"{first} {last}".strip()
        elif first:
            return first
        elif last:
            return last
        else:
            return ""
    
    def extract_phone_data(self, row: pd.Series) -> List[PhoneData]:
        """Extract all phone data from a row with metadata."""
        phone_data = []
        
        # Find all phone columns (up to 30)
        for i in range(1, 31):
            phone_col = f"Phone {i}"
            status_col = f"Phone Status {i}"
            type_col = f"Phone Type {i}"
            tag_col = f"Phone Tag {i}"
            
            if phone_col in row.index and pd.notna(row[phone_col]):
                # Clean phone number
                phone_number = str(row[phone_col]).strip()
                if phone_number and phone_number != "nan":
                    # Get metadata
                    status = str(row.get(status_col, "")).strip() if status_col in row.index else "UNKNOWN"
                    phone_type = str(row.get(type_col, "")).strip() if type_col in row.index else "UNKNOWN"
                    tags = str(row.get(tag_col, "")).strip() if tag_col in row.index else ""
                    
                    # Calculate priority score
                    priority_score = self._calculate_phone_priority(status, phone_type, tags, i)
                    
                    # Determine if this is a Pete prioritized phone (top 4)
                    is_pete_prioritized = i <= 4
                    
                    # Calculate confidence
                    confidence = self._calculate_phone_confidence(status, phone_type)
                    
                    phone_data.append(PhoneData(
                        number=phone_number,
                        original_column=phone_col,
                        status=status,
                        phone_type=phone_type,
                        tags=tags,
                        priority_score=priority_score,
                        is_pete_prioritized=is_pete_prioritized,
                        confidence=confidence
                    ))
        
        return phone_data
    
    def _calculate_phone_priority(self, status: str, phone_type: str, tags: str, position: int) -> float:
        """Calculate priority score for a phone number."""
        score = 0.0
        
        # Status weights
        status_weights = {
            'CORRECT': 100.0,
            'UNKNOWN': 70.0,
            'NO_ANSWER': 50.0,
            'WRONG': 0.0,
            'DEAD': 0.0,
            'DNC': -100.0
        }
        score += status_weights.get(status.upper(), 0.0)
        
        # Type weights
        type_weights = {
            'MOBILE': 10.0,
            'LANDLINE': 0.0,
            'UNKNOWN': 0.0
        }
        score += type_weights.get(phone_type.upper(), 0.0)
        
        # Tag weights (call count penalty)
        if tags and 'call_a' in tags.lower():
            try:
                call_count = int(re.search(r'call_a(\d+)', tags.lower()).group(1))
                score -= call_count * 5  # Penalty for high call counts
            except:
                pass
        
        # Position penalty (earlier phones slightly preferred)
        score -= position
        
        return score
    
    def _calculate_phone_confidence(self, status: str, phone_type: str) -> float:
        """Calculate confidence score for a phone number."""
        confidence = 0.5  # Base confidence
        
        # Status confidence
        status_confidence = {
            'CORRECT': 1.0,
            'UNKNOWN': 0.7,
            'NO_ANSWER': 0.6,
            'WRONG': 0.1,
            'DEAD': 0.0,
            'DNC': 0.0
        }
        confidence *= status_confidence.get(status.upper(), 0.5)
        
        # Type confidence
        type_confidence = {
            'MOBILE': 0.9,
            'LANDLINE': 0.8,
            'UNKNOWN': 0.6
        }
        confidence *= type_confidence.get(phone_type.upper(), 0.6)
        
        return min(confidence, 1.0)
    
    def calculate_phone_quality_score(self, phones: List[PhoneData]) -> float:
        """Calculate overall phone quality score for an owner."""
        if not phones:
            return 0.0
        
        # Weight by priority score and confidence
        total_score = 0.0
        total_weight = 0.0
        
        for phone in phones:
            weight = phone.priority_score + phone.confidence * 10
            total_score += phone.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 0.0
    
    def analyze_property_group(self, group: pd.DataFrame) -> EnhancedOwnerObject:
        """Analyze a group of properties to create an enhanced owner object."""
        if group.empty:
            return EnhancedOwnerObject()
        
        # Get first row for basic info
        first_row = group.iloc[0]
        
        # Extract phone data from all rows in the group
        all_phones = []
        for _, row in group.iterrows():
            phones = self.extract_phone_data(row)
            all_phones.extend(phones)
        
        # Remove duplicates (same number)
        unique_phones = {}
        for phone in all_phones:
            if phone.number not in unique_phones or phone.priority_score > unique_phones[phone.number].priority_score:
                unique_phones[phone.number] = phone
        
        all_phones = list(unique_phones.values())
        
        # Sort by priority score
        all_phones.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Get Pete prioritized phones (top 4)
        pete_phones = all_phones[:4]
        for phone in pete_phones:
            phone.is_pete_prioritized = True
        
        # Create owner name
        first_name = first_row.get('First Name', '')
        last_name = first_row.get('Last Name', '')
        individual_name = self.create_owner_name(first_name, last_name)
        
        # Detect business entity
        business_name = str(first_row.get('Seller 1', ''))
        is_business_owner = self.detect_business_entity(business_name)
        is_individual_owner = bool(individual_name and not is_business_owner)
        
        # Property details
        property_addresses = []
        property_details = []
        total_value = 0.0
        
        for _, row in group.iterrows():
            prop_addr = str(row.get('Property Address', ''))
            mail_addr = str(row.get('Mailing Address', ''))
            value = float(row.get('Property Value', 0))
            
            if prop_addr and prop_addr != "nan":
                property_addresses.append(prop_addr)
                total_value += value
                
                # Create property detail
                prop_phones = self.extract_phone_data(row)
                property_details.append(PropertyDetail(
                    property_address=prop_addr,
                    mailing_address=mail_addr,
                    owner_name=business_name or individual_name,
                    owner_type="Business" if is_business_owner else "Individual",
                    property_value=value,
                    phone_numbers=prop_phones
                ))
        
        # Calculate phone quality score
        phone_quality_score = self.calculate_phone_quality_score(all_phones)
        
        # Determine best contact method
        best_contact_method = self._determine_best_contact_method(all_phones)
        
        # Create skip trace target
        skip_trace_target = individual_name if individual_name else business_name
        
        # LLC analysis
        llc_analysis = self._analyze_llc(business_name, all_phones, property_details)
        
        # Create enhanced owner object
        owner_obj = EnhancedOwnerObject(
            individual_name=individual_name,
            business_name=business_name,
            mailing_address=str(first_row.get('Mailing Address', '')),
            property_address=str(first_row.get('Property Address', '')),
            is_individual_owner=is_individual_owner,
            is_business_owner=is_business_owner,
            has_skip_trace_info=bool(skip_trace_target),
            total_property_value=total_value,
            property_count=len(property_addresses),
            property_addresses=property_addresses,
            all_phones=all_phones,
            pete_prioritized_phones=pete_phones,
            phone_quality_score=phone_quality_score,
            best_contact_method=best_contact_method,
            skip_trace_target=skip_trace_target,
            confidence_score=phone_quality_score,
            seller1_name=business_name or individual_name,
            property_details=property_details,
            llc_analysis=llc_analysis
        )
        
        return owner_obj
    
    def _determine_best_contact_method(self, phones: List[PhoneData]) -> str:
        """Determine the best contact method based on phone quality."""
        if not phones:
            return "No phone available"
        
        # Get best phone
        best_phone = max(phones, key=lambda x: x.priority_score)
        
        if best_phone.status == "CORRECT":
            return f"Call {best_phone.number} (Verified)"
        elif best_phone.status == "UNKNOWN":
            return f"Call {best_phone.number} (Unverified)"
        elif best_phone.status == "NO_ANSWER":
            return f"Call {best_phone.number} (No Answer)"
        else:
            return f"Skip trace needed"
    
    def _analyze_llc(self, business_name: str, phones: List[PhoneData], properties: List[PropertyDetail]) -> Dict[str, Any]:
        """Analyze LLC/business entity information."""
        analysis = {
            'is_llc': False,
            'business_type': 'Individual',
            'phone_count': len(phones),
            'property_count': len(properties),
            'total_value': sum(p.property_value for p in properties),
            'contact_quality': 'Unknown'
        }
        
        if self.detect_business_entity(business_name):
            analysis['is_llc'] = True
            analysis['business_type'] = 'Business Entity'
            
            # Determine business type
            name_lower = business_name.lower()
            if 'llc' in name_lower:
                analysis['business_type'] = 'LLC'
            elif 'inc' in name_lower or 'corp' in name_lower:
                analysis['business_type'] = 'Corporation'
            elif 'trust' in name_lower:
                analysis['business_type'] = 'Trust'
        
        # Contact quality based on phone status
        correct_phones = [p for p in phones if p.status == "CORRECT"]
        if correct_phones:
            analysis['contact_quality'] = 'Good'
        elif any(p.status == "UNKNOWN" for p in phones):
            analysis['contact_quality'] = 'Fair'
        else:
            analysis['contact_quality'] = 'Poor'
        
        return analysis
    
    def analyze_dataset(self, df: pd.DataFrame) -> Tuple[List[EnhancedOwnerObject], pd.DataFrame]:
        """Analyze entire dataset to create enhanced owner objects."""
        self.logger.info(f"🔍 Starting enhanced owner analysis for {len(df):,} records")
        
        # Group by property address to identify owners
        property_groups = df.groupby('Property Address')
        
        enhanced_owner_objects = []
        enhanced_data = []
        
        total_groups = len(property_groups)
        self.logger.info(f"📊 Processing {total_groups:,} property groups")
        
        for i, (property_addr, group) in enumerate(property_groups):
            if i % 1000 == 0:
                self.logger.info(f"📈 Progress: {i:,}/{total_groups:,} groups processed")
            
            # Create enhanced owner object
            owner_obj = self.analyze_property_group(group)
            
            if owner_obj.seller1_name:  # Only add if we have a valid owner
                enhanced_owner_objects.append(owner_obj)
                
                # Add to enhanced dataframe
                for _, row in group.iterrows():
                    enhanced_row = row.copy()
                    enhanced_row['Owner Type'] = 'Business' if owner_obj.is_business_owner else 'Individual'
                    enhanced_row['Phone Quality Score'] = owner_obj.phone_quality_score
                    enhanced_row['Best Contact Method'] = owner_obj.best_contact_method
                    enhanced_row['Skip Trace Target'] = owner_obj.skip_trace_target
                    enhanced_row['Property Count'] = owner_obj.property_count
                    enhanced_row['Total Property Value'] = owner_obj.total_property_value
                    enhanced_data.append(enhanced_row)
        
        enhanced_df = pd.DataFrame(enhanced_data)
        
        self.logger.info(f"✅ Enhanced owner analysis complete: {len(enhanced_owner_objects):,} owners created")
        self.logger.info(f"📊 Enhanced dataframe: {len(enhanced_df):,} rows")
        
        return enhanced_owner_objects, enhanced_df


def test_enhanced_owner_analyzer():
    """Test the enhanced owner analyzer."""
    print("🧪 Testing Enhanced Owner Analyzer")
    print("=" * 50)
    
    # Create sample data
    sample_data = {
        'Property Address': ['123 Main St', '123 Main St', '456 Oak Ave'],
        'Mailing Address': ['123 Main St', '123 Main St', '789 Pine St'],
        'First Name': ['John', 'John', 'Jane'],
        'Last Name': ['Doe', 'Doe', 'Smith'],
        'Seller 1': ['John Doe', 'John Doe', 'Jane Smith'],
        'Property Value': [200000, 200000, 300000],
        'Phone 1': ['555-1234', '555-1234', '555-5678'],
        'Phone Status 1': ['CORRECT', 'CORRECT', 'UNKNOWN'],
        'Phone Type 1': ['MOBILE', 'MOBILE', 'LANDLINE'],
        'Phone Tags 1': ['call_a01', 'call_a01', 'call_a02'],
        'Phone 2': ['555-9999', '555-9999', '555-8888'],
        'Phone Status 2': ['WRONG', 'WRONG', 'CORRECT'],
        'Phone Type 2': ['LANDLINE', 'LANDLINE', 'MOBILE'],
        'Phone Tags 2': ['call_a03', 'call_a03', 'call_a01']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Test analyzer
    analyzer = EnhancedOwnerAnalyzer()
    owner_objects, enhanced_df = analyzer.analyze_dataset(df)
    
    print(f"✅ Created {len(owner_objects)} enhanced owner objects")
    
    for i, owner in enumerate(owner_objects):
        print(f"\n🏠 Owner {i+1}: {owner.seller1_name}")
        print(f"   Type: {'Business' if owner.is_business_owner else 'Individual'}")
        print(f"   Properties: {owner.property_count}")
        print(f"   Total Value: ${owner.total_property_value:,.0f}")
        print(f"   Phone Quality Score: {owner.phone_quality_score:.2f}")
        print(f"   Best Contact: {owner.best_contact_method}")
        print(f"   All Phones: {len(owner.all_phones)}")
        print(f"   Pete Phones: {len(owner.pete_prioritized_phones)}")
        
        # Show phone details
        for j, phone in enumerate(owner.all_phones[:3]):
            print(f"     Phone {j+1}: {phone.number} ({phone.status}, {phone.phone_type})")
    
    print(f"\n📊 Enhanced DataFrame: {len(enhanced_df)} rows")
    print(f"📋 New Columns: {[col for col in enhanced_df.columns if col not in df.columns]}")


if __name__ == "__main__":
    test_enhanced_owner_analyzer() 