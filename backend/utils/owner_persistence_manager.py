#!/usr/bin/env python3
"""
Property Owners Persistence Manager

Manages persistent storage and loading of Property Owners data between sessions.
Ensures Owner Objects are always saved and can be retrieved later.
"""

import json
import pickle
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.enhanced_owner_analyzer import EnhancedOwnerObject, EnhancedOwnerAnalyzer


class OwnerPersistenceManager:
    """Manages persistent storage of Property Owners data."""
    
    def __init__(self, base_dir: str = "data/processed"):
        """
        Initialize the Owner Persistence Manager.
        
        Args:
            base_dir: Base directory for storing data (default: data/processed)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.base_dir / "owner_objects").mkdir(exist_ok=True)
        (self.base_dir / "enhanced_data").mkdir(exist_ok=True)
        (self.base_dir / "reports").mkdir(exist_ok=True)
        (self.base_dir / "backups").mkdir(exist_ok=True)
        
        self.logger = logger
    
    def save_owner_objects(self, owner_objects: List[EnhancedOwnerObject], 
                          dataset_name: str = None, 
                          create_backup: bool = True) -> str:
        """
        Save Owner Objects to persistent storage.
        
        Args:
            owner_objects: List of Owner Objects to save
            dataset_name: Name for this dataset (auto-generated if None)
            create_backup: Whether to create a backup of existing data
            
        Returns:
            str: Path to saved data
        """
        if not dataset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_name = f"owner_objects_{timestamp}"
        
        self.logger.info(f"💾 Starting to save {len(owner_objects):,} Owner Objects...")
        
        save_dir = self.base_dir / "owner_objects" / dataset_name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup if requested
        if create_backup:
            self._create_backup(dataset_name)
        
        # Filter out non-EnhancedOwnerObject instances
        valid_objects = [obj for obj in owner_objects if hasattr(obj, 'individual_name')]
        self.logger.info(f"📊 Found {len(valid_objects):,} valid Enhanced Owner Objects out of {len(owner_objects):,} total")
        
        if len(valid_objects) == 0:
            self.logger.warning("⚠️ No valid Enhanced Owner Objects found to save!")
            # Log sample of invalid objects for debugging
            invalid_objects = [obj for obj in owner_objects if not hasattr(obj, 'individual_name')]
            if invalid_objects:
                self.logger.info(f"🔍 Sample invalid objects: {invalid_objects[:3]}")
        
        # Save Enhanced Owner Objects as pickle (preserves all object attributes)
        owner_objects_path = save_dir / "owner_objects.pkl"
        with open(owner_objects_path, 'wb') as f:
            pickle.dump(valid_objects, f)
        self.logger.info(f"✅ Saved {len(valid_objects):,} Enhanced Owner Objects to pickle: {owner_objects_path}")
        
        # Save as JSON for human readability
        owner_objects_json = []
        for obj in valid_objects:  # Use valid_objects instead of owner_objects
            # Skip if not an EnhancedOwnerObject instance
            if not hasattr(obj, 'individual_name'):
                continue
                
            owner_objects_json.append({
                'individual_name': obj.individual_name,
                'business_name': obj.business_name,
                'mailing_address': obj.mailing_address,
                'property_address': obj.property_address,
                'is_individual_owner': obj.is_individual_owner,
                'is_business_owner': obj.is_business_owner,
                'has_skip_trace_info': obj.has_skip_trace_info,
                'total_property_value': obj.total_property_value,
                'property_count': obj.property_count,
                'property_addresses': obj.property_addresses,
                'skip_trace_target': obj.skip_trace_target,
                'confidence_score': obj.confidence_score,
                'seller1_name': obj.seller1_name
            })
        
        json_path = save_dir / "owner_objects.json"
        with open(json_path, 'w') as f:
            json.dump(owner_objects_json, f, indent=2)
        self.logger.info(f"✅ Saved {len(owner_objects_json):,} Owner Objects to JSON: {json_path}")
        
        # Save summary statistics
        summary = self._generate_summary(valid_objects)
        summary_path = save_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"✅ Saved summary statistics: {summary_path}")
        
        # Log sample of saved Owner Objects
        if valid_objects:
            self.logger.info(f"🎯 Sample saved Owner Objects:")
            for i, obj in enumerate(valid_objects[:3], 1):
                owner_type = "Individual+Business" if obj.is_individual_owner and obj.is_business_owner else \
                           "Individual Only" if obj.is_individual_owner else \
                           "Business Only" if obj.is_business_owner else "Unknown"
                
                self.logger.info(f"   {i}. {obj.seller1_name[:50]:<50} | {owner_type:<15} | {obj.confidence_score:.1f} confidence | {obj.property_count} properties")
        
        # Save metadata
        metadata = {
            'dataset_name': dataset_name,
            'saved_at': datetime.now().isoformat(),
            'total_owners': len(valid_objects),
            'file_paths': {
                'owner_objects_pkl': str(owner_objects_path),
                'owner_objects_json': str(json_path),
                'summary': str(summary_path)
            }
        }
        
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"✅ Saved {len(valid_objects):,} Owner Objects to {save_dir}")
        self.logger.info(f"📁 Dataset saved as: {dataset_name}")
        
        return str(save_dir)
    
    def save_enhanced_dataframe(self, df: pd.DataFrame, 
                               dataset_name: str = None) -> str:
        """
        Save enhanced dataframe with Owner Object columns.
        
        Args:
            df: Enhanced dataframe with Owner Object columns
            dataset_name: Name for this dataset
            
        Returns:
            str: Path to saved data
        """
        if not dataset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_name = f"enhanced_data_{timestamp}"
        
        self.logger.info(f"💾 Starting to save enhanced dataframe with {len(df):,} rows...")
        
        save_dir = self.base_dir / "enhanced_data" / dataset_name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for Owner Object columns
        owner_object_columns = [col for col in df.columns if col in [
            'Seller_1', 'Skip_Trace_Target', 'Owner_Confidence', 
            'Owner_Type', 'Property_Count'
        ]]
        
        self.logger.info(f"📊 Found {len(owner_object_columns)} Owner Object columns: {owner_object_columns}")
        
        # Convert to pandas if it's a polars DataFrame
        if hasattr(df, 'to_pandas'):
            df_pandas = df.to_pandas()
        else:
            df_pandas = df
        
        # Save as CSV
        csv_path = save_dir / "enhanced_data.csv"
        df_pandas.to_csv(csv_path, index=False)
        self.logger.info(f"✅ Saved full dataframe ({len(df_pandas):,} rows) to CSV: {csv_path}")
        
        # Save as Excel (with smart engine selection)
        excel_path = save_dir / "enhanced_data.xlsx"
        try:
            # Use xlsxwriter for faster export on large datasets
            if len(df_pandas) > 10000:
                df_pandas.to_excel(excel_path, index=False, engine='xlsxwriter')
            else:
                df_pandas.to_excel(excel_path, index=False, engine='openpyxl')
            self.logger.info(f"✅ Saved full dataframe ({len(df_pandas):,} rows) to Excel: {excel_path}")
        except ImportError:
            # Fallback to openpyxl if xlsxwriter not available
            try:
                df_pandas.to_excel(excel_path, index=False, engine='openpyxl')
                self.logger.info(f"✅ Saved full dataframe ({len(df_pandas):,} rows) to Excel: {excel_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not save Excel file: {e}")
                excel_path = None
        except Exception as e:
            self.logger.warning(f"⚠️ Could not save Excel file: {e}")
            excel_path = None
        
        # Save sample (first 1000 rows)
        sample_path = save_dir / "enhanced_data_sample.csv"
        df_pandas.head(1000).to_csv(sample_path, index=False)
        self.logger.info(f"✅ Saved sample dataframe (1,000 rows) to CSV: {sample_path}")
        
        # Save sample as Excel
        sample_excel_path = save_dir / "enhanced_data_sample.xlsx"
        try:
            df_pandas.head(1000).to_excel(sample_excel_path, index=False, engine='xlsxwriter')
            self.logger.info(f"✅ Saved sample dataframe (1,000 rows) to Excel: {sample_excel_path}")
        except ImportError:
            # Fallback to openpyxl
            try:
                df_pandas.head(1000).to_excel(sample_excel_path, index=False, engine='openpyxl')
                self.logger.info(f"✅ Saved sample dataframe (1,000 rows) to Excel: {sample_excel_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not save sample Excel file: {e}")
                sample_excel_path = None
        except Exception as e:
            self.logger.warning(f"⚠️ Could not save sample Excel file: {e}")
            sample_excel_path = None
        
        # Log sample of enhanced data
        if len(df_pandas) > 0:
            self.logger.info(f"🎯 Sample enhanced data:")
            sample_data = df_pandas.head(3)
            for i, (_, row) in enumerate(sample_data.iterrows(), 1):
                seller1 = row.get('Seller_1', 'N/A')[:40]
                skip_trace = row.get('Skip_Trace_Target', 'N/A')[:40]
                confidence = row.get('Owner_Confidence', 0)
                owner_type = row.get('Owner_Type', 'N/A')
                property_count = row.get('Property_Count', 0)
                
                self.logger.info(f"   {i}. Seller: {seller1:<40} | Skip Trace: {skip_trace:<40} | Confidence: {confidence:.1f} | Type: {owner_type} | Properties: {property_count}")
        
        # Save metadata
        metadata = {
            'dataset_name': dataset_name,
            'saved_at': datetime.now().isoformat(),
            'total_rows': len(df_pandas),
            'total_columns': len(df_pandas.columns),
            'owner_object_columns': owner_object_columns,
            'file_paths': {
                'full_data_csv': str(csv_path),
                'full_data_excel': str(excel_path) if excel_path else None,
                'sample_data_csv': str(sample_path),
                'sample_data_excel': str(sample_excel_path) if sample_excel_path else None
            }
        }
        
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"✅ Saved enhanced dataframe ({len(df_pandas):,} rows) to {save_dir}")
        self.logger.info(f"📁 Dataset saved as: {dataset_name}")
        
        return str(save_dir)
    
    def load_owner_objects(self, dataset_name: str) -> List[EnhancedOwnerObject]:
        """
        Load Owner Objects from persistent storage.
        
        Args:
            dataset_name: Name of the dataset to load
            
        Returns:
            List[EnhancedOwnerObject]: Loaded Enhanced Owner Objects
        """
        load_dir = self.base_dir / "owner_objects" / dataset_name
        
        if not load_dir.exists():
            raise FileNotFoundError(f"Dataset '{dataset_name}' not found at {load_dir}")
        
        # Try pickle first (preserves all object attributes)
        pkl_path = load_dir / "owner_objects.pkl"
        if pkl_path.exists():
            with open(pkl_path, 'rb') as f:
                owner_objects = pickle.load(f)
            self.logger.info(f"✅ Loaded {len(owner_objects):,} Owner Objects from {pkl_path}")
            return owner_objects
        
        # Fallback to JSON
        json_path = load_dir / "owner_objects.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                owner_objects_data = json.load(f)
            
            # Reconstruct Owner Objects
            owner_objects = []
            for data in owner_objects_data:
                obj = EnhancedOwnerObject(
                    individual_name=data.get('individual_name', ''),
                    business_name=data.get('business_name', ''),
                    mailing_address=data.get('mailing_address', ''),
                    property_address=data.get('property_address', ''),
                    is_individual_owner=data.get('is_individual_owner', False),
                    is_business_owner=data.get('is_business_owner', False),
                    has_skip_trace_info=data.get('has_skip_trace_info', False),
                    total_property_value=data.get('total_property_value', 0.0),
                    property_count=data.get('property_count', 0),
                    property_addresses=data.get('property_addresses', []),
                    skip_trace_target=data.get('skip_trace_target', ''),
                    confidence_score=data.get('confidence_score', 0.0),
                    seller1_name=data.get('seller1_name', '')
                )
                owner_objects.append(obj)
            
            self.logger.info(f"✅ Loaded {len(owner_objects):,} Owner Objects from {json_path}")
            return owner_objects
        
        raise FileNotFoundError(f"No Owner Objects data found in {load_dir}")
    
    def load_enhanced_dataframe(self, dataset_name: str) -> pd.DataFrame:
        """
        Load enhanced dataframe from persistent storage.
        
        Args:
            dataset_name: Name of the dataset to load
            
        Returns:
            pd.DataFrame: Loaded enhanced dataframe
        """
        load_dir = self.base_dir / "enhanced_data" / dataset_name
        
        if not load_dir.exists():
            raise FileNotFoundError(f"Dataset '{dataset_name}' not found at {load_dir}")
        
        csv_path = load_dir / "enhanced_data.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Enhanced data not found at {csv_path}")
        
        df = pd.read_csv(csv_path)
        self.logger.info(f"✅ Loaded enhanced dataframe ({len(df):,} rows) from {csv_path}")
        
        return df
    
    def list_saved_datasets(self) -> Dict[str, Dict[str, Any]]:
        """
        List all saved datasets with their metadata.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of dataset names and their metadata
        """
        datasets = {}
        
        # List Owner Objects datasets
        owner_objects_dir = self.base_dir / "owner_objects"
        if owner_objects_dir.exists():
            for dataset_dir in owner_objects_dir.iterdir():
                if dataset_dir.is_dir():
                    metadata_path = dataset_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        datasets[f"owner_objects_{dataset_dir.name}"] = metadata
        
        # List enhanced data datasets
        enhanced_data_dir = self.base_dir / "enhanced_data"
        if enhanced_data_dir.exists():
            for dataset_dir in enhanced_data_dir.iterdir():
                if dataset_dir.is_dir():
                    metadata_path = dataset_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        datasets[f"enhanced_data_{dataset_dir.name}"] = metadata
        
        return datasets
    
    def get_latest_dataset(self, dataset_type: str = "owner_objects") -> Optional[str]:
        """
        Get the name of the most recent dataset.
        
        Args:
            dataset_type: Type of dataset ("owner_objects" or "enhanced_data")
            
        Returns:
            Optional[str]: Name of the latest dataset, or None if none found
        """
        datasets = self.list_saved_datasets()
        
        # Filter by type
        type_datasets = {
            name: metadata for name, metadata in datasets.items() 
            if name.startswith(dataset_type)
        }
        
        if not type_datasets:
            return None
        
        # Find the most recent
        latest = max(type_datasets.items(), key=lambda x: x[1]['saved_at'])
        return latest[0].replace(f"{dataset_type}_", "")
    
    def _create_backup(self, dataset_name: str):
        """Create a backup of existing data."""
        backup_dir = self.base_dir / "backups" / f"{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy existing data if it exists
        existing_dir = self.base_dir / "owner_objects" / dataset_name
        if existing_dir.exists():
            import shutil
            shutil.copytree(existing_dir, backup_dir, dirs_exist_ok=True)
            self.logger.info(f"✅ Created backup at {backup_dir}")
    
    def _generate_summary(self, owner_objects: List[EnhancedOwnerObject]) -> Dict[str, Any]:
        """Generate summary statistics for Owner Objects."""
        # Filter out non-EnhancedOwnerObject instances
        valid_objects = [obj for obj in owner_objects if hasattr(obj, 'individual_name')]
        total_owners = len(valid_objects)
        
        if total_owners == 0:
            return {
                'total_owners': 0,
                'total_properties': 0,
                'total_value': 0,
                'average_properties_per_owner': 0,
                'average_value_per_owner': 0,
                'confidence_breakdown': {
                    'high_confidence': {'count': 0, 'percentage': 0},
                    'medium_confidence': {'count': 0, 'percentage': 0},
                    'low_confidence': {'count': 0, 'percentage': 0}
                },
                'owner_type_breakdown': {
                    'individual_only': {'count': 0, 'percentage': 0},
                    'business_only': {'count': 0, 'percentage': 0},
                    'individual_business': {'count': 0, 'percentage': 0}
                }
            }
        
        # Count by confidence
        high_conf = len([obj for obj in valid_objects if obj.confidence_score >= 0.8])
        medium_conf = len([obj for obj in valid_objects if 0.5 <= obj.confidence_score < 0.8])
        low_conf = len([obj for obj in valid_objects if obj.confidence_score < 0.5])
        
        # Count by owner type
        individual_only = len([obj for obj in valid_objects if obj.is_individual_owner and not obj.is_business_owner])
        business_only = len([obj for obj in valid_objects if obj.is_business_owner and not obj.is_individual_owner])
        both_types = len([obj for obj in valid_objects if obj.is_individual_owner and obj.is_business_owner])
        
        # Calculate totals
        total_properties = sum(obj.property_count for obj in valid_objects)
        total_value = sum(obj.total_property_value for obj in valid_objects)
        
        return {
            'total_owners': total_owners,
            'total_properties': total_properties,
            'total_value': total_value,
            'average_properties_per_owner': total_properties / total_owners if total_owners > 0 else 0,
            'average_value_per_owner': total_value / total_owners if total_owners > 0 else 0,
            'confidence_breakdown': {
                'high_confidence': {'count': high_conf, 'percentage': high_conf/total_owners*100 if total_owners > 0 else 0},
                'medium_confidence': {'count': medium_conf, 'percentage': medium_conf/total_owners*100 if total_owners > 0 else 0},
                'low_confidence': {'count': low_conf, 'percentage': low_conf/total_owners*100 if total_owners > 0 else 0}
            },
            'owner_type_breakdown': {
                'individual_only': {'count': individual_only, 'percentage': individual_only/total_owners*100 if total_owners > 0 else 0},
                'business_only': {'count': business_only, 'percentage': business_only/total_owners*100 if total_owners > 0 else 0},
                'individual_business': {'count': both_types, 'percentage': both_types/total_owners*100 if total_owners > 0 else 0}
            }
        }


def save_property_owners_persistent(owner_objects: List[EnhancedOwnerObject], 
                                   enhanced_df: pd.DataFrame = None,
                                   dataset_name: str = None) -> Dict[str, str]:
    """
    Convenience function to save Property Owners data persistently.
    
    Args:
        owner_objects: List of Owner Objects to save
        enhanced_df: Enhanced dataframe (optional)
        dataset_name: Name for the dataset (auto-generated if None)
        
    Returns:
        Dict[str, str]: Paths to saved data
    """
    manager = OwnerPersistenceManager()
    
    # Save Owner Objects
    owner_objects_path = manager.save_owner_objects(owner_objects, dataset_name)
    
    # Save enhanced dataframe if provided
    enhanced_data_path = None
    if enhanced_df is not None:
        enhanced_data_path = manager.save_enhanced_dataframe(enhanced_df, dataset_name)
    
    return {
        'owner_objects_path': owner_objects_path,
        'enhanced_data_path': enhanced_data_path
    }


def load_property_owners_persistent(dataset_name: str = None) -> Tuple[List[EnhancedOwnerObject], Optional[pd.DataFrame]]:
    """
    Convenience function to load Property Owners data persistently.
    
    Args:
        dataset_name: Name of the dataset to load (uses latest if None)
        
            Returns:
            Tuple[List[EnhancedOwnerObject], Optional[pd.DataFrame]]: Loaded Enhanced Owner Objects and enhanced dataframe
    """
    manager = OwnerPersistenceManager()
    
    # Get dataset name if not provided
    if not dataset_name:
        dataset_name = manager.get_latest_dataset("owner_objects")
        if not dataset_name:
            raise FileNotFoundError("No saved Property Owners datasets found")
    
    # Load Owner Objects
    owner_objects = manager.load_owner_objects(dataset_name)
    
    # Try to load enhanced dataframe
    enhanced_df = None
    try:
        enhanced_df = manager.load_enhanced_dataframe(dataset_name)
    except FileNotFoundError:
        pass  # Enhanced dataframe not available
    
    return owner_objects, enhanced_df


if __name__ == "__main__":
    # Example usage
    manager = OwnerPersistenceManager()
    
    # List saved datasets
    datasets = manager.list_saved_datasets()
    print("📁 Saved Property Owners Datasets:")
    for name, metadata in datasets.items():
        print(f"   {name}: {metadata['total_owners']:,} owners, saved {metadata['saved_at']}")
    
    # Get latest dataset
    latest = manager.get_latest_dataset()
    if latest:
        print(f"\n🕐 Latest dataset: {latest}")
    else:
        print("\n❌ No saved datasets found") 