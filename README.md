I prepared a  a sales intake form (Google Forms -> Google Sheets) and a Make.com (Integromat) automation that routes each new lead to the relevant departments (Ads, Marketing, Operations, Sales, Finance). Below are the project files (form spec, sample sheet, Make scenario instructions, email templates, README) you can copy, implement, and demonstrate. I’ll tell you what I created and how to run it at the end.

````markdown name=README.md
# Sales Intake + Make.com Routing — Project for CV

Overview
- A demo project that collects sales leads via Google Forms, stores responses in Google Sheets, and uses Make.com to route each lead to the appropriate departments (Ads, Marketing, Operations, Sales, Finance).
- Purpose: show an end-to-end automation demonstrating data capture, conditional routing, mapping, notifications, and error handling.

What I created for you in this repository
- google-form-questions.md — suggested Google Form fields (copy into your Google Form).
- sheet-sample.csv — example Google Sheet headers and 3 test rows (import to test).
- make-scenario-instructions.md — step-by-step Make.com (Integromat) scenario design including modules, filters, mapping, and error handling.
- email-templates.md — email and Slack message templates with variables to paste into Make modules.
- demo-script.md — short script and suggested screenshots/video to show this on your CV or in interviews.

Why this is good for your CV
- Shows ability to design end-to-end automation across Google ecosystem and Make.com.
- Demonstrates conditional logic, data mapping, notifications, and logging.
- Can show performance metrics (time-to-notify, number of leads processed) and test cases.

Quick demo steps
1. Create the Google Form using google-form-questions.md.
2. Link the Form to a Google Sheet (or create a sheet with the headers from sheet-sample.csv and make Forms write to it).
3. Create a Make scenario per make-scenario-instructions.md (use Google Sheets "Watch Rows" or Google Forms "Watch Responses").
4. Add test responses (use sample rows in sheet-sample.csv).
5. Run the scenario and show notifications and the log row updates.

CV bullet examples
- Built an automated lead routing pipeline using Google Forms, Google Sheets and Make.com to automatically notify Ads, Marketing, Sales, Operations and Finance teams on new leads.
- Implemented conditional routing, file handling, and error notifications; reduced manual lead triage time by X% (estimate in demo).
- Technologies: Google Forms, Google Sheets, Google Drive, Make.com (Integromat), Gmail/Slack.

Contact / Support
- If you want, I can produce a downloadable Make scenario JSON (if you want the exact export) or walk you through building the scenario live.
````

````markdown name=google-form-questions.md
# Google Form — Suggested fields for Sales Intake Form

Form title: Sales Lead Intake

Fields (use these exact labels to make mapping easier)
1. Timestamp (Google Forms provides automatic response timestamp)
2. Full name (Short answer) — "Full name"
3. Email (Short answer) — "Email"
4. Phone number (Short answer) — "Phone"
5. Company name (Short answer) — "Company"
6. Product / Service interested in (Dropdown or Multiple choice) — "Product"
   - Example options: "Consulting", "Implementation", "Software license", "Support", "Other"
7. Estimated deal value (Short answer, numeric) — "Deal value (USD)"
8. Expected close date (Date) — "Expected close date"
9. Lead source (Multiple choice) — "Lead source"
   - Options: "Google Ads", "Organic Search", "Referral", "Social", "Email campaign", "Trade show", "Other"
10. Campaign / Ad ID (Short answer, optional) — "Campaign ID"
11. Urgency (Multiple choice) — "Urgency"
    - Options: "Low", "Medium", "High"
12. Implementation required? (Multiple choice) — "Needs implementation"
    - Options: "Yes", "No"
13. Notes (Paragraph) — "Notes"
14. File upload (optional) — "Attachments" (enable if you want to accept PDFs/briefs)
15. Consent checkbox — "I consent to be contacted about this inquiry"

Form settings
- Collect email addresses: optional (we also have an Email field).
- Limit to one response per user: optional for demo.
- Response destination: Link to a Google Sheet.

Tips
- Make sure "Attachments" go to Google Drive; the response sheet will contain Drive file URLs.
- Use dropdowns for consistent values (Product, Lead source, Urgency).
````

```name=sheet-sample.csv
Timestamp,Full name,Email,Phone,Company,Product,Deal value (USD),Expected close date,Lead source,Campaign ID,Urgency,Needs implementation,Notes,Attachments
2025-10-21 09:15:00,Alex Gomez,alex@example.com,+1-555-0100,Acme Corp,Implementation,7500,2025-11-05,Google Ads,GA-1234,High,Yes,"Ready to sign",https://drive.google.com/file/d/EXAMPLE1
2025-10-21 10:42:00,Sarah Lee,sarah@example.com,+1-555-0200,GreenTech,Software license,1200,2025-12-01,Organic Search,,Medium,No,"Budget Q4",""
2025-10-21 11:05:00,Tom H.,tom.h@example.com,+44-20-5555,BlueSky,Consulting,3000,2026-01-15,Referral,REF-202,Low,Yes,"Needs scoping",https://drive.google.com/file/d/EXAMPLE2
```

