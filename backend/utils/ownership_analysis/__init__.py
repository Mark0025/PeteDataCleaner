#!/usr/bin/env python3
"""
Ownership Analysis Package

Handles deduplication, grouping, and analysis of property ownership patterns.
"""

from .address_deduplicator import AddressDeduplicator, deduplicate_by_mailing_address
from .owner_identifier import OwnerIdentifier
from .seller_structure_builder import SellerStructureBuilder

__all__ = [
    'AddressDeduplicator',
    'deduplicate_by_mailing_address',
    'OwnerIdentifier', 
    'SellerStructureBuilder'
]
