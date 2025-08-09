# Phase 1: Enhanced Deduplicator

**Version:** 1.0  
**Date:** 2025-08-09  
**Status:** Planning  
**Branch:** `feat/enhanced-deduplicator`

## 🎯 **Phase 1 Goal**

Enhance the existing duplicate removal dialog to support address-based grouping and smart seller creation, while maintaining all existing functionality.

## 📊 **Data Analysis Results**

### **Owner Patterns Found:**

- **Total Records:** 1,000
- **Unique Owners:** 907 (90.7%)
- **Business Entities:** 142 (15.7% of owners)
- **Individual Owners:** 764 (84.3% of owners)

### **Address Patterns:**

- **Addresses with Multiple Owners:** 47 (4.7%)
- **Addresses with Single Owner:** 863 (95.3%)
- **Owners with Multiple Properties:** 49 (5.4%)

### **Contact Quality:**

- **Phone Columns:** 30 available
- **Status Distribution:** DEAD (most common), UNKNOWN, NO_ANSWER, WRONG, CORRECT
- **CORRECT Numbers:** Only 69 out of 1,000 in Phone 1 (6.9%)

## 🛠️ **Implementation Plan**

### **Step 1: Analyze Current Duplicate Removal Dialog**

**File:** `frontend/dialogs/duplicate_removal_dialog.py`

**Current Features:**

- ✅ All Columns deduplication
- ✅ Selected Columns deduplication
- ✅ Case-insensitive deduplication
- ✅ Keep first/last/none options

**Enhancement Needed:**

- 🆕 Address-based grouping
- 🆕 Smart seller creation
- 🆕 Phone prioritization integration

### **Step 2: Design Enhanced UI**

**New Radio Button Options:**

```
Duplicate Detection Method:
☑️ All Columns (existing)
☑️ Selected Columns (existing)
☑️ Case-Insensitive (existing)
🆕 Address-Based Grouping (NEW)
🆕 Smart Seller Creation (NEW)
```

**Address-Based Grouping Options:**

```
Grouping Strategy:
☑️ Remove full duplicates (same address + seller + phones)
☑️ Create Seller 1,2,3,4,5 from address duplicates
☑️ Apply phone prioritization to each seller
☑️ Hold additional sellers for future Pete processing
```

### **Step 3: Create Smart Seller Creator**

**File:** `backend/utils/smart_seller_creator.py`

**Core Logic:**

```python
def create_seller_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Group by Property Address
    2. For each group:
       - If identical rows → DEDUPE
       - If different sellers → CREATE Seller 1,2,3,4,5
       - Apply phone prioritization to each seller
    3. Return Pete-ready DataFrame
    """
```

**Seller Creation Rules:**

1. **Group by Property Address**
2. **Identify identical rows** (same seller + same phones) → Remove duplicates
3. **For different sellers at same address:**
   - Create Seller 1,2,3,4,5 based on phone prioritization
   - Apply existing phone prioritizer to each seller's phones
   - Concatenate emails for each seller
4. **Hold additional sellers** (6+) for future processing

### **Step 4: Integrate Phone Prioritizer**

**File:** `backend/utils/phone_prioritizer/phone_prioritizer.py`

**Integration Points:**

- Use existing `prioritize()` function for each seller group
- Apply prioritization to Phone 1-30 for each seller
- Map prioritized phones to Pete's Phone 1-5 slots

### **Step 5: Update Pete Header Mapper**

**File:** `backend/utils/pete_header_mapper.py`

**Enhancements:**

- Support Seller 1-5 structure
- Handle multiple sellers per property
- Maintain export status tracking

## 📁 **File Changes**

### **New Files:**

```
backend/utils/smart_seller_creator.py          # NEW: Seller grouping logic
backend/utils/address_grouping_engine.py       # NEW: Address-based grouping
```

### **Modified Files:**

```
frontend/dialogs/duplicate_removal_dialog.py   # ENHANCED: Add new options
backend/utils/pete_header_mapper.py           # ENHANCED: Support Seller 1-5
```

## 🎯 **Success Criteria**

### **Functional Requirements:**

- [ ] Address-based grouping works correctly
- [ ] Smart seller creation creates Seller 1-5
- [ ] Phone prioritization applied per seller
- [ ] Full duplicates removed completely
- [ ] UI maintains all existing functionality

### **Data Quality:**

- [ ] Zero full duplicates in output
- [ ] Optimal phone prioritization per seller
- [ ] Clean Seller 1-5 structure for Pete

### **User Experience:**

- [ ] Clear UI options for new features
- [ ] Preview shows what will happen
- [ ] Maintains existing workflow

## 🔄 **Testing Strategy**

### **Test Scenarios:**

1. **Full Duplicates:** Same address + seller + phones → Should dedupe
2. **Address Duplicates:** Same address + different sellers → Should create Seller 1-5
3. **Mixed Scenario:** Combination of both → Should handle correctly
4. **Phone Prioritization:** Verify CORRECT numbers get priority
5. **Business Entities:** LLCs and individuals handled correctly

### **Test Data:**

- Use sample from `upload/All_RECORDS_12623 (1).csv`
- Create test scenarios with known duplicates
- Verify output matches expected Pete format

## 🚀 **Implementation Steps**

### **Week 1:**

1. **Day 1-2:** Analyze current duplicate removal dialog
2. **Day 3-4:** Design enhanced UI mockups
3. **Day 5:** Create smart seller creator skeleton

### **Week 2:**

1. **Day 1-2:** Implement smart seller creator logic
2. **Day 3-4:** Integrate phone prioritizer
3. **Day 5:** Update Pete header mapper

### **Week 3:**

1. **Day 1-2:** Enhance duplicate removal dialog UI
2. **Day 3-4:** Integration testing
3. **Day 5:** User acceptance testing

## 📋 **Acceptance Criteria**

### **Must Have:**

- [ ] Address-based grouping option in UI
- [ ] Smart seller creation (Seller 1-5)
- [ ] Phone prioritization per seller
- [ ] Full duplicate removal
- [ ] Maintains existing functionality

### **Should Have:**

- [ ] Preview of what will happen
- [ ] Progress indicators for large datasets
- [ ] Error handling for edge cases

### **Could Have:**

- [ ] Export status tracking
- [ ] Business entity detection
- [ ] Contact quality scoring

---

**Changelog:**

- v1.0: Initial Phase 1 plan with detailed implementation steps