````markdown name=make-scenario-instructions.md
# Make.com Scenario — Step-by-step instructions

Overview
- Trigger: New row in Google Sheets (the sheet where Google Forms writes responses).
- Flow: Watch Row -> Router -> Branches for Ads, Marketing, Operations, Sales, Finance -> Send notifications -> Update sheet log row -> Error handling.

Recommended approach: Use Google Sheets "Watch Rows" module set to the sheet where Forms writes. It's reliable and gives row data (including file URLs).

Scenario structure (module-by-module)

1) Trigger — Google Sheets > Watch Rows
   - Connection: your Google account
   - Spreadsheet: select the Form responses spreadsheet
   - Sheet: "Form Responses 1" (or the sheet name)
   - Trigger options:
     - Trigger on new rows only
     - If you want instant response, set scenario to "Immediately" and enable webhooks if needed, or schedule every 1 minute.

2) Tools — Parse row / Normalizer (optional)
   - If some fields need normalization (strip currency symbols from Deal value), use "Text aggregator" or "Set variable".
   - Example: create a variable DealValueNumeric = Number( replace(Deal value (USD), /[^0-9.]/g , '') )

3) Router — add one Router module to create parallel branches:
   - Left-most branch: Ads
   - Next: Marketing
   - Next: Operations
   - Next: Sales
   - Next: Finance
   - Final branch: Logging only (master log)

Branch filters (examples you can paste into each branch Filter condition)

- Sales (send every lead to Sales)
  - Condition: true (no filter or always pass)
  - Action: Sales notification

- Ads
  - Condition: "Lead source" equals "Google Ads" OR "Campaign ID" is not empty
  - Action: Send Ads notification

- Marketing
  - Condition: "Lead source" is "Organic Search" OR "Social" OR "Email campaign" OR "Referral"
  - Action: Send Marketing notification
  - Note: If you want marketing copied on most leads, add OR conditions accordingly.

- Operations
  - Condition: "Needs implementation" equals "Yes" OR "Urgency" equals "High" OR DealValueNumeric > 5000
  - Action: Save attachments to Operations folder + send notification

- Finance
  - Condition: DealValueNumeric > 0 (or > 1000 if you only want larger deals)
  - Action: Send Finance notification (include Deal value + payment terms if available)

4) Actions per branch — examples

- Send email (Gmail > Send an email)
  - To: department email (ads@example.com, marketing@example.com, ops@example.com, sales@example.com, finance@example.com)
  - Subject: New lead: {{Full name}} — {{Company}} — ${{Deal value (USD)}}
  - Body: use template variables (see email-templates.md)
  - Attachments: if Attachments field contains Drive URLs, use HTTP or Google Drive > Get a File to attach the file binary, or just include the Drive link.

- Post to Slack (Slack > Post a message)
  - Channel: #ads, #marketing, #ops, etc.
  - Message: short summary + link to sheet row

- Save files to Drive (Google Drive > Upload a file)
  - If response contains Drive file IDs or external URLs, use HTTP module to download (if accessible) then upload to a designated folder per department.

5) Update Google Sheet (Google Sheets > Update a Row)
   - Add columns to your sheet: "Notified (teams)", "Notified at", "Make scenario run id", "Processing status"
   - After notifications, update the row with e.g. Notified (teams): "Sales, Ads" and Notified at: now().

6) Error handler
   - Add Error Handler bundle in Make (scenario settings)
   - On error: send email to admin (you), increment a "Failed attempts" cell, add detailed error row to a "Processing errors" sheet.
   - Optionally retry certain modules with exponential backoff (Make supports repeating/notifications).

Advanced options
- Use conditional delays or review queue: if "Urgency" is High, also send SMS to sales rep (use Twilio module).
- Use Aggregator: if multiple rows come at once, aggregate and send one digest email to marketing every hour.
- Use Webhooks: to integrate with internal CRMs via HTTP > Make a request.

Testing
1. Populate the Google Sheet with the sample rows from sheet-sample.csv.
2. Run the scenario in "Run once" mode in Make; watch the execution flow and logs.
3. Check: department inboxes/Slack channels, updated sheet columns, Drive folder for attachments, and the scenario history/errors.

Security & Permissions
- Use a dedicated Google account or OAuth connection with the minimal scopes needed.
- Mask or do not send full PII to public channels.
- Consider adding an "Internal only" flag for sensitive leads.

Notes about rate limits and quotas
- Google Sheets and Drive have rate limits. For high volume, use batching and exponential backoff.
- Make.com plan limits may restrict run frequency — choose a plan that supports your demo frequency.

