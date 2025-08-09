# 🎯 Pete Data Cleaner

**Smart data preparation assistant that transforms messy spreadsheets into clean, Pete-ready data.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![Tests](https://img.shields.io/badge/Tests-16%20passed-brightgreen.svg)](https://github.com/Mark0025/PeteDataCleaner)

---

## 🚀 What Pete Data Cleaner Does

Pete Data Cleaner is your **smart data preparation assistant** that transforms messy spreadsheets into clean, Pete-ready data. Think of it as having a data expert who knows exactly what Pete needs and automatically fixes common problems.

### 🎯 The Problem We Solve

**Before Pete Data Cleaner:**

- 📱 Phone numbers look like: `4098880401.0`, `8702853184.0` (with annoying .0 endings)
- 📊 Spreadsheets have 30+ phone columns but Pete only needs 5
- 🗂️ Column names are messy: `Phone 1`, `Phone_1`, `phone1`, `PHONE1`
- 📋 Empty columns everywhere cluttering your view
- ⏰ Hours spent manually cleaning and organizing data

**After Pete Data Cleaner:**

- 📱 Clean phone numbers: `4098880401`, `8702853184`
- 🎯 Smart selection of the 5 best phone numbers for Pete
- 🏷️ Consistent, clean column names
- 🧹 Hidden empty columns for clean workspace
- ⚡ Minutes instead of hours

---

## 📦 Installation

### Prerequisites

- **Python 3.12+**
- **Git**

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Mark0025/PeteDataCleaner.git
cd PeteDataCleaner

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the application
uv run python frontend/main_window.py
```

### Alternative Installation (pip)

```bash
# Clone and install
git clone https://github.com/Mark0025/PeteDataCleaner.git
cd PeteDataCleaner
pip install -r requirements.txt
python frontend/main_window.py
```

---

## 🎮 How to Use Pete Data Cleaner

### 1️⃣ **Upload Your Data**

1. Launch the application: `uv run python frontend/main_window.py`
2. Click **"Upload File"** and select your CSV or Excel file
3. Pete automatically:
   - 🔍 Detects your file format
   - 🧹 Strips trailing `.0` from phone numbers
   - 📊 Shows a preview of your cleaned data
   - ✅ Validates that your data is ready for processing

### 2️⃣ **Smart Data Preparation**

Use the **Data Prep Editor** to organize your data:

#### **Column Tools:**

- **Hide/Show Columns:** Right-click columns to hide or show them
- **Rename Columns:** Right-click → "Rename" to clean up column names
- **Merge Columns:** Select multiple columns → "Merge" with custom delimiters
- **Hide Empty ≥90%:** Checkbox to automatically hide mostly empty columns

#### **Data Tools:**

- **📞 Prioritize Phones:** Smart phone number selection
- **🧹 Strip .0:** Remove trailing .0 from numeric strings
- **📊 Sample Data:** Preview large datasets
- **🔄 Transform Data:** Advanced data transformations

### 3️⃣ **Phone Number Intelligence**

Click **"📞 Prioritize Phones"** to see your phone data analysis:

#### **What Pete Analyzes:**

- 📊 **Status Analysis:** Shows counts of 'CORRECT', 'WRONG', 'UNKNOWN' numbers
- 📱 **Type Analysis:** Categorizes by 'MOBILE', 'LANDLINE', 'VOIP'
- 📞 **Call History:** Analyzes tags like `call_a01` (called once), `call_a05` (called 5 times)

#### **Smart Selection Logic:**

- ✅ **Priority 1:** CORRECT numbers (verified working)
- 📱 **Priority 2:** MOBILE numbers (higher connection rate)
- 📞 **Priority 3:** Numbers with fewer call attempts
- ❌ **Excluded:** WRONG numbers (saves Pete time)

### 4️⃣ **Pete Mapping**

Map your cleaned columns to Pete's expected format:

- 🎯 **Smart Suggestions:** Pete suggests the best matches for your columns
- 🏷️ **Clean Headers:** Consistent, readable column names
- ✅ **Validation:** Ensures all required Pete fields are mapped

### 5️⃣ **Export & Done**

Review your final data and export:

- 📊 **Final Preview:** Clean, organized data ready for Pete
- 💾 **Multiple Formats:** Export as CSV, Excel, or Pete's preferred format
- ✅ **Quality Check:** Ensures data meets Pete's requirements

---

## 🔧 Key Features

### ⚡ **Automatic .0 Cleanup**

- **Problem:** Excel exports phone numbers as `4098880401.0`
- **Solution:** Pete automatically strips the `.0` on upload
- **Result:** Clean numbers like `4098880401`

### 🎯 **Smart Phone Prioritization**

- **Input:** 30 phone columns with mixed status
- **Analysis:** Shows status distribution (CORRECT: 312, WRONG: 500, etc.)
- **Output:** 5 best phones selected based on:
  - 🥇 **CORRECT** status (verified working numbers)
  - 📱 **MOBILE** type (higher connection success)
  - 📞 **Call history** (prefer fewer attempts)
  - ❌ **Exclude WRONG** numbers (saves time)

### 🧹 **Hide Empty Columns**

- **Problem:** Spreadsheets cluttered with empty columns
- **Solution:** "Hide Empty ≥90%" checkbox
- **Result:** Clean workspace showing only relevant data

### 📊 **Version History**

- **Undo/Redo:** Every change is tracked
- **Version Names:** Descriptive names like "Prioritize Phones", "Strip .0"
- **Rollback:** Return to any previous state

### 🎨 **Clean Interface**

- **Blue Headers:** Professional, readable design
- **Intuitive Navigation:** Clear buttons and menus
- **Responsive Layout:** Adapts to different screen sizes

---

## 📁 Project Structure

```
PeteDataCleaner/
├── frontend/                 # GUI application
│   ├── main_window.py       # Main application window
│   ├── components/          # Reusable UI components
│   ├── dialogs/            # Modal dialogs
│   ├── toolsui/            # Data tools panel
│   └── data_prep/          # Data preparation editor
├── backend/                 # Core data processing
│   └── utils/              # Data utilities
│       ├── phone_prioritizer.py    # Phone number logic
│       ├── trailing_dot_cleanup.py # .0 cleanup
│       ├── data_standardizer.py    # Data standardization
│       └── preferences.py          # User preferences
├── tests/                  # Test suite
│   ├── test_phone_prioritizer.py
│   ├── test_upload_flow.py
│   └── test_gui_workflow.py
├── upload/                 # Sample data files
├── DEV_MAN/               # Development documentation
└── pyproject.toml         # Project configuration
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/test_phone_prioritizer.py -v
uv run pytest tests/test_upload_flow.py -v
uv run pytest tests/test_gui_workflow.py -v

# Run with coverage
uv run pytest tests/ --cov=backend --cov=frontend
```

**Test Results:** ✅ 16 tests passed, 1 skipped

---

## 📊 Data Transformation Examples

### Phone Number Cleaning

**Input:** `4098880401.0`, `8702853184.0`, `4054104179.0`
**Output:** `4098880401`, `8702853184`, `4054104179`

### Phone Prioritization Logic

**Input:** 30 phone columns with mixed status
**Output:** 5 best phones selected based on:

- 🥇 **CORRECT** status (verified working numbers)
- 📱 **MOBILE** type (higher connection success)
- 📞 **Call history** (prefer fewer attempts)
- ❌ **Exclude WRONG** numbers (saves time)

### Column Organization

**Input:** Messy column names like `Phone_1`, `phone1`, `PHONE1`
**Output:** Clean, consistent names like `Phone 1`, `Phone 2`, etc.

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/Mark0025/PeteDataCleaner.git
cd PeteDataCleaner

# Install development dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run application
uv run python frontend/main_window.py
```

### Project Structure

- **Frontend:** PyQt5-based GUI with modular components
- **Backend:** Pandas-based data processing with utilities
- **Testing:** pytest with pytest-qt for GUI testing
- **Documentation:** Comprehensive DEV_MAN/ structure

### Key Technologies

- **Python 3.12+:** Core language
- **PyQt5:** GUI framework
- **Pandas:** Data manipulation
- **pytest:** Testing framework
- **uv:** Package management

---

## 📈 Performance

### Test Results

- ✅ **16 tests passed** (1 skipped for large files)
- ✅ **Phone prioritization:** Processes 310,724 rows in seconds
- ✅ **GUI responsiveness:** Smooth interface with large datasets
- ✅ **Memory efficient:** Handles large CSV files without issues

### Supported File Formats

- **CSV:** Primary format with automatic encoding detection
- **Excel:** .xlsx and .xls files
- **Large Files:** Handles files up to 200MB+ efficiently

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feat/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation in DEV_MAN/
- Use conventional commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Common Issues

1. **"No module named 'backend'"** → Run `uv sync` to install dependencies
2. **GUI not starting** → Ensure PyQt5 is installed: `uv add PyQt5`
3. **Large file errors** → Files >200MB are skipped automatically

### Getting Help

- 📖 **Documentation:** Check DEV_MAN/ for detailed guides
- 🐛 **Issues:** Report bugs on GitHub
- 💬 **Questions:** Open a GitHub discussion

---

## 🎉 Acknowledgments

- **Pete Team:** For the data requirements and feedback
- **PyQt5 Community:** For the excellent GUI framework
- **Pandas Team:** For powerful data manipulation tools

---

**Made with ❤️ for Pete Data Cleaner**

_Transform your messy data into Pete-ready perfection!_
