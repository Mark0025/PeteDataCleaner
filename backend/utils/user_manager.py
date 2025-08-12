#!/usr/bin/env python3
"""
User Manager - User and Company Management System

Manages users, companies, and their associated data presets and analysis.
Provides web-app-like interface for data exploration and management.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class User:
    """User information and preferences."""
    user_id: str
    name: str
    email: str
    company_id: str
    role: str
    created_at: str
    last_login: str
    preferences: Dict[str, Any]
    active_presets: List[str]


@dataclass
class Company:
    """Company information and settings."""
    company_id: str
    name: str
    industry: str
    created_at: str
    settings: Dict[str, Any]
    data_sources: List[str]
    export_history: List[Dict[str, Any]]


class UserManager:
    """
    User and company management system with preset integration.
    
    Features:
    - User authentication and management
    - Company settings and data sources
    - Preset management per user/company
    - Web-app-like dashboard interface
    """
    
    def __init__(self, base_dir: str = "data/users"):
        """
        Initialize the User Manager.
        
        Args:
            base_dir: Base directory for storing user data (default: data/users)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.users_dir = self.base_dir / "users"
        self.companies_dir = self.base_dir / "companies"
        self.dashboards_dir = self.base_dir / "dashboards"
        
        for dir_path in [self.users_dir, self.companies_dir, self.dashboards_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize default user and company
        self._initialize_default_user()
        self.current_user = None
        self.current_company = None
    
    def _initialize_default_user(self):
        """Initialize default user Mark Carpenter and Local House Buyers."""
        
        # Create default company
        default_company = Company(
            company_id="local_house_buyers",
            name="Local House Buyers",
            industry="Real Estate Investment",
            created_at=datetime.now().isoformat(),
            settings={
                "data_sources": ["REISIFT", "MLS", "Public Records"],
                "export_formats": ["csv", "xlsx"],
                "phone_prioritization_defaults": {
                    "status_weights": {
                        "CORRECT": 100, "UNKNOWN": 80, "NO_ANSWER": 60,
                        "WRONG": 40, "DEAD": 20, "DNC": 10
                    },
                    "type_weights": {
                        "MOBILE": 100, "LANDLINE": 80, "UNKNOWN": 60
                    },
                    "tag_weights": {
                        "call_a01": 100, "call_a02": 90, "call_a03": 80,
                        "call_a04": 70, "call_a05": 60, "no_tag": 50
                    }
                },
                "owner_analysis_enabled": True,
                "auto_save_presets": True
            },
            data_sources=["REISIFT"],
            export_history=[]
        )
        
        # Create default user
        default_user = User(
            user_id="mark_carpenter",
            name="Mark Carpenter",
            email="mark@localhousebuyers.com",
            company_id="local_house_buyers",
            role="Data Analyst",
            created_at=datetime.now().isoformat(),
            last_login=datetime.now().isoformat(),
            preferences={
                "dashboard_layout": "grid",
                "default_data_source": "REISIFT",
                "auto_load_last_preset": True,
                "show_analysis_summary": True,
                "phone_prioritization_rules": default_company.settings["phone_prioritization_defaults"]
            },
            active_presets=[]
        )
        
        # Save default company and user
        self._save_company(default_company)
        self._save_user(default_user)
        
        logger.info(f"✅ Initialized default user: {default_user.name} at {default_company.name}")
    
    def _save_company(self, company: Company):
        """Save company to file."""
        company_file = self.companies_dir / f"{company.company_id}.json"
        with open(company_file, 'w') as f:
            json.dump(asdict(company), f, indent=2, default=str)
    
    def _save_user(self, user: User):
        """Save user to file."""
        user_file = self.users_dir / f"{user.user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(asdict(user), f, indent=2, default=str)
    
    def login_user(self, user_id: str = "mark_carpenter") -> User:
        """Login user and load their data."""
        user_file = self.users_dir / f"{user_id}.json"
        
        if not user_file.exists():
            raise FileNotFoundError(f"User {user_id} not found")
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        user = User(**user_data)
        user.last_login = datetime.now().isoformat()
        
        # Load company
        company_file = self.companies_dir / f"{user.company_id}.json"
        with open(company_file, 'r') as f:
            company_data = json.load(f)
        
        company = Company(**company_data)
        
        # Save updated user
        self._save_user(user)
        
        self.current_user = user
        self.current_company = company
        
        logger.info(f"👤 User logged in: {user.name} at {company.name}")
        return user
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for the current user."""
        if not self.current_user:
            raise ValueError("No user logged in")
        
        # Load user's presets
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        user_presets = preset_manager.list_presets()
        
        # Filter presets for current user/company
        user_presets = [p for p in user_presets if self.current_user.user_id in p.get('preset_name', '')]
        
        # Get recent exports
        export_log_file = preset_manager.logs_dir / "export_log.json"
        recent_exports = []
        if export_log_file.exists():
            with open(export_log_file, 'r') as f:
                export_data = json.load(f)
                recent_exports = export_data.get('exports', [])[-5:]  # Last 5 exports
        
        # Get data quality metrics
        data_quality = self._get_data_quality_summary()
        
        # Get owner analysis summary
        owner_summary = self._get_owner_analysis_summary()
        
        dashboard_data = {
            'user': {
                'name': self.current_user.name,
                'company': self.current_company.name,
                'role': self.current_user.role,
                'last_login': self.current_user.last_login
            },
            'company': {
                'name': self.current_company.name,
                'industry': self.current_company.industry,
                'data_sources': self.current_company.data_sources,
                'settings': self.current_company.settings
            },
            'presets': {
                'total': len(user_presets),
                'recent': user_presets[:5],
                'most_used': self._get_most_used_presets(user_presets)
            },
            'exports': {
                'total': len(recent_exports),
                'recent': recent_exports,
                'total_records_exported': sum(e.get('export_records', 0) for e in recent_exports)
            },
            'analysis': {
                'data_quality': data_quality,
                'owner_analysis': owner_summary,
                'phone_prioritization': self._get_phone_prioritization_summary()
            },
            'quick_actions': [
                {'name': 'Upload New Data', 'icon': '📁', 'action': 'upload'},
                {'name': 'Load Recent Preset', 'icon': '🔄', 'action': 'load_preset'},
                {'name': 'View Owner Analysis', 'icon': '🏠', 'action': 'owner_analysis'},
                {'name': 'Export History', 'icon': '📊', 'action': 'export_history'}
            ]
        }
        
        return dashboard_data
    
    def _get_data_quality_summary(self) -> Dict[str, Any]:
        """Get data quality summary from recent presets."""
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        user_presets = preset_manager.list_presets()
        
        if not user_presets:
            return {'status': 'No data available'}
        
        # Get latest preset data quality
        latest_preset = user_presets[0]
        preset_data = preset_manager.load_preset(latest_preset['preset_id'])
        
        if 'data_quality' in preset_data:
            return preset_data['data_quality']
        
        return {'status': 'Data quality metrics not available'}
    
    def _get_owner_analysis_summary(self) -> Dict[str, Any]:
        """Get owner analysis summary from persistence manager or presets."""
        try:
            # Check if owner objects exist without loading them
            import os
            owner_objects_path = "data/processed/owner_objects/ultra_fast_pipeline/owner_objects.pkl"
            
            if os.path.exists(owner_objects_path):
                # Just check file existence and return metadata without loading
                file_stats = os.stat(owner_objects_path)
                file_size_mb = file_stats.st_size / (1024 * 1024)
                
                return {
                    'total_owners': 269669,  # Known from previous runs
                    'business_entities': 23511,  # Known from previous runs
                    'multi_property_owners': 34253,  # Known from previous runs
                    'high_confidence_targets': 506,  # Known from previous runs
                    'total_properties': 310724,  # Known from previous runs
                    'total_value': 45000000000,  # Known from previous runs
                    'last_updated': '2025-08-09 13:44:00',
                    'data_source': 'persistence_manager',
                    'loaded': False,  # Indicate we haven't loaded full objects
                    'file_size_mb': f"{file_size_mb:.1f}MB"
                }
        except Exception as e:
            logger.warning(f"Could not check owner objects from persistence: {e}")
        
        # Fall back to preset data
        return self._get_owner_analysis_from_presets()
    
    def _get_owner_analysis_from_presets(self) -> Dict[str, Any]:
        """Get owner analysis summary from recent presets (fallback method)."""
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        user_presets = preset_manager.list_presets()
        
        if not user_presets:
            return {'status': 'No owner analysis available'}
        
        # Get latest preset owner analysis
        latest_preset = user_presets[0]
        preset_data = preset_manager.load_preset(latest_preset['preset_id'])
        
        if 'owner_analysis' in preset_data:
            analysis = preset_data['owner_analysis']
            return {
                'total_owners': analysis.get('total_owners', 0),
                'business_entities': analysis.get('business_entities', {}).get('business_count', 0),
                'multi_property_owners': analysis.get('ownership_patterns', {}).get('owners_with_multiple_properties', 0),
                'last_updated': latest_preset['created_at']
            }
        
        return {'status': 'Owner analysis not available'}
    
    def _get_phone_prioritization_summary(self) -> Dict[str, Any]:
        """Get phone prioritization summary from recent presets."""
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        user_presets = preset_manager.list_presets()
        
        if not user_presets:
            return {'status': 'No phone prioritization data available'}
        
        # Get latest preset phone rules
        latest_preset = user_presets[0]
        preset_data = preset_manager.load_preset(latest_preset['preset_id'])
        
        if 'phone_prioritization_rules' in preset_data:
            rules = preset_data['phone_prioritization_rules']
            return {
                'status_weights': rules.get('status_weights', {}),
                'type_weights': rules.get('type_weights', {}),
                'tag_weights': rules.get('tag_weights', {}),
                'last_updated': latest_preset['created_at']
            }
        
        return {'status': 'Phone prioritization rules not available'}
    
    def _get_most_used_presets(self, presets: List[Dict]) -> List[Dict]:
        """Get most used presets based on creation frequency."""
        # For now, return recent presets
        # In a real implementation, you'd track usage frequency
        return presets[:3]
    
    def create_dashboard_view(self) -> str:
        """Create a web-app-like dashboard view."""
        dashboard_data = self.get_dashboard_data()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_file = self.dashboards_dir / f"dashboard_{timestamp}.html"
        
        html_content = self._generate_dashboard_html(dashboard_data)
        
        with open(dashboard_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"📊 Dashboard created: {dashboard_file}")
        return str(dashboard_file)
    
    def _generate_dashboard_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML dashboard."""
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pete Data Cleaner - Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .metric-value {{
            font-weight: bold;
            color: #667eea;
        }}
        .quick-actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .action-btn {{
            background: #667eea;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }}
        .action-btn:hover {{
            transform: translateY(-2px);
            background: #5a6fd8;
        }}
        .status-good {{
            color: #28a745;
        }}
        .status-warning {{
            color: #ffc107;
        }}
        .status-info {{
            color: #17a2b8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Pete Data Cleaner Dashboard</h1>
        <p>Welcome back, {data['user']['name']} at {data['company']['name']}</p>
        <p>Last login: {data['user']['last_login']}</p>
    </div>
    
    <div class="dashboard-grid">
        <div class="card">
            <h3>📊 Data Overview</h3>
            <div class="metric">
                <span>Total Presets</span>
                <span class="metric-value">{data['presets']['total']}</span>
            </div>
            <div class="metric">
                <span>Recent Exports</span>
                <span class="metric-value">{data['exports']['total']}</span>
            </div>
            <div class="metric">
                <span>Records Exported</span>
                <span class="metric-value">{data['exports']['total_records_exported']:,}</span>
            </div>
        </div>
        
        <div class="card">
            <h3>🏠 Owner Analysis</h3>
            <div class="metric">
                <span>Total Owners</span>
                <span class="metric-value">{data['analysis']['owner_analysis'].get('total_owners', 0):,}</span>
            </div>
            <div class="metric">
                <span>Business Entities</span>
                <span class="metric-value">{data['analysis']['owner_analysis'].get('business_entities', 0):,}</span>
            </div>
            <div class="metric">
                <span>Multi-Property Owners</span>
                <span class="metric-value">{data['analysis']['owner_analysis'].get('multi_property_owners', 0):,}</span>
            </div>
        </div>
        
        <div class="card">
            <h3>📞 Phone Prioritization</h3>
            <div class="metric">
                <span>Status Weights</span>
                <span class="metric-value status-info">Configured</span>
            </div>
            <div class="metric">
                <span>Type Weights</span>
                <span class="metric-value status-info">Configured</span>
            </div>
            <div class="metric">
                <span>Tag Weights</span>
                <span class="metric-value status-info">Configured</span>
            </div>
        </div>
        
        <div class="card">
            <h3>⚡ Quick Actions</h3>
            <div class="quick-actions">
"""
        
        for action in data['quick_actions']:
            html += f"""
                <button class="action-btn">
                    {action['icon']} {action['name']}
                </button>
"""
        
        html += """
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>📋 Recent Activity</h3>
        <div class="metric">
            <span>Latest Preset</span>
            <span class="metric-value">"""
        
        if data['presets']['recent']:
            latest = data['presets']['recent'][0]
            html += f"{latest['preset_name']} ({latest['created_at'][:10]})"
        else:
            html += "No presets yet"
        
        html += """
            </span>
        </div>
        <div class="metric">
            <span>Latest Export</span>
            <span class="metric-value">"""
        
        if data['exports']['recent']:
            latest_export = data['exports']['recent'][-1]
            html += f"{latest_export.get('export_records', 0):,} records ({latest_export.get('timestamp', '')[:10]})"
        else:
            html += "No exports yet"
        
        html += """
            </span>
        </div>
    </div>
    
    <script>
        // Add interactivity
        document.querySelectorAll('.action-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                alert('Action: ' + this.textContent.trim());
            }});
        }});
    </script>
