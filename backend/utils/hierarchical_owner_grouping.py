#!/usr/bin/env python3
"""
Hierarchical Owner Grouping Utility

Groups owners by mailing address as the unique key identifier,
with hierarchical owner name resolution and property count sorting.
"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from loguru import logger


@dataclass
class HierarchicalOwnerGroup:
    """Represents a hierarchical owner group based on mailing address."""
    
    # Core identification
    owner_name: str = ""
    mailing_address: str = ""
    
    # Property portfolio
    property_count: int = 0
    total_value: float = 0.0
    properties: List[Dict[str, Any]] = None
    
    # Contact information
    phone_quality: float = 0.0
    phone_count: int = 0
    correct_phones: int = 0
    best_contact: str = ""
    
    # Owner classification
    is_business: bool = False
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = []
    
    def __str__(self):
        return f"HierarchicalOwnerGroup({self.owner_name}, {self.property_count} properties, ${self.total_value:,.0f})"


class HierarchicalOwnerGrouper:
    """Groups owners hierarchically by mailing address with proper name resolution."""
    
    def __init__(self):
        self.logger = logger
    
    def determine_owner_name(self, owner) -> str:
        """Determine the best owner name using hierarchy: individual > business > default."""
        if owner.individual_name and owner.individual_name.strip():
            return owner.individual_name.strip()
        elif owner.business_name and owner.business_name.strip():
            return owner.business_name.strip()
        else:
            # Default concatenated name
            first_name = getattr(owner, 'first_name', '')
            last_name = getattr(owner, 'last_name', '')
            owner_name = f"{first_name} {last_name}".strip()
            if not owner_name:
                return "Unknown Owner"
            return owner_name
    
    def group_owners_by_mailing_address(self, owner_objects: List[Any]) -> List[HierarchicalOwnerGroup]:
        """
        Group owners by mailing address as the unique key identifier.
        
        Args:
            owner_objects: List of owner objects (EnhancedOwnerObject or similar)
            
        Returns:
            List of HierarchicalOwnerGroup objects sorted by property count
        """
        self.logger.info(f"🏠 Starting hierarchical owner grouping for {len(owner_objects):,} owners")
        
        # Create hierarchical owner groups based on mailing address
        owner_groups = {}
        
        for owner in owner_objects:
            # Determine the best owner name (hierarchy: individual > business > default)
            owner_name = self.determine_owner_name(owner)
            
            # Use mailing address as unique key for grouping
            mailing_key = owner.mailing_address.strip() if owner.mailing_address else "No Mailing Address"
            
            # Initialize owner group if not exists
            if mailing_key not in owner_groups:
                owner_groups[mailing_key] = HierarchicalOwnerGroup(
                    owner_name=owner_name,
                    mailing_address=mailing_key,
                    properties=[],
                    total_value=0.0,
                    phone_quality=0.0,
                    phone_count=0,
                    correct_phones=0,
                    best_contact='',
                    is_business=False,
                    confidence_score=0.0
                )
            
            group = owner_groups[mailing_key]
            
            # Add properties to this owner group
            if hasattr(owner, 'property_details') and owner.property_details:
                for prop_detail in owner.property_details:
                    # Add all properties (don't filter out same address)
                    group.properties.append({
                        'property_address': prop_detail.property_address,
                        'property_value': prop_detail.property_value,
                        'owner_type': prop_detail.owner_type
                    })
            elif hasattr(owner, 'property_addresses') and owner.property_addresses:
                for prop_addr in owner.property_addresses:
                    group.properties.append({
                        'property_address': prop_addr,
                        'property_value': owner.total_property_value / max(owner.property_count, 1),
                        'owner_type': "Business" if owner.is_business_owner else "Individual"
                    })
            # Fallback: if no property details, add the main property address
            elif hasattr(owner, 'property_address') and owner.property_address:
                group.properties.append({
                    'property_address': owner.property_address,
                    'property_value': owner.total_property_value,
                    'owner_type': "Business" if owner.is_business_owner else "Individual"
                })
            
            # Update group totals
            group.total_value += owner.total_property_value
            group.phone_quality = max(group.phone_quality, getattr(owner, 'phone_quality_score', 0.0))
            if hasattr(owner, 'best_contact_method') and owner.best_contact_method and not group.best_contact:
                group.best_contact = owner.best_contact_method
            group.is_business = group.is_business or getattr(owner, 'is_business_owner', False)
            group.confidence_score = max(group.confidence_score, getattr(owner, 'confidence_score', 0.0))
            group.phone_count += len(getattr(owner, 'all_phones', []))
            group.correct_phones += len([p for p in getattr(owner, 'all_phones', []) if getattr(p, 'status', '') == "CORRECT"])
        
        # Convert to list and filter owners with properties
        owner_list = []
        for mailing_key, group in owner_groups.items():
            group.property_count = len(group.properties)
            if group.property_count > 0:  # Only include owners with properties
                owner_list.append(group)
        
        # Sort by property count (highest first), then by total value
        owner_list.sort(key=lambda x: (x.property_count, x.total_value), reverse=True)
        
        self.logger.info(f"✅ Created {len(owner_list):,} hierarchical owner groups")
        return owner_list
    
    def get_owner_summary_stats(self, owner_groups: List[HierarchicalOwnerGroup]) -> Dict[str, Any]:
        """Get summary statistics for the owner groups."""
        if not owner_groups:
            return {}
        
        total_owners = len(owner_groups)
        total_properties = sum(og.property_count for og in owner_groups)
        total_value = sum(og.total_value for og in owner_groups)
        business_owners = sum(1 for og in owner_groups if og.is_business)
        individual_owners = total_owners - business_owners
        
        # Multi-property owners
        multi_property_owners = sum(1 for og in owner_groups if og.property_count > 1)
        
        # High confidence targets
        high_confidence = sum(1 for og in owner_groups if og.confidence_score >= 0.8)
        medium_confidence = sum(1 for og in owner_groups if 0.6 <= og.confidence_score < 0.8)
        low_confidence = sum(1 for og in owner_groups if og.confidence_score < 0.6)
        
        # Phone quality stats
        avg_phone_quality = sum(og.phone_quality for og in owner_groups) / total_owners if total_owners > 0 else 0
        total_phones = sum(og.phone_count for og in owner_groups)
        total_correct_phones = sum(og.correct_phones for og in owner_groups)
        
        return {
            'total_owners': total_owners,
            'total_properties': total_properties,
            'total_value': total_value,
            'business_owners': business_owners,
            'individual_owners': individual_owners,
            'multi_property_owners': multi_property_owners,
            'high_confidence_targets': high_confidence,
            'medium_confidence_targets': medium_confidence,
            'low_confidence_targets': low_confidence,
            'avg_phone_quality': avg_phone_quality,
            'total_phones': total_phones,
            'total_correct_phones': total_correct_phones,
            'phone_accuracy_rate': (total_correct_phones / total_phones * 100) if total_phones > 0 else 0
        }
    
    def get_top_owners_by_property_count(self, owner_groups: List[HierarchicalOwnerGroup], limit: int = 10) -> List[HierarchicalOwnerGroup]:
        """Get top owners sorted by property count."""
        return owner_groups[:limit]
    
    def get_top_owners_by_value(self, owner_groups: List[HierarchicalOwnerGroup], limit: int = 10) -> List[HierarchicalOwnerGroup]:
        """Get top owners sorted by total property value."""
        return sorted(owner_groups, key=lambda x: x.total_value, reverse=True)[:limit]
    
    def filter_owners_by_type(self, owner_groups: List[HierarchicalOwnerGroup], owner_type: str = "all") -> List[HierarchicalOwnerGroup]:
        """Filter owners by type (business, individual, or all)."""
        if owner_type.lower() == "business":
            return [og for og in owner_groups if og.is_business]
        elif owner_type.lower() == "individual":
            return [og for og in owner_groups if not og.is_business]
        else:
            return owner_groups
    
    def filter_owners_by_confidence(self, owner_groups: List[HierarchicalOwnerGroup], min_confidence: float = 0.0) -> List[HierarchicalOwnerGroup]:
        """Filter owners by minimum confidence score."""
        return [og for og in owner_groups if og.confidence_score >= min_confidence]
    
    def search_owners(self, owner_groups: List[HierarchicalOwnerGroup], search_term: str) -> List[HierarchicalOwnerGroup]:
        """Search owners by name or address."""
        search_term = search_term.lower()
        results = []
        
        for og in owner_groups:
            if (search_term in og.owner_name.lower() or 
                search_term in og.mailing_address.lower() or
                any(search_term in prop['property_address'].lower() for prop in og.properties)):
                results.append(og)
        
        return results


def test_hierarchical_owner_grouping():
    """Test the hierarchical owner grouping functionality."""
    from backend.utils.owner_persistence_manager import load_property_owners_persistent
    
    # Load owner objects
    owner_objects, enhanced_df = load_property_owners_persistent()
    
    if not owner_objects:
        print("❌ No owner objects found")
        return
    
    # Create grouper
    grouper = HierarchicalOwnerGrouper()
    
    # Group owners
    owner_groups = grouper.group_owners_by_mailing_address(owner_objects)
    
    # Get summary stats
    stats = grouper.get_owner_summary_stats(owner_groups)
    
    print(f"📊 Hierarchical Owner Grouping Results:")
    if stats:
        print(f"   Total Owners: {stats.get('total_owners', 0):,}")
        print(f"   Total Properties: {stats.get('total_properties', 0):,}")
        print(f"   Total Value: ${stats.get('total_value', 0):,.0f}")
        print(f"   Business Owners: {stats.get('business_owners', 0):,}")
        print(f"   Individual Owners: {stats.get('individual_owners', 0):,}")
        print(f"   Multi-Property Owners: {stats.get('multi_property_owners', 0):,}")
        print(f"   High Confidence Targets: {stats.get('high_confidence_targets', 0):,}")
        print(f"   Average Phone Quality: {stats.get('avg_phone_quality', 0):.1f}/10")
    else:
        print("   No owner groups created")
    
    # Show top owners by property count
    top_owners = grouper.get_top_owners_by_property_count(owner_groups, 5)
    print(f"\n🏆 Top 5 Owners by Property Count:")
    for i, owner in enumerate(top_owners, 1):
        print(f"   {i}. {owner.owner_name} - {owner.property_count} properties (${owner.total_value:,.0f})")


if __name__ == "__main__":
    test_hierarchical_owner_grouping() 