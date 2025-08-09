# 🎯 Custom Export UI & Enhanced Owner Dashboard Plan

**Version:** 1.0  
**Date:** 2025-08-09  
**Status:** 🔄 In Progress  
**Priority:** High

## 🎯 Goal

Create a modular system with:

1. **Pete Exports** - Keep existing (for Pete CRM integration)
2. **Custom Export UI** - New tool for investor analysis
3. **Enhanced Owner Dashboard** - Comprehensive phone data analysis
4. **Modular Structure** - Proper folder organization

## 📁 Modular Folder Structure

```
frontend/
├── components/
│   └── owner_dashboard/           # NEW: Owner dashboard module
│       ├── __init__.py
│       ├── owner_dashboard.py     # Main dashboard component
│       ├── owner_analysis.py      # Owner analysis views
│       ├── phone_analysis.py      # Phone quality analysis
│       ├── llc_analysis.py        # Business entity analysis
│       └── portfolio_analysis.py  # Property portfolio analysis
│
│   └── custom_export/             # NEW: Custom export module
│       ├── __init__.py
│       ├── custom_export_ui.py    # Main export interface
│       ├── export_config.py       # Export configuration
│       ├── header_selector.py     # Header selection interface
│       └── export_preview.py      # Export preview
│
│   └── data_analysis/             # NEW: Data analysis tools
│       ├── __init__.py
│       ├── phone_quality.py       # Phone quality analysis
│       ├── owner_insights.py      # Owner insights
│       └── skip_trace.py          # Skip trace analysis
```

## 🔧 Implementation Strategy

### **Phase 1: Enhanced Owner Objects (Backend)**

**File:** `backend/utils/enhanced_owner_analyzer.py`

**New Classes:**

```python
@dataclass
class EnhancedOwnerObject:
    # Core owner data
    individual_name: str = ""
    business_name: str = ""
    mailing_address: str = ""
    property_address: str = ""
    is_individual_owner: bool = False
    is_business_owner: bool = False
    confidence_score: float = 0.0
    seller1_name: str = ""

    # Property portfolio
    total_property_value: float = 0.0
    property_count: int = 0
    property_addresses: List[str] = None

    # Enhanced phone data
    all_phones: List[PhoneData] = None
    pete_prioritized_phones: List[PhoneData] = None
    phone_quality_score: float = 0.0
    best_contact_method: str = ""

    # Skip trace
    skip_trace_target: str = ""
    has_skip_trace_info: bool = False

    # LLC analysis
    llc_analysis: Dict[str, Any] = None

@dataclass
class PhoneData:
    number: str = ""
    original_column: str = ""
    status: str = ""
    phone_type: str = ""
    tags: str = ""
    priority_score: float = 0.0
    is_pete_prioritized: bool = False
    confidence: float = 0.0
```

### **Phase 2: Custom Export UI (Frontend)**

**File:** `frontend/components/custom_export/custom_export_ui.py`

**Features:**

- [ ] **Header Selection**: Checkbox list of all available headers
- [ ] **Export Presets**: Pete (default), Investor, Custom
- [ ] **Preview Mode**: See what will be exported
- [ ] **Format Selection**: CSV, Excel, JSON
- [ ] **Filter Options**: By owner type, phone quality, etc.

**UI Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 🎯 Custom Export Tool - Investor Analysis              │
├─────────────────────────────────────────────────────────┤
│ 📋 Export Preset: [Pete ▼] [Investor] [Custom]        │
│                                                         │
│ 📊 Available Headers:                                  │
│ ☑️ Property Address    ☑️ Mailing Address             │
│ ☑️ Owner Name         ☑️ Phone 1 (Pete)              │
│ ☑️ Phone 2 (Pete)     ☑️ Phone 3 (Pete)              │
│ ☑️ Phone 4 (Pete)     ☐ Phone 5 (Original)           │
│ ☐ Phone Status 1      ☐ Phone Type 1                  │
│ ☐ Phone Tags 1        ☐ Phone Quality Score           │
│ ☐ LLC Analysis        ☐ Skip Trace Score              │
│                                                         │
│ 🔍 Filters:                                           │
│ Owner Type: [All ▼]   Phone Quality: [All ▼]          │
│                                                         │
│ 📁 Export Format: [CSV ▼] [Excel] [JSON]              │
│ 📊 Preview: [Show/Hide]                               │
│                                                         │
│ [📤 Export] [💾 Save Preset] [❌ Cancel]              │
└─────────────────────────────────────────────────────────┘
```

### **Phase 3: Enhanced Owner Dashboard (Frontend)**

**File:** `frontend/components/owner_dashboard/owner_dashboard.py`

**Features:**

- [ ] **Phone Quality Overview**: Distribution of phone statuses
- [ ] **LLC Analysis**: Business entity breakdown
- [ ] **Skip Trace Opportunities**: Ranked by phone quality
- [ ] **Property Portfolio View**: All properties per owner
- [ ] **Contact Strategy**: Best approach per owner

**Dashboard Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 🏠 Enhanced Owner Dashboard                            │
├─────────────────────────────────────────────────────────┤
│ 📊 Overview Cards:                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Total Owners│ │ Phone Quality│ │ Skip Trace  │        │
│ │   269,669   │ │   Score 8.2 │ │   506       │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                         │
│ 📱 Phone Quality Distribution:                         │
│ ████████████████████████████████████████████████████   │
│ CORRECT: 15,234 | UNKNOWN: 45,678 | WRONG: 12,345      │
│                                                         │
│ 🏢 LLC Analysis:                                       │
│ Business Entities: 23,511 | Individual: 246,158        │
│                                                         │
│ 🎯 Skip Trace Opportunities:                           │
│ High Quality (8.0+): 506 | Medium (6.0-8.0): 1,234    │
│                                                         │
│ [🔍 Search Owners] [📊 Export Analysis] [⚙️ Settings]  │
└─────────────────────────────────────────────────────────┘
```

