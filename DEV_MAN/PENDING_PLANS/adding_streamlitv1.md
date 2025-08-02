# Feature Plan: adding_streamlitv1

## Goal

Implement a Streamlit-based UI for Google Sheets interaction, human-readable info extraction, table viewing, and analysis logging.

---

## Steps

1. **Scaffold Project Structure**

   - [x] Create `backend/`, `frontend/`, `DEV_MAN/`, `plans/`, and `plans/current/` directories.
   - [x] Add `Task.md` and this feature plan.

2. **Set Up Logging**

   - [ ] Add `loguru` to requirements and initialize logging in all scripts.
   - [ ] Ensure all logs and analysis are written to `DEV_MAN/`.

3. **Backend: Google Sheets Client**

   - [ ] Implement `backend/sheets_client.py` for Google Sheets API access (variable sheet ID, extract sheet names, headers, data).
   - [ ] Implement `backend/workflow.py` for analysis (compare sheets, log issues, etc.).

4. **Frontend: Streamlit UI**

   - [ ] Implement `frontend/app.py`:
     - [ ] Input for Google Sheet URL/ID.
     - [ ] Display spreadsheet name, sheet names, headers.
     - [ ] Table view for selected sheet.
     - [ ] Button to run analysis and show results.

5. **Main Entry Point**

   - [ ] Implement `main.py` to select between UI and backend workflows.

6. **Documentation & Diagrams**

   - [ ] Add Mermaid diagrams for architecture and workflow.
   - [ ] Document all progress and issues in `DEV_MAN/`.

7. **Versioning & GitHub**
   - [ ] Commit all changes with clear messages using GitHub CLI.
   - [ ] Tag versions as features progress.

---

## Status

- **In Progress**
- Next: Set up logging and backend client.
