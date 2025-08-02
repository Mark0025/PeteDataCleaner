# 🚀 Data Import Enhancements Plan (v1.0)

**Created:** 2025-08-02
**Author:** AI Agent

---

## 🎯 Goal & Scope

Enhance the data-prep workflow after file upload so that users receive a clean, concise dataset ready for Pete mapping—with minimal clicks.

Key additions:

1. **Auto Strip `.0` on Upload** – silently clean numeric-like strings when the DataFrame is first loaded (GUI & CLI).
2. **Correct-Number Prioritization** – automatically reorder up to 30 phone columns (REISift) down to Pete’s 5, using status priority:
   1. _CORRECT_
   2. _UNKNOWN_
   3. _NO_ANSWER_
   4. _WRONG / DEAD_
   5. _DNC_ (excluded)
      The first good phone goes to `Phone 1`, second to `Phone 2`, etc.
3. **Hide Empty Columns Option** – checkbox/button on upload to hide any column that is all-null/blank.
4. **Export Options** – buttons to export the prepared DataFrame to `.xlsx` (Excel) and `.csv` from the preview screen.
5. **“Map to Pete Headers” Final Button** – single action that runs the existing mapping flow on the cleaned DataFrame.

---

## ✅ Sequential Steps

- [ ] 1. _Backend_ – move `clean_dataframe()` call into:
      • `backend/utils/data_standardizer.load_upload_file`
      • `frontend/components/file_selector.preview_table` (for immediate UI feedback)
- [ ] 2. _Phone prioritization util_ – create `backend/utils/phone_prioritizer.py` with `select_top_phone_columns(df)` returning cleaned & reordered DF (max 5 phones).
- [ ] 3. _UI Button_ – add "📞 Prioritize Phones" button in Data Tools panel. Clicking it:
      • Runs `select_top_phone_columns`.
      • Shows preview dialog of original vs Pete slots.
      • "Apply" saves new version in DataPrepEditor.
- [ ] 4. _Hide Empty Columns_ – add checkbox “Hide Empty” in FileSelector; when checked, calls existing `filter_empty_columns()` util.
- [ ] 5. _Export Buttons_ – in `frontend/components/standardized_preview_ui.py` add “Export Excel” & “Export CSV” buttons using pandas `to_excel` / `to_csv` with QFileDialog save prompt.
- [ ] 6. _Map to Pete Headers_ – add final button in Preview UI that invokes existing mapping flow (`MainWindow.show_mapping_ui`).
- [ ] 7. Update / add unit tests:
     • phone prioritization logic (edge cases where <5 good phones).
     • hide-empty column option toggles visibility.
     • export functions create files.
- [ ] 8. Update docs, regenerate whats-working.
- [ ] 9. Commit on branch `feat/data-import-enhancements` & open PR referencing this plan.

---

## 🖥️ Mermaid Diagram

```mermaid
graph TD
    A[File Upload] --> B[Auto Strip .0]
    B --> C[Phone Prioritization]
    C --> D[Hide Empty Columns (optional)]
    D --> E[Data Prep Editor]
    E --> F[Preview]
    F --> G[Export CSV/XLSX]
    F --> H[Map to Pete Final]
```

---

## 📋 Status

Current status: **Pending user approval**

---

## 📝 Changelog

- v1.0 – Initial draft (2025-08-02)

---