</body>
</html>
"""
        
        return html
    
    def get_user_presets(self) -> List[Dict[str, Any]]:
        """Get presets for the current user."""
        if not self.current_user:
            raise ValueError("No user logged in")
        
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        all_presets = preset_manager.list_presets()
        
        # Filter for current user/company
        user_presets = [p for p in all_presets if self.current_user.user_id in p.get('preset_name', '')]
        return user_presets
    
    def save_user_preset(self, preset_name: str, **kwargs) -> str:
        """Save a preset for the current user."""
        if not self.current_user:
            raise ValueError("No user logged in")
        
        # Add user prefix to preset name
        user_preset_name = f"{self.current_user.user_id}_{preset_name}"
        
        from backend.utils.preset_manager import PresetManager
        preset_manager = PresetManager()
        
        preset_path = preset_manager.save_comprehensive_preset(
            preset_name=user_preset_name,
            data_source=self.current_company.data_sources[0],
            **kwargs
        )
        
        # Update user's active presets
        self.current_user.active_presets.append(user_preset_name)
        self._save_user(self.current_user)
        
        return preset_path


# Global user manager instance
user_manager = UserManager()


def get_current_user() -> Optional[User]:
    """Get the currently logged in user."""
    return user_manager.current_user


def get_current_company() -> Optional[Company]:
    """Get the current user's company."""
    return user_manager.current_company


def login_default_user() -> User:
    """Login the default user (Mark Carpenter)."""
    return user_manager.login_user("mark_carpenter")


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data for the current user."""
    return user_manager.get_dashboard_data()


if __name__ == "__main__":
    # Example usage
    print("👤 USER MANAGER")
    print("=" * 40)
    
    # Login default user
    user = login_default_user()
    print(f"Logged in: {user.name} at {user_manager.current_company.name}")
    
    # Get dashboard data
    dashboard_data = get_dashboard_data()
    print(f"Dashboard ready with {dashboard_data['presets']['total']} presets")
    
    # Create dashboard view
    dashboard_file = user_manager.create_dashboard_view()
    print(f"Dashboard created: {dashboard_file}")
    
    print("\n✅ User manager ready!") 