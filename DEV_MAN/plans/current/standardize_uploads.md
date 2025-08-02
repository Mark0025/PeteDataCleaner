# Pete Template Upload Standardizer Plan

**Version:** 1.5.0  
**Changelog:**

- v1.5.0: Add interactive, paginated preview of standardized DataFrame (rows and columns) before accepting mapping (2024-07-21)
- v1.4.0: Add configurable mapping rules file (JSON), rule visibility in review tables, and separate mapped/not-mapped tables (2024-07-21)
- v1.3.0: Add dual table review (full and mapped-only), mapped-only edit mode, mapping versioning/save, and numbered tab selection from available Google Sheet tabs (2024-07-21)
- v1.2.0: Add explicit domain-specific mapping rules, one-to-one mapping, unmatched reporting, and 'Rule/Reason' column in review table (2024-07-21)
- v1.1.0: Add smarter keyword/context filter for mapping and batch mapping review UI (2024-07-21)
- v1.0.0: Initial plan for end-to-end upload standardization utility (2024-07-19)

---

## Goal

- Take any uploaded data file (CSV or Excel) and map its columns to the Pete Template headers (from the specified Google Sheet).
- Output:
  - An Excel file with all upload data, columns in Pete’s order, ready for upload.
  - An Excel file with any columns/rows that could NOT be mapped to Pete’s template.
  - A pretty markdown report in the CLI showing exactly what happened (mappings, unmapped, summary).
  - A versioned mapping file (JSON) for reproducibility and future reuse.
  - A configurable mapping rules file (JSON) for easy rule tweaks.
  - **An interactive, paginated preview of the standardized DataFrame (rows and columns) before accepting the mapping.**

## Sequential Steps

- [ ] 1. Fetch Pete Template headers from the Google Sheet: [Pete Template](https://docs.google.com/spreadsheets/d/11M1wYpVdfQfZOM3y5GSVj75FuYCQ0qVtOt4MbUpbZzw/edit?gid=506597534)
- [ ] 2. List all available tabs in the selected Google Sheet and prompt user to select from a numbered list.
- [ ] 3. Load the uploaded file (CSV or Excel) from `upload/`.
- [ ] 4. Load mapping rules from a config file (`DEV_MAN/mappings/mapping_rules.json`).
- [ ] 5. Apply explicit and config-driven mapping rules to propose mappings, ensuring one-to-one mapping (no duplicates).
- [ ] 6. Show a full mapping table (all upload columns, mapped/unmapped, rule/reason).
- [ ] 7. Show two separate tables: one for mapped columns (upload → Pete, rule/reason), one for not mapped columns (upload, rule/reason). Allow user to edit mapped columns.
- [ ] 8. For each Pete header, if no upload column matches, show as 'NOT AVAILABLE'. For each upload column, if no Pete header matches, show as 'NOT MAPPED'.
- [ ] 9. Save the mapping for reproducibility/versioning (JSON with timestamp in `DEV_MAN/mappings/`).
- [ ] 10. Optionally allow user to load a previous mapping for similar uploads.
- [ ] 11. Transform the data: create a new DataFrame with Pete’s headers, fill mapped columns, leave unmapped Pete columns blank.
- [ ] 12. **Interactive preview: Paginate both rows and columns of the standardized DataFrame before accepting mapping.**
- [ ] 13. Output Excel file 1: Standardized data (Pete headers, ready for upload).
- [ ] 14. Output Excel file 2: Unmapped columns/rows (for review).
- [ ] 15. Log all actions/results to `DEV_MAN/`.
- [ ] 16. Generate a pretty markdown report in the CLI summarizing the mapping, unmapped columns, and output files.

---

## Configurable Mapping Rules (mapping_rules.json)

- `never_map`: List of upload columns (or regex patterns) that should never be mapped.
- `explicit_map`: Dict of upload column → Pete header for explicit mappings (e.g., "Last sold": "Sale Date").
- `phone_pattern`: Regex for phone columns to map (e.g., "^Phone ?\\d+$").
- `email_pattern`: Regex for email columns to map (e.g., "^Email ?\\d+$").
- `concat_fields`: Dict for concatenation rules (e.g., {"Seller": ["First Name", "Last Name"]}).
- All rules are visible in the review tables (rule/reason column).

---

## Mermaid Diagram

```mermaid
flowchart TD
    A[User selects upload file in CLI] --> B[Fetch Pete Template headers from Google Sheet]
    B --> C[List and select tab from available tabs]
    C --> D[Read upload file into DataFrame]
    D --> E[Load mapping rules from config file]
    E --> F[Apply mapping rules, one-to-one]
    F --> G[Show full mapping table]
    G --> H[Show mapped and not mapped tables separately, allow edit]
    H --> I[Save mapping version (JSON)]
    I --> J[Transform data to Pete format]
    J --> K[Interactive Preview: Paginate rows/columns of standardized DataFrame]
    K --> L[User accepts or edits mapping]
    L --> M[Output Excel: Standardized data]
    L --> N[Output Excel: Unmapped columns/rows]
    M --> O[Log/report actions to DEV_MAN/]
    N --> O
    O --> P[CLI: Pretty Markdown report of results]
```

---

## Rationale

- Ensures all uploads are standardized to Pete’s template, regardless of source format.
- Provides full traceability and transparency (logs, reports, reproducible mapping).
- CLI-driven for speed, minimal typing, and developer experience.
- Excel output for compatibility with Pete’s workflow.
- Smarter mapping reduces manual work and errors, especially for ambiguous columns.
- One-to-one mapping and explicit/config rules prevent duplicates and mismatches.
- Versioned mapping files enable reproducibility and easy reuse.
- Tab selection from available list prevents user error.
- Configurable rules allow for rapid iteration and domain adaptation.
- Separate mapped/not-mapped tables improve review and accuracy.
- **Interactive preview ensures the user knows exactly what will be accepted and output, even for wide files.**

---

## Status

- **Awaiting implementation of v1.5.0 (interactive, paginated preview of standardized DataFrame before accepting mapping).**
- No code will be written until this plan is approved.
