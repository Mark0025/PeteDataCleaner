# Dev_man

## Overview

This project automates the deployment of Google Apps Script code to a Google Apps Script project associated with a Google Sheet. The automation is performed entirely from the terminal/IDE using Python and the Google Apps Script API.

## Features Implemented

### 1. Apps Script Code Deployment

- The project contains a `gas_code.js` file with Google Apps Script code.
- The code is pushed to the target Apps Script project (identified by `SCRIPT_ID` in `.env`) using the `update_gas.py` Python script.
- The deployment includes a required manifest file, `appsscript.json`.

### 2. Apps Script Functionality

- The deployed Apps Script code does the following:
  - Defines a `sendFormEmail(e)` function that:
    - Sends an HTML email to `mark@peterei.com`, `support@peterei.com`, and `jon@ihbuyuers.com` whenever triggered.
    - The email contains all form submission data from the linked Google Sheet, formatted as an HTML table.
  - Defines a `createTrigger()` function that:
    - Sets up a trigger to run `sendFormEmail` on form submission.

### 3. Environment and Credentials

- Uses a `.env` file to store configuration values, including:
  - `SHEET_ID` (Google Sheet ID for form responses)
  - `SCRIPT_ID` (Google Apps Script project ID)
- Uses `client_secret.json` for OAuth2 authentication with Google APIs.

### 4. Automation Workflow

- The `update_gas.py` script:
  - Loads environment variables from `.env`.
  - Authenticates with Google using OAuth2.
  - Reads the Apps Script code and manifest from `gas_code.js` and `appsscript.json`.
  - Pushes both files to the specified Apps Script project.

### 5. Test Email Functionality

- The deployed Apps Script code now includes a `sendTestEmail()` function:
  - When run, it sends a beautifully formatted HTML email to `mark@peterei.com` containing the most recent entry from the linked Google Sheet.
  - The email uses modern, visually appealing table styles for clarity and professionalism.
  - If there are no entries, it notifies the recipient accordingly.

### 6. Running Custom Functions from the Apps Script UI

- Any function defined in the Apps Script code (such as `sendTestEmail`) can be run manually from the Apps Script UI:
  - Open the Apps Script editor attached to your project.
  - Select the function name from the dropdown menu at the top.
  - Click the Run ▶️ button to execute the function.
- This is useful for testing or for one-off administrative actions.

## What the App Does NOT Do

- Does not create the initial Apps Script project or link it to a Google Sheet (must be done manually once).
- Does not manage or deploy triggers automatically from Python (the `createTrigger()` function must be run from the Apps Script environment).
- Does not process or send emails from Python; all email logic is in the Apps Script code.
- Does not interact with Google Sheets or Drive from Python (other than for deployment).

## Usage Summary

1. Place your Apps Script code in `gas_code.js` and manifest in `appsscript.json`.
2. Run `uv run python update_gas.py` to deploy the code to your Apps Script project.
3. In the Apps Script environment, run `createTrigger()` once to set up the email trigger.
4. On each form submission, the Apps Script will send an HTML email with the form data to the specified recipients.