### **Phase 4: Export Configuration System**

**File:** `frontend/components/custom_export/export_config.py`

**Export Presets:**

```python
EXPORT_PRESETS = {
    'pete': {
        'name': 'Pete CRM Export',
        'description': 'Standard export for Pete CRM integration',
        'headers': [
            'Property Address', 'Mailing Address', 'Owner Name',
            'Phone 1', 'Phone 2', 'Phone 3', 'Phone 4'
        ],
        'filters': {'include_pete_prioritized': True}
    },
    'investor': {
        'name': 'Investor Analysis',
        'description': 'Comprehensive analysis for investment decisions',
        'headers': [
            'Property Address', 'Mailing Address', 'Owner Name',
            'All Phones', 'Phone Status', 'Phone Type', 'Phone Tags',
            'Phone Quality Score', 'LLC Analysis', 'Skip Trace Score',
            'Property Count', 'Total Value'
        ],
        'filters': {'include_all_phones': True}
    },
    'custom': {
        'name': 'Custom Export',
        'description': 'User-defined header selection',
        'headers': [],
        'filters': {}
    }
}
```

## 📋 Implementation Steps

### **Step 1: Create Modular Structure**

- [ ] Create `frontend/components/owner_dashboard/` folder
- [ ] Create `frontend/components/custom_export/` folder
- [ ] Create `frontend/components/data_analysis/` folder
- [ ] Set up `__init__.py` files

### **Step 2: Enhanced Owner Objects**

- [ ] Create `EnhancedOwnerObject` class
- [ ] Create `PhoneData` class
- [ ] Update owner analysis to include phone data
- [ ] Preserve original phone metadata

### **Step 3: Custom Export UI**

- [ ] Create header selection interface
- [ ] Implement export presets
- [ ] Add preview functionality
- [ ] Create export configuration system

### **Step 4: Enhanced Owner Dashboard**

- [ ] Create phone quality analysis view
- [ ] Add LLC analysis section
- [ ] Implement skip trace opportunities
- [ ] Add property portfolio view

### **Step 5: Integration**

- [ ] Integrate with main app
- [ ] Add navigation to new tools
- [ ] Test export functionality
- [ ] Verify dashboard performance

## 🎯 Expected Results

### **Custom Export UI:**

- **Pete Export**: Default preset for Pete CRM
- **Investor Export**: All phone data with quality indicators
- **Custom Export**: User-selectable headers
- **Preview Mode**: See exactly what will be exported
- **Multiple Formats**: CSV, Excel, JSON

### **Enhanced Owner Dashboard:**

- **Phone Quality Metrics**: Distribution of phone statuses
- **LLC Analysis**: Business entity breakdown
- **Skip Trace Opportunities**: Ranked by phone quality
- **Property Portfolio**: All properties per owner
- **Contact Strategy**: Best approach recommendations

### **Modular Benefits:**

- **Clean Separation**: Pete exports vs investor tools
- **Maintainable**: Each module has clear responsibility
- **Extensible**: Easy to add new analysis tools
- **Reusable**: Components can be used elsewhere

## 🚀 Benefits

### **For Pete CRM:**

- **Unchanged Exports**: Pete integration continues working
- **Clear Prioritization**: Pete phones clearly marked
- **Quality Indicators**: Know which phones are best

### **For Investor Analysis:**

- **Complete Phone Data**: All phones with status/tags/types
- **Quality Metrics**: Phone quality scores
- **LLC Insights**: Business entity analysis
- **Custom Exports**: Select exactly what you need

### **For Development:**

- **Modular Structure**: Clean, maintainable code
- **Separation of Concerns**: Pete vs investor functionality
- **Extensible Design**: Easy to add new features

---

**Changelog:**

- v1.0: Initial plan creation
- Designed modular folder structure
- Planned custom export UI
- Designed enhanced owner dashboard
- Separated Pete exports from investor tools
