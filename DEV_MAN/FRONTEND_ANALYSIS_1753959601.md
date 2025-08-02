# 🎨 Frontend Architecture Analysis

**Components Analyzed:** 8

---

## 📊 Component Distribution

- **Component:** 1 files
- **Configuration:** 1 files
- **Dialog:** 1 files
- **MainWindow:** 1 files
- **Widget:** 4 files

---

## 🔌 Backend Integration

**Files importing backend:** 3 of 8

- `gui_mapping_tool.py` (Dialog)
- `main_window.py` (MainWindow)
- `data_standardizer.py` (Widget)

---

## 🗺️ Data Mapping & Concatenation Capabilities

**Files with mapping logic:** 4
**Files with concatenation:** 1

### Mapping Components:
- `gui_mapping_tool.py` - Methods: save, upload_new_csv, map_to_pete_headers (+11 more)
- `main_window.py` - Methods: upload_new_csv, map_to_pete_headers, show_mapping_ui
- `data_standardizer.py` - Methods: load_pete_headers_from_sheet, load_upload_file, load_rules (+9 more)
- `whatsworking.py` - Methods: analyze_mapping_issues

### Concatenation Components:
- `gui_mapping_tool.py` (Dialog)

---

## 📋 Detailed Component Analysis

### Component Components (1)

#### 📄 `base_component.py`
**Features:** 🖼️ PyQt5
**Complexity:** 5
- **UI Elements:** QWidget
- **Connects To:** frontend.utils.logo_utils

### Configuration Components (1)

#### 📄 `constants.py`
**Complexity:** 0

### Dialog Components (1)

#### 📄 `gui_mapping_tool.py`
**Features:** 🖼️ PyQt5 | 🔌 Backend | 🗺️ Mapping | 🔗 Concatenation
**Complexity:** 61
- **UI Elements:** QComboBox, QLabel, QMainWindow, QTableWidget, QCheckBox, QDialog, QLineEdit, QWidget
- **Event Handlers:** on_file_selected, concatenate_selected_columns
- **Data Methods:** save, upload_new_csv, map_to_pete_headers (+11 more)
- **Connects To:** frontend.utils.data_type_converter, frontend.utils.data_standardizer

### MainWindow Components (1)

#### 📄 `main_window.py`
**Features:** 🖼️ PyQt5 | 🔌 Backend | 🗺️ Mapping
**Complexity:** 17
- **UI Elements:** QComboBox, QLabel, QMainWindow, QDialog, QWidget
- **Data Methods:** upload_new_csv, map_to_pete_headers, show_mapping_ui
- **Connects To:** frontend.components.base_component, frontend.utils.logo_utils, frontend.utils.data_standardizer, frontend.constants

### Widget Components (4)

#### 📄 `__init__.py`
**Complexity:** 0

#### 📄 `data_standardizer.py`
**Features:** 🔌 Backend | 🗺️ Mapping
**Complexity:** 18
- **Data Methods:** load_pete_headers_from_sheet, load_upload_file, load_rules (+9 more)

#### 📄 `data_type_converter.py`
**Complexity:** 7

#### 📄 `whatsworking.py`
**Features:** 🗺️ Mapping
**Complexity:** 5
- **Data Methods:** analyze_mapping_issues

---

## 💡 Architecture Analysis & Recommendations

**Average Component Complexity:** 14.1

### 🚨 High Complexity Components (Consider Refactoring):

- `gui_mapping_tool.py` (Complexity: 61)

### 🔌 Backend Integration Suggestions:

**Components with mapping logic that could benefit from backend integration:**
- `whatsworking.py`

### 🔗 Concatenation Workflow:

**Files handling concatenation (e.g., FirstName + LastName → Seller):**
- `gui_mapping_tool.py` (Dialog)