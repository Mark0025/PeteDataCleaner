# Plan: GUI-Based Mapping Tool for Data Standardization (v0.6.0)

---

**Status:** In Progress (Final Integration & Full Backend-Frontend Parity)
**Date:** 2024-07-21
**Version:** v0.6.0
**Changelog:**

- v0.6.0: Added final integration plan for full backend-frontend parity. Checklist for all backend features/rules and frontend wiring. Added Mermaid diagram for full workflow. Updated rationale and sequential steps.
- v0.5.0: Added a settings dialog accessible via a gear icon in the UI for all mapping/preview configs (fuzzy threshold, preview row/col count, show/hide unmapped, enable/disable fuzzy, etc.). Settings changes apply live to mapping and preview. Gear/settings icon always visible. All settings changes are powered by backend DataStandardizer and rules config. Updated workflow diagram and sequential steps.

---

## Final Integration & Full Backend-Frontend Parity

### **Backend Features/Rules (from DataStandardizer):**

- [x] Pete headers loaded from Google Sheet/tab (SheetsClient)
- [x] Upload file loading (CSV/XLSX)
- [x] Mapping rules loaded from mapping_rules.json (never_map, explicit_map, concat_fields, fuzzy threshold, etc.)
- [x] Mapping logic: never_map, explicit_map, concat_fields, phone/email pattern, exact/fuzzy match, one-to-one, manual edits
- [x] Preview/transform: DataFrame to Pete format, concatenation, unmapped Pete headers filled, preview logic
- [x] Reporting: Markdown report, unmapped columns, Pete headers not available
- [x] Persistence: Save/load previous mappings for a given sheet/tab

### **Frontend Features to Wire Up:**

- [x] Pete headers fetched from backend (not placeholder)
- [x] Upload file loaded and previewed
- [x] Settings dialog updates rules and menu options live
- [x] Mapping UI uses all backend rules (never_map, explicit_map, fuzzy, etc.) via propose_mapping
- [x] One-to-one mapping enforced in dropdowns
- [x] Manual mapping via dropdowns (and/or custom entry)
- [ ] **[In Progress] Concatenation/multi-select UI for fields like Seller**
- [ ] **[In Progress] Live mapping/preview update on settings change**
- [ ] Previous mapping load/save (offer to load previous mapping for current sheet/tab)
- [x] Preview and download of standardized data (CSV/XLSX)
- [x] Reporting: Generate and view/save backend’s mapping report
- [x] Error handling for backend failures
- [ ] Settings changes update mapping/preview live
- [x] Menu option toggling is robust and reflected in UI
- [x] Docstrings/comments for maintainability

---

**Note:**

- The next steps will be implemented directly in code, with no mockups, for full stack production readiness.

---

## Sequential Steps

- [ ] 1. Review all backend features/rules and ensure understanding
- [ ] 2. Review all frontend code in /current and backend
- [ ] 3. Wire up Pete headers fetching from backend
- [ ] 4. Implement live settings updates for mapping/preview
- [ ] 5. Add concatenation/multi-select UI for fields like Seller
- [ ] 6. Add previous mapping load/save
- [ ] 7. Add reporting (generate/view/save report)
- [ ] 8. Polish error handling and user feedback
- [ ] 9. Add/expand docstrings and comments
- [ ] 10. Final testing and user feedback

---

## Mermaid Diagram

```mermaid
graph TD
    A[Start GUI Mapping Tool (PyQt5)] --> B{Startup Menu (CLI Options)}
    B -->|Workspace| L[Workspace Management (future)]
    B -->|Standardize| M[Standardization Utilities (future)]
    B -->|Rules| N[Rule Management (future)]
    B -->|Backend| O[Backend/Analysis Utilities (future)]
    B -->|Test| P[Run Tests (future)]
    B -->|GUI Mapping Tool| C{Select Data File}
    B -->|Exit| Q[Exit Application]
    C -->|Choose Existing| D[List files in upload/]
    C -->|Upload New CSV| E[File Picker Dialog]
    E --> F[Copy file to upload/]
    D --> G[Load Selected File]
    F --> G
    G --> H[Fetch Pete Headers from Google Sheets]
    H --> I[Display Mapping UI (Dropdowns, One-to-One, Rule/Reason, Concatenation, Toggle Headers, Back to Main Menu, Gear Icon/Settings Dialog, Previous Mapping)]
    I --> J[Preview Standardized Data in Table (Full Columns, Scrollable, Live Settings)]
    J --> K[Save/Export Mapping & Data]
    J --> R[Generate/View Report]
    K --> B
    R --> B
```

---

## Rationale

- Ensures all backend features/rules are fully implemented and respected in the frontend.
- Guarantees robust, user-friendly, and production-ready workflow.
- Provides full traceability, reporting, and maintainability.
- Follows project rules: plan first, checklist, changelog, rationale, and directory hygiene.

---

## Status

- **In Progress: Final integration and full backend-frontend parity.**

---

## Directory Hygiene

- Confirmed correct location: `DEV_MAN/plans/current/gui_mapping_tool.md`.
- No duplicate plans or folders created.

---
