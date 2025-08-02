// Helper to get the correct sheet by ID from script properties
function getSheet() {
  // SHEET_ID should be set as a script property in Apps Script UI
  var sheetId = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!sheetId) {
    throw new Error('SHEET_ID script property not set. Set it in Apps Script UI > Project Settings > Script Properties.');
  }
  return SpreadsheetApp.openById(sheetId).getSheets()[0];
}

function getFormTitle() {
  var sheetId = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!sheetId) {
    throw new Error('SHEET_ID script property not set.');
  }
  var ss = SpreadsheetApp.openById(sheetId);
  return ss.getName();
}

function getLogoUrl() {
  return "https://drive.google.com/uc?export=view&id=1R00SE5d8MehiJlzcghO2vBQ8QfuZ6K11";
}

function sendFormEmail(e) {
  var recipients = getRecipients();
  var responses = e.values;
  var sheet = getSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var formTitle = getFormTitle();
  var logoUrl = getLogoUrl();

  var html = `
    <div style="font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; background: #f9f9f9; padding: 32px;">
      <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
          <img src="${logoUrl}" alt="PETE Logo" style="height: 48px; margin-bottom: 12px;" />
        </div>
        <h2 style="color: #2d7ff9; text-align: center; margin-bottom: 24px;">New submission on ${formTitle}</h2>
        <table style="width: 100%; border-collapse: collapse; font-size: 16px;">
          <thead>
            <tr>
              <th style="background: #2d7ff9; color: #fff; padding: 12px 8px; text-align: left; border-top-left-radius: 8px;">Field</th>
              <th style="background: #2d7ff9; color: #fff; padding: 12px 8px; text-align: left; border-top-right-radius: 8px;">Value</th>
            </tr>
          </thead>
          <tbody>
            ${headers.map((header, i) => `
              <tr style="background: ${i % 2 === 0 ? '#f4f8fd' : '#fff'};">
                <td style="padding: 10px 8px; border-bottom: 1px solid #e3eaf2;"><b>${header}</b></td>
                <td style="padding: 10px 8px; border-bottom: 1px solid #e3eaf2;">${responses[i]}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;

  for (var i = 0; i < recipients.length; i++) {
    MailApp.sendEmail({
      to: recipients[i],
      subject: "New submission on " + formTitle,
      htmlBody: html
    });
  }
}

function createTrigger() {
  var ss = SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty('SHEET_ID'));
  ScriptApp.newTrigger('sendFormEmail')
    .forSpreadsheet(ss)
    .onFormSubmit()
    .create();
}

function getRecipients() {
  return [
    "mark@peterei.com",
    "support@peterei.com",
    "jon@ihbuyuers.com"
  ];
}

function sendTestEmail() {
  var recipients = getRecipients();
  var sheet = getSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var lastRow = sheet.getLastRow();
  var formTitle = getFormTitle();
  var logoUrl = getLogoUrl();
  var html;

  if (lastRow < 2) {
    html = `<div style="font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; background: #f9f9f9; padding: 32px;">
      <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
          <img src="${logoUrl}" alt="PETE Logo" style="height: 48px; margin-bottom: 12px;" />
        </div>
        <h2 style="color: #2d7ff9; text-align: center; margin-bottom: 24px;">Test Email: No Form Entries on ${formTitle}</h2>
        <p style='font-family:sans-serif;color:#555;'>No form entries found in the sheet.</p>
      </div>
    </div>`;
  } else {
    var lastEntry = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];
    html = `
      <div style="font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; background: #f9f9f9; padding: 32px;">
        <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 32px;">
          <div style="text-align: center; margin-bottom: 24px;">
            <img src="${logoUrl}" alt="PETE Logo" style="height: 48px; margin-bottom: 12px;" />
          </div>
          <h2 style="color: #2d7ff9; text-align: center; margin-bottom: 24px;">New submission on ${formTitle}</h2>
          <table style="width: 100%; border-collapse: collapse; font-size: 16px;">
            <thead>
              <tr>
                <th style="background: #2d7ff9; color: #fff; padding: 12px 8px; text-align: left; border-top-left-radius: 8px;">Field</th>
                <th style="background: #2d7ff9; color: #fff; padding: 12px 8px; text-align: left; border-top-right-radius: 8px;">Value</th>
              </tr>
            </thead>
            <tbody>
              ${headers.map((header, i) => `
                <tr style="background: ${i % 2 === 0 ? '#f4f8fd' : '#fff'};">
                  <td style="padding: 10px 8px; border-bottom: 1px solid #e3eaf2;"><b>${header}</b></td>
                  <td style="padding: 10px 8px; border-bottom: 1px solid #e3eaf2;">${lastEntry[i]}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          <div style="margin-top: 32px; text-align: center; color: #888; font-size: 13px;">This is a test email sent from your Google Apps Script integration.</div>
        </div>
      </div>
    `;
  }

  for (var i = 0; i < recipients.length; i++) {
    MailApp.sendEmail({
      to: recipients[i],
      subject: "New submission on " + formTitle,
      htmlBody: html
    });
  }
}

// To set SHEET_ID as a script property:
// In Apps Script UI: Project Settings > Script Properties > Add SHEET_ID with your Google Sheet ID value. 