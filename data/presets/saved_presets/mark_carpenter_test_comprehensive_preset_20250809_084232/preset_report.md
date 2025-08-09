# 📊 Data Processing Preset Report
**Preset Name:** mark_carpenter_test_comprehensive_preset
**Preset ID:** mark_carpenter_test_comprehensive_preset_20250809_084232
**Data Source:** REISIFT
**Created:** 2025-08-09T08:42:32.433480

## 📈 Data Summary
- **Original Data:** 100 rows × 15 columns
- **Prepared Data:** 100 rows × 15 columns
- **Export Data:** 50 rows × 15 columns

## 📞 Phone Prioritization
### Status Weights:
```json
{
  "CORRECT": 100,
  "UNKNOWN": 80,
  "NO_ANSWER": 60,
  "WRONG": 40,
  "DEAD": 20,
  "DNC": 10
}
```

### Type Weights:
```json
{
  "MOBILE": 100,
  "LANDLINE": 80,
  "UNKNOWN": 60
}
```

### Tag Weights:
```json
{
  "call_a01": 100,
  "call_a02": 90,
  "call_a03": 80,
  "call_a04": 70,
  "call_a05": 60,
  "no_tag": 50
}
```

## 🏠 Owner Analysis
- **Total Owners:** 95
- **Business Entities:** 12
- **Multi-Property Owners:** 8

## 🔧 Data Preparation Steps
### Version History:
```json
[
  {
    "action": "Strip .0",
    "details": "Removed trailing .0 from numeric-like strings",
    "timestamp": "2025-08-09T08:42:32.432452"
  },
  {
    "action": "Phone Prioritization",
    "details": "Prioritized phones using custom rules",
    "timestamp": "2025-08-09T08:42:32.432465"
  },
  {
    "action": "Owner Analysis",
    "details": "Analyzed ownership patterns and business entities",
    "timestamp": "2025-08-09T08:42:32.432469"
  }
]
```

## 📁 Files Included
- `metadata.json` - Preset metadata and summary
- `phone_prioritization_rules.json` - Custom phone prioritization rules
- `owner_analysis.json` - Owner analysis results
- `data_prep_summary.json` - Data preparation steps
- `original_data_sample.csv` - Sample of original data
- `prepared_data_sample.csv` - Sample of prepared data
- `export_data_sample.csv` - Sample of export data
- `column_comparison.json` - Column mapping comparison
- `data_quality.json` - Data quality metrics
- `preset_report.md` - This report

## 🔍 How to Use This Preset
1. Load the preset using the preset manager
2. Apply the same phone prioritization rules
3. Reference the owner analysis for marketing insights
4. Use the data quality metrics for validation
5. Compare column mappings for consistency