If you want, I can convert this into a step-by-step clickable checklist or produce a Make scenario export (json) you can import — tell me which Make account email you will use and I’ll format the export.
````

````markdown name=email-templates.md
# Notification templates (copy into Gmail/Slack modules in Make)

General variables (Make syntax varies; adapt to your module's variables)
- {{Full name}}, {{Email}}, {{Phone}}, {{Company}}, {{Product}}, {{Deal value (USD)}}, {{Expected close date}}, {{Lead source}}, {{Campaign ID}}, {{Urgency}}, {{Notes}}, {{Attachments}}, {{Row link}} (link to the Google Sheet row)

Email — Sales
Subject: New lead: {{Full name}} — {{Company}} — ${{Deal value (USD)}}
Body:
Hi Sales team,

New lead received:
- Name: {{Full name}}
- Company: {{Company}}
- Email: {{Email}}
- Phone: {{Phone}}
- Product: {{Product}}
- Estimated value: ${{Deal value (USD)}}
- Expected close date: {{Expected close date}}
- Lead source: {{Lead source}} (Campaign: {{Campaign ID}})
- Urgency: {{Urgency}}
- Needs implementation: {{Needs implementation}}

Notes:
{{Notes}}

Link to response: {{Row link}}
Attachments: {{Attachments}}

Please follow up within 24 hours.

Thanks,
Lead Automation

Email — Ads
Subject: Ad lead captured — {{Campaign ID}} — {{Full name}}
Body:
Hi Ads,

A lead attributed to Ads/Campaign {{Campaign ID}} was captured:
- Name: {{Full name}}, Company: {{Company}}, Email: {{Email}}, Phone: {{Phone}}
- Deal value: ${{Deal value (USD)}}, Product: {{Product}}
- Notes: {{Notes}}
- Link: {{Row link}}

Please check campaign performance and assign follow-up if needed.

Slack message example
Channel: #ops
Message:
:rotating_light: New high-urgency lead
Name: {{Full name}} | Company: {{Company}} | ${{Deal value (USD)}} | Urgency: {{Urgency}}
Link: {{Row link}}

Finance email
Subject: New deal to review — {{Company}} — ${{Deal value (USD)}}
Body:
Hi Finance,

Please review the following lead for billing/credit checks:
- Company: {{Company}}
- Deal value: ${{Deal value (USD)}}
- Contact: {{Full name}} ({{Email}}, {{Phone}})
- Expected close: {{Expected close date}}
- Notes: {{Notes}}
- Link to response: {{Row link}}

Thanks.

Tips
- Keep messages short and actionable.
- Use direct links to the row or CRM for quick context.
- Add templates for follow-up actions (e.g., "Call within 24h", "Assign account manager").
````

````markdown name=demo-script.md
# Demo script & screenshots for CV presentation

Suggested demo flow (2–4 minutes)
1. Show Google Form: explain fields and why they matter.
2. Submit a sample form entry (use the sample data).
3. Show the Google Sheet row being added (live or via sheet-sample.csv).
4. Open Make scenario run history: show the scenario triggered and the branches that ran.
5. Show notifications:
   - Sales inbox email
   - Ads Slack message or email
   - Operations Drive folder where attachments were copied
   - Finance email if threshold reached
6. Show the Google Sheet updated columns: "Notified (teams)" and timestamps.
7. Show error handling: optionally simulate a failure (e.g., temporarily revoke a Gmail connection) and show the error notification sent to admin.

Screenshots to capture
- Google Form
- Google Sheet with headers and the sample row
- Make scenario diagram (router + branches)
- Make execution history (one successful run)
- Example email or Slack message

One-line pitch for CV
"Built an automated lead intake pipeline using Google Forms, Google Sheets and Make.com to route new leads to Ads, Marketing, Sales, Operations and Finance — including conditional filters, file handling and failure notifications."
````

What I did
- I designed a complete, copy-paste-ready project structure: form fields, a sample sheet, Make.com scenario steps with module-level details and branch filters, notification templates, testing steps, and a demo script you can use for a CV presentation.

What's next (actionable)
- Create the Google Form (copy fields from google-form-questions.md) and link it to a fresh Google Sheet or import sheet-sample.csv to test.
- In Make.com, create a new scenario and implement the modules per make-scenario-instructions.md; paste templates from email-templates.md into your Gmail/Slack modules.
- Run tests using demo-script.md and capture the screenshots/video for your CV.

If you want, I can:
- Generate a ready-to-import Make.com scenario export (JSON) tailored to a specific set of department emails and Drive folder IDs — provide the department email addresses and Drive folder IDs and I’ll create the export file for you.
- Or walk you step-by-step while you create the scenario in your Make account.

Which would you like me to do next: produce an importable Make scenario JSON (you’ll provide target emails/folder IDs), or walk you through building it live?
