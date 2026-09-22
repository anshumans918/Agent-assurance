# OpenEMR Patient Portal — Demo Healthcare Application
## Product Requirements Document (PRD)

**Version:** 0.4 (Verified against live demo on 2026-09-15; navigation, login validation and the card-tile defect recorded 2026-09-22)  
**Product:** OpenEMR Patient Portal  
**Type:** Open-source EHR patient portal (public demo instance with synthetic data)  
**Primary user:** Patient  
**Application URL:** https://demo.openemr.io/openemr/portal

---

## Application Access

The OpenEMR Patient Portal is available as a publicly accessible demonstration environment maintained by the OpenEMR project.

**Portal URL:** https://demo.openemr.io/openemr/portal  
**Alternate instances:** https://demo.openemr.io/a/openemr/portal, https://demo.openemr.io/b/openemr/portal  
**Staff (clinic) application:** https://demo.openemr.io/openemr

The demo environment is shared by the public and is reset daily at approximately 08:00 UTC. Data created during a session does not persist beyond the reset, and other visitors may change data during the day.

Portal login requires three values: **Username**, **Password** and **E-Mail Address**. Credentials are publicly documented at https://www.open-emr.org/demo/ and are supplied at runtime; they must not be committed to the repository.

A patient account supports one active session. Signing in again with the same account ends the previous session.

---

## 1. Product Overview

The OpenEMR Patient Portal is a browser-based portal that allows patients of a clinic running OpenEMR to securely access their health information and complete common tasks online.

The portal is connected to the clinic's OpenEMR electronic health record (EHR). Information shown in the portal comes from the patient's chart. Patient changes to profile information and completed documents are sent to clinic staff for review before they are committed to the chart.

The product provides a single dashboard for:

- Completing clinical documents and forms sent by the clinic.
- Viewing past and future appointments and scheduling new appointments.
- Exchanging secure messages with the care team.
- Reviewing a health snapshot (immunizations, medications, prescriptions, allergies, problems, lab results).
- Reviewing and requesting changes to profile information.
- Reviewing a billing summary.
- Viewing and downloading medical reports, including the Summary of Care (C-CDA).
- Managing a digital signature, login credentials and portal theme.

The demo instance uses synthetic patient data. No real patient or protected health information is involved.

---

## 2. Product Vision

The portal gives patients a single digital destination to:

- Understand their current health information.
- Keep their personal, contact and insurance information accurate.
- Manage appointments with the clinic.
- Communicate securely with their care team.
- Complete and sign paperwork before a visit.
- Access, print and download their medical records.
- Review what they owe.

The portal should feel like an extension of the clinic's EHR, where the patient and the clinic work from the same chart.

---

## 3. Product Goals

### Primary Goals

1. Give patients secure, authenticated access to their own chart information.
2. Allow patients to send profile changes to staff for review.
3. Allow patients to view appointments and schedule new ones.
4. Provide secure patient-to-care-team messaging.
5. Allow patients to complete, sign and submit clinic forms online.
6. Allow patients to view and download a Summary of Care and custom medical history reports.
7. Present immunizations, medications, prescriptions, allergies, problems and lab results clearly.

### Secondary Goals

- Support accessible core workflows.
- Provide consistent navigation and terminology.
- Clearly communicate loading, success, error and empty states.
- Keep patient records strictly separated.
- Allow personalisation (theme, digital signature).

---

## 4. Target Users

### 4.1 Patient

The primary user of the portal.

The patient can:

- Sign in and log out.
- View the portal dashboard.
- View profile information and send edits for staff review.
- View immunizations, current medications, active prescriptions, allergies, current problems and lab results.
- View future and past appointments.
- Schedule a new appointment.
- Read, compose and archive secure messages.
- Complete, sign, save as draft and submit clinic forms.
- Upload documents.
- View the billing summary for a date range.
- View and download the Summary of Care (C-CDA).
- Generate a customized medical history report and download it as PDF.
- Download stored medical record documents.
- Set a default digital signature.
- Change login credentials.
- Change the portal theme.

### 4.2 Clinic Staff (Provider / Front Desk)

Staff use the OpenEMR staff application, not the portal.

Staff actions that affect the portal include:

- Enabling portal access for a patient.
- Reviewing and committing profile changes.
- Reviewing submitted documents ("Onsite Portal Reviewed").
- Confirming appointments.
- Replying to patient messages.

Staff-facing functionality is outside the scope of this PRD, except where it produces a result visible in the portal.

### 4.3 Demo Providers

The demo clinic has three providers available for scheduling:

- Donna Lee
- Billy Smith
- Fred Stone

---

# 5. Product Navigation

After login the portal shows the **Dashboard**: a grid of tiles, each with an icon and a green button carrying the module name. A blue **Dashboard** button in the top bar returns to the tile grid from anywhere. There is no left-side menu at desktop width.

Most modules open as cards inside the dashboard page (`home.php`). Selecting a tile's green button expands that module's card in place of the tile grid: the tile grid collapses, the module card (for example **Health Snapshot (Medical Lists)**) becomes visible, and the page does not reload. The address bar is not a reliable signal that a card opened; the visible card heading is.

**Known defect (demo, observed 2026-09-22):** in Chrome, selecting a card tile does not open its card. The dashboard page loads jQuery and Bootstrap four times, so each tile click toggles the card an even number of times and it ends closed; the tile grid stays on screen. Tile-to-card navigation ("selecting a card opens the module") is therefore expected to fail until this is fixed. Each module's content remains reachable from its standalone page in the entry-point table below, and content checks should use that page rather than the tile.

Clinical Documents opens its own page. Some features inside cards open their own pages or dialogs (see the entry points below).

The tiles, in order:

1. Dashboard
2. Clinical Documents
3. Appointments
4. Secure Messaging
5. Health Snapshot
6. Profile
7. Billing Summary
8. Medical Reports
9. Settings
10. Help
11. Logout

There is no separate account dropdown; Settings and Logout are tiles on the Dashboard.

### Module entry points

Paths are relative to the portal root (`https://demo.openemr.io/openemr/portal/`) and open directly in the browser while signed in (a signed-out request returns the login page). "Card" means the module opens in place on `home.php` via its tile. `<pid>` is the signed-in patient's id, visible in the Clinical Documents tile link (`pid=1` for Phil Belford).

| Module | Opens as | Entry point |
|---|---|---|
| Dashboard | Tile grid | `home.php` |
| Clinical Documents | Page | `patient/onsitedocuments?pid=<patient id>` (tile link) |
| Appointments | Card | Appointments tile only (no standalone page) |
| Secure Messaging | Card, hosting the mailbox page | Mailbox page `messaging/messages.php` (heading Secure Messaging) |
| Health Snapshot | Card built from list pages | `get_problems.php` (Current Problems), `get_medications.php` (Current Medications), `get_allergies.php` (Medication Allergies), `get_prescriptions.php` (Active Prescriptions), `get_lab_results.php` (Lab Results); each shows the section's table or **No Results**. Patient Immunization is in the card only |
| Profile | Card | Profile page `patient/patientdata?pid=<pid>&user=<username>` (Patient Portal – Patient Data) |
| Billing Summary | Card, hosting the ledger page | Ledger page `report/pat_ledger.php` (Patient Billing Summary by Date) |
| Medical Reports | Card with sub-cards | Customized Medical History Report `report/portal_patient_report.php?pid=<pid>`; Download Medical Record Documents `get_patient_documents.php` (Download On File Documents) |
| Summary of Care | Page / download | Links inside the Medical Reports card |
| Settings | Card | Manage Login Credentials page `account/index_reset.php` (Change Portal Credentials); Select Theme and Default Digital Signature are in the card only |
| Logout | Page | `logout.php` |

An **About Portal Dashboard** dialog is available with a **Visit Forum** link (OpenEMR community forum) and a **Close** button.

---

# 6. Authentication

## 6.1 Login

The login page (title: **Patient Portal Login**) contains:

- Username field (required).
- Password field (required).
- E-Mail Address field.
- Language selector (default **Default - English (Standard)**, followed by Albanian, Amharic, Arabic, Armenian and other languages).
- **Log In** button.

The demo login page does not show Forgot Password or Register links.

### Product Behavior

When valid Username, Password and E-Mail Address are submitted, the patient is authenticated and taken to the portal Dashboard.

When credentials are invalid, the portal stays on the login page and shows:

> Something went wrong. Please try again.

The error does not reveal which field was wrong or whether the username exists.

If Username or Password is empty, the form is not submitted: the page stays on the login page, no session starts, and the empty field is marked as required and invalid. The message for the empty field is shown by the browser's built-in form validation (a native tooltip, not text on the page), so it is not part of the page content.

Selecting a language changes the portal interface language.

## 6.2 Change Credentials

A patient can change login credentials from **Settings → Manage Login Credentials**.

The change-credentials form includes new password and confirm new password fields. If they differ, the portal shows:

> The new password fields are not the same.

## 6.3 Session

An authenticated session remains active according to the configured timeout.

Only one session per patient account is active at a time; a new login with the same account ends the earlier session.

When a session ends or expires, protected pages return the login page.

On the public demo the patient accounts are shared, so another visitor signing in to the same account can end a session at any time, and a sign-in can occasionally leave the login page displayed. In either case signing in again with the same Username, Password and E-Mail Address, from a freshly loaded login page, restores access to the Dashboard.

## 6.4 Logout

When the patient selects **Logout**:

- The session is terminated.
- The patient is returned to the login page (`index.php?site=default&logout`).
- Portal pages and data endpoints require login again.

---

# 7. Dashboard

The Dashboard is the default page after login. Its heading is **Dashboard**.

## 7.1 Dashboard Cards

The dashboard shows a card for each module, each with a title and short description:

| Card | Description shown |
|---|---|
| Clinical Documents | Clinical forms and documents that have been sent by your clinical staff to be filled out. |
| Appointments | View upcoming appointments and if allowed by your clinical staff make new appointments. |
| Secure Messaging | You can send and receive secure communications with your care team staff through this system. |
| Health Snapshot | See your immunization, medications, active prescriptions, allergy list, current problems list, and lab results. |
| Profile | Review and edit your medical profile information. This includes your basic demographics (name, address, emergency contact). You can also review your insurance information if you use a third party insurer to help pay for treatment of care. |
| Billing Summary | — |
| Medical Reports | Setup your digital signature for signing your clinical documents, update your login credentials, or change application settings in the portal. *(demo currently reuses the Settings description — likely a copy defect)* |
| Settings | Setup your digital signature for signing your clinical documents, update your login credentials, or change application settings in the portal. |

Selecting a card opens the same module as the matching navigation item.

## 7.2 Loading

While a card loads, the portal shows **Loading...** or **Working! Please wait...**.

---

# 8. Profile

## 8.1 Profile View

The Profile card is titled **Profile From Medical Records** and has an **Edit Profile** action.

Information is grouped into sections:

**Who**

- Name.
- External ID.
- DOB.
- Birth Sex.
- S.S.
- Marital Status.
- Sex.

**Contact**

- Address, City, State, Postal Code, Country.
- Mother's Name.
- Emergency Contact, Emergency Phone.
- Home Phone, Work Phone, Mobile Phone.
- Contact Email.

**Choices**

- Provider.
- Pharmacy.
- HIPAA Notice Received.
- Allow Voice Message, Leave Message With, Allow Mail Message, Allow SMS, Allow Email.
- Allow Immunization Registry Use, Allow Immunization Info Sharing.
- Allow Health Information Exchange.
- Allow Patient Portal.

**Employer**

- Occupation.

**Stats**

- Language.

**Insurance**

- Primary, Secondary and Tertiary insurance: provider, plan name, policy number, group number, subscriber details, subscriber employer details.

## 8.2 Edit Profile

Selecting **Edit Profile** opens the editable profile form.

Editable fields include:

- Title, First, Middle, Last.
- Birth Date, Gender, Marital Status.
- Street, City, State, Postal Code, County, Country Code.
- Home Phone, Business Phone, Cell Phone, Contact or Notify Phone, Contact Relationship.
- Email, Email Direct.
- Preferred Language, Race, Ethnicity, Religion, Family Size.
- Mothers Name, Guardians Name.
- Pharmacy Id, Referral Provider.
- Allow Email, Allow SMS, Allow Voice Call, Allow Postal Mail, Allow Notice, Allow Health Info Exchange, Allow Immunization Registry Use, Allow Immunization Info Share, Allow Patient Portal, Hipaa Message.
- Comments about change request.

The form shows the following guidance, which can be closed with **Dismiss**:

> Any changes here will be reviewed by provider staff before committing to your chart.

## 8.3 Send for Review

1. The patient changes one or more fields.
2. The patient selects **Send for Review**.
3. The changes are flagged and staff are notified.
4. Until staff review them, the profile shows a **Pending** state and the chart keeps its original values.

While changes are pending:

- The patient can open the profile and keep editing.
- Patient edits are shown in **blue**; original chart values are shown in **red**.
- Clicking a red or blue value switches that field between the edit and the chart value.
- **Revert Edits** changes all fields back to chart values.
- Sending for review again sends the values currently in the fields.

---

# 9. Health Snapshot

The Health Snapshot card is titled **Health Snapshot (Medical Lists)** and is read-only.

It contains these sections, in order:

## 9.1 Patient Immunization

Lists immunization records.

Empty state:

> No records found.

## 9.2 Current Medications

Columns:

- Drug.
- Start Date.
- Last Modified.
- End Date.

## 9.3 Active Prescriptions

Lists active prescriptions from the chart.

## 9.4 Medication Allergy List

Columns:

- Title.
- Reported Date.
- Start Date.
- End Date.
- Referrer.

## 9.5 Current Problems List

Columns:

- Title.
- Reported Date.
- Start Date.
- End Date.

## 9.6 Lab Results

Lists lab results received into the chart.

## 9.7 Empty State

A list with no records shows:

> No Results

(Patient Immunization uses "No records found.")

---

# 10. Appointments

## 10.1 Appointment Lists

The Appointments card has two sections:

**Future Appointments**

- Empty state: **No Appointments**.
- **Schedule A New Appointment** action.

**Past Appointments**

Each appointment shows:

- Day and date (e.g. Friday, 2018-01-19).
- Time (e.g. 2:30 pm).
- Type (e.g. Office Visit).
- Provider.
- Status.

When more past appointments exist than the display limit, the list ends with:

> Display limit reached More past appointments may exist

## 10.2 Schedule A New Appointment

Selecting **Schedule A New Appointment** opens the **Add New Event** form.

Form fields:

| Field | Details |
|---|---|
| Visit | Office Visit, Established Patient, TeleHealth Established Patient, New Patient, Telehealth New Patient, Health and Behavioral Assessment, Preventive Care Services, Ophthalmological Services |
| Date | Appointment date |
| Time | Hour and minute, with AM / PM selector |
| Duration | Minutes |
| Patient | The signed-in patient (pre-filled) |
| Provider | Lee, Donna · Smith, Billy · Stone, Fred |
| Reason | Free text |

Actions:

- **See Availability** — shows available time slots for the selected provider.
- **Save** — validates and saves the appointment.

Flow:

```text
Appointments
   ↓
Schedule A New Appointment
   ↓
Select Visit type
   ↓
Select Provider
   ↓
See Availability → choose date/time
   ↓
Enter Reason
   ↓
Save
   ↓
Appointment appears under Future Appointments
```

Whether scheduling is allowed is configured by the clinic.

---

# 11. Secure Messaging

Secure Messaging opens as its own page with heading **Secure Messaging**.

## 11.1 Mailbox

Folders, each with a message count:

- Inbox.
- Sent.
- All.
- Archive.

Toolbar:

- **Compose Message**.
- **Actions** menu: Mark all as read, Compose Message, Send Selected to Archive, Refresh.
- **Return Home** / **Exit Mail** to return to the dashboard.

Empty mailbox shows a count of **0** and no message rows.

## 11.2 Message Thread

Opening a message shows the message and **Associated Messages in thread**, with a reply option.

## 11.3 Compose Message

The **Compose Message** dialog contains:

| Field | Details |
|---|---|
| To | Care-team recipient list |
| Subject | Free text with suggestions: General, Insurance, Prior Auth, Bill/Collect, Referral, Pharmacy. Default: General |
| Body | Message text |

Actions:

- **Send**.
- **Cancel**.

## 11.4 Send

When a valid message is sent:

- The message appears in **Sent** and the Sent count increases.
- The message is delivered to the recipient's OpenEMR inbox.

A message without a recipient or body is not sent.

---

# 12. Clinical Documents

Clinical Documents opens the **Documents and Forms** page (title: Patient Portal Documents).

## 12.1 Toolbar

- **Signature** — sign using the patient's digital signature.
- **Print**.
- **Download**.
- **Chart to Onsite Portal Reviewed**.
- **Download Chart History**.
- **Select Form** — choose a form to complete.
- **Activities** — document history.
- **Help**.
- **Reload**.
- **Upload**.
- **Exit to Dashboard**.

## 12.2 Available Forms

The demo clinic provides these forms under **Select Form**:

- General
- Hipaa Document
- Insurance Info
- Medical History
- Privacy Document

## 12.3 Complete a Form

```text
Clinical Documents
   ↓
Select Form
   ↓
Fill in fields
   ↓
Signature (sign where required)
   ↓
Save as Draft  or  Submit Completed
   ↓
Document appears in Activities with status
```

- **Save as Draft** keeps the document editable.
- **Submit Completed** sends it to staff for review.

## 12.4 Activities (Document History)

Columns:

- Id.
- Document.
- Create Date.
- Reviewed Date.
- Status.
- Signed.
- Signed Date.

---

# 13. Billing Summary

The Billing Summary opens **Patient Billing Summary by Date**.

- **From** date.
- **To** date.
- **Submit**.

Before a search, the page shows:

> Please input search criteria above, and click Submit to view results.

After Submit, charges and payments in the date range are listed.

---

# 14. Medical Reports

The Medical Reports card offers four options:

## 14.1 View Summary of Care

Opens a printable Summary of Care document (C-CDA) with the patient's healthcare information, usable for transferring care.

## 14.2 Download Summary of Care

Downloads the Summary of Care (C-CDA).

## 14.3 Customized Medical History Report

Page heading: **Patient Report**.

- **Check All** / **Clear All**.
- Section checkboxes: Demographics, History, Insurance, Billing, Allergies, Medications, Immunizations, Medical Problems, Patient Notes, Transactions, Communications.
- **Issues** — individual allergies, medical problems and medications, each with status (e.g. Active).
- **Encounters & Forms** — individual encounters and forms with dates (e.g. SOAP, Vitals).
- **Generate Report**.
- **Download PDF**.

## 14.4 Download Medical Record Documents

Heading: **Download On File Documents**.

- **Select All Documents** checkbox.
- Individual document checkboxes.
- **Download Selected Documents**.
- Note: "Your files will download as a zip file".

---

# 15. Settings

The Settings card contains:

## 15.1 Default Digital Signature

Opens a signature pad where the patient draws and saves a default signature, used when signing clinical documents.

## 15.2 Manage Login Credentials

Opens the change-credentials form (see 6.2).

## 15.3 Select Theme

- **Current Theme** selector: Cobalt blue, Dark, Forest green, Light, Manila, Solar.
- **Apply** reloads the portal with the selected theme.

---

# 16. Help

Help opens portal help content. Medical Reports and Clinical Documents also have their own Help sections.

---

# 17. Data Model

## Patient

```text
pid
pubpid (External ID)
title
fname
mname
lname
DOB
sex
ss
status (marital)
street
city
state
postal_code
country_code
mothersname
contact_relationship
phone_contact
phone_home
phone_biz
phone_cell
email
email_direct
language
race
ethnicity
religion
occupation
providerID
pharmacy_id
hipaa_notice
hipaa_voice
hipaa_mail
hipaa_allowsms
hipaa_allowemail
allow_imm_reg_use
allow_imm_info_share
allow_health_info_ex
allow_patient_portal
```

## Portal Account

```text
pid
portal_username
portal_login_username
portal_pwd
portal_email
```

## Insurance

```text
pid
type (primary | secondary | tertiary)
provider
plan_name
policy_number
group_number
subscriber_fname
subscriber_lname
subscriber_relationship
subscriber_DOB
subscriber_employer
```

## Provider (User)

```text
id
fname
lname
```

## Appointment (Calendar Event)

```text
pc_eid
pc_pid
pc_aid (provider)
pc_catid (visit type)
pc_eventDate
pc_startTime
pc_duration
pc_apptstatus
pc_hometext (reason)
```

## Issue (Problem / Allergy / Medication)

```text
id
pid
type (medical_problem | allergy | medication)
title
date (reported)
begdate
enddate
referredby
activity
```

## Prescription

```text
id
patient_id
drug
dosage
start_date
active
```

## Immunization

```text
id
patient_id
cvx_code
administered_date
```

## Lab Result

```text
procedure_result_id
result_text
result
units
range
abnormal
date
result_status
```

## Portal Message

```text
id
pid
sender
recipient
title (subject)
body
date
message_status
mail_chain (thread)
```

## Onsite Document

```text
id
pid
doc_type (form name)
create_date
review_date
denial_reason (status)
patient_signed_status
patient_signed_time
```

## Pending Change (Onsite Portal Activity)

```text
id
patient_id
activity (profile | document)
status (waiting | reviewed)
date
```

---

# 18. Relationships Between Modules

```text
Patient
 ├── Portal Account (username, password, email)
 ├── Profile
 │     ├── Insurance
 │     └── Pending Changes → Staff Review
 ├── Health Snapshot
 │     ├── Immunizations
 │     ├── Medications
 │     ├── Prescriptions
 │     ├── Allergies
 │     ├── Problems
 │     └── Lab Results
 ├── Appointments
 │     └── Provider
 ├── Secure Messages
 │     └── Care-team recipient
 ├── Clinical Documents
 │     ├── Digital Signature (Settings)
 │     └── Staff Review
 ├── Billing Summary
 └── Medical Reports
       ├── Summary of Care (C-CDA)
       ├── Customized Medical History Report
       └── Medical Record Documents
```

Examples:

- A scheduled appointment appears under Future Appointments.
- A sent message appears in Sent and the Sent count increases.
- Profile edits sent for review show a Pending state and do not change Profile From Medical Records until staff commit them.
- A submitted form appears in Activities with its status and signed state.
- The default digital signature set in Settings is used when signing documents.
- Allergies, medical problems and medications in Health Snapshot match the Issues listed in the Customized Medical History Report.

---

# 19. Healthcare Interoperability Model

OpenEMR exposes a FHIR R4 (US Core) API and produces C-CDA documents. Portal data maps as follows:

| Portal Data | FHIR Resource |
|---|---|
| Profile | Patient |
| Insurance | Coverage |
| Current problem | Condition |
| Current medication / prescription | MedicationRequest |
| Allergy | AllergyIntolerance |
| Immunization | Immunization |
| Lab result | Observation (laboratory) |
| Vitals | Observation (vital-signs) |
| Appointment | Appointment |
| Provider | Practitioner |
| Clinical document | DocumentReference |
| Summary of Care | C-CDA DocumentReference |

UI, reports and API use the same patient identifier.

---

# 20. Business Rules

### BR-001 — Authentication Required

All portal pages and data require an authenticated session. After logout, protected pages return the login page.

### BR-002 — Three-Factor Login Fields

Login requires a matching Username, Password and E-Mail Address.

### BR-003 — Generic Login Error

Failed login shows a generic error that does not reveal which value was wrong.

### BR-004 — Patient Ownership

A patient can access only their own chart data, appointments, messages, documents and reports.

### BR-005 — Single Session

A new login with the same account ends the previous session.

### BR-006 — Profile Changes Require Review

Profile edits do not change the chart until staff commit them; until then the profile is Pending.

### BR-007 — Read-Only Clinical Data

Immunizations, medications, prescriptions, allergies, problems and lab results cannot be edited in the portal.

### BR-008 — Future Appointments Only

New appointments cannot be scheduled in the past.

### BR-009 — Provider Availability

New appointments should use a time available for the selected provider (See Availability).

### BR-010 — Message Required Fields

A message requires a recipient and body; Subject defaults to General.

### BR-011 — Document Signature

Forms with a signature field must be signed before Submit Completed.

### BR-012 — Draft vs Submitted

Draft documents remain editable; submitted documents go to staff review.

### BR-013 — Password Confirmation

New password and confirm password must match.

### BR-014 — Synthetic, Shared Data

All demo data is synthetic, shared with other visitors and reset daily. Tests must not rely on data created by others.

---

# 21. Empty States

| Module | Empty state |
|---|---|
| Patient Immunization | No records found. |
| Medications, Prescriptions, Allergies, Problems, Lab Results | No Results |
| Future Appointments | No Appointments |
| Secure Messaging folders | Count shows 0, no rows |
| Billing Summary (before search) | Please input search criteria above, and click Submit to view results. |

---

# 22. Error States

| Situation | Behavior |
|---|---|
| Invalid login | "Something went wrong. Please try again." — stays on login page |
| Missing Username or Password | Not submitted; stays on login page; empty field marked required/invalid by browser validation |
| New passwords differ | "The new password fields are not the same." |
| Session ended / logged out | Login page shown |
| Past appointments exceed display limit | "Display limit reached More past appointments may exist" |

Error messages do not expose technical details or patient information.

---

# 23. Loading States

- Dashboard: **Working! Please wait...**
- Health Snapshot lists, Appointments, Customized Medical History Report, Secure Messaging: **Loading...**

Buttons should prevent duplicate submission while processing.

---

# 24. Accessibility

Accessibility is a secondary goal. Its keyboard checks are limited to what can be observed from the page: controls are reachable with Tab and dialogs can be closed with Escape. Full keyboard-only completion of each workflow below is desired but is not an acceptance criterion for this release.

Keyboard-accessible core workflows:

- Login (including Language selector).
- Navigation menu.
- Profile editing and Send for Review.
- Scheduling an appointment.
- Composing and sending a message.
- Completing a form (signature pad may need an accessible alternative).

Interactive elements have meaningful accessible names; form fields have labels.

Pending vs original profile values are shown in blue and red; this should also be conveyed without relying on color alone.

Dialogs (About Portal Dashboard, Compose Message, Add New Event) can be closed with the keyboard and manage focus.

---

# 25. Responsive Design

## Desktop

Left navigation menu with dashboard cards in a grid.

## Tablet

Cards reflow to fewer columns; navigation remains available.

## Mobile

Navigation collapses to a toggle menu. Lists and forms remain usable; wide tables scroll horizontally.

---

# 26. Sample Synthetic Patient — Phil Belford

Observed on the demo on 2026-09-15. Values may change during the day.

**Portal login:** Username / Password / E-Mail Address supplied at runtime (`OPENEMR_PORTAL_USER`, `OPENEMR_PORTAL_PASSWORD`, `OPENEMR_PORTAL_EMAIL`)

| Field | Value |
|---|---|
| Name | Phil Belford |
| External ID | 1 |
| DOB | 1972-02-09 |
| Sex | Male |
| Marital Status | Single |
| Address | 6666 String Street, Longview, Florida 44433, USA |
| Emergency Contact | Wilma, 222-333-4444 |
| Contact Email | heya@invalid.email.com |
| Provider | Billy Smith |
| Occupation | Pen |
| Language | English |
| Primary Insurance | Aekna — Bad Plan, Policy 555, Group 444 |

### Health Snapshot

- **Current Medications:** Norvasc, Lisinopril
- **Active Prescriptions:** No Results
- **Allergies:** penicillin, iodine
- **Current Problems:** HTN, Chronic Renal Insuficiency
- **Lab Results:** No Results
- **Immunizations:** No records found.

### Appointments

- **Future:** No Appointments
- **Past:** Office Visits with Billy Smith, 2:30 pm, weekdays from 2018-01-19 (display limit reached)

### Encounters & Forms (Customized Report)

- SOAP, Vitals (dated the day of the demo reset)

---

# 27. Sample Synthetic Patient — Susan Underwood

Observed on the demo on 2026-09-15.

**Portal login:** supplied at runtime (`OPENEMR_PORTAL_USER_2`, `OPENEMR_PORTAL_PASSWORD_2`, `OPENEMR_PORTAL_EMAIL_2`)

| Field | Value |
|---|---|
| Name | Susan Ardmore Underwood |
| External ID | 2 |
| DOB | 1967-02-08 |
| Sex | Female |
| Marital Status | Married |
| Address | 3454 Apple Road, Longview 44533 |
| Contact Email | nana@invalid.email.com |
| Provider | Donna Lee |

### Health Snapshot

- **Current Medications:** Metformin, Lipitor, Lisinopril
- **Allergies:** No Results
- **Current Problems:** diabetes
- **Lab Results:** No Results

### Appointments

- **Future:** No Appointments
- **Past:** Office Visits with Donna Lee, 11:00 am, weekdays from 2018-01-19

Signing in as Susan must never show Phil's data (e.g. Norvasc, penicillin, HTN, Billy Smith), and signing in as Phil must never show Susan's data (e.g. Metformin, diabetes, Donna Lee).

---

# 28. Example Patient Experience

```text
Log In (Username, Password, E-Mail Address)
   ↓
Dashboard
   ↓
Open Health Snapshot → review medications, allergies, problems
   ↓
Open Profile → verify name, DOB, provider
   ↓
Edit Profile → change phone → Send for Review → see Pending
   ↓
Open Appointments → Schedule A New Appointment → See Availability → Save
   ↓
Open Secure Messaging → Compose Message → Send → check Sent
   ↓
Open Clinical Documents → Select Form (Medical History) → Sign → Submit Completed
   ↓
Open Medical Reports → View Summary of Care
   ↓
Customized Medical History Report → select Allergies + Medications → Generate Report
   ↓
Settings → Select Theme → Apply
   ↓
Logout
```

---

# 29. Future Product Capabilities

Not part of this scope:

- Forgot Password and patient self-registration (not enabled on the demo).
- Secure Chat.
- Online payments.
- Prescription refill requests.
- Telehealth video visits.
- Proxy / family access.
- Third-party SMART on FHIR app access.
- Staff-side review workflows.

---

# 30. Product Release Scope

### Account

- Login, logout, session handling, change credentials.

### Patient Information

- Profile view, edit and Send for Review.

### Health Snapshot

- Immunizations, medications, prescriptions, allergies, problems, lab results.

### Care Management

- Future and past appointments, schedule a new appointment.

### Communication

- Secure Messaging (folders, compose, send, archive).

### Documents and Reports

- Clinical Documents (select, sign, draft, submit, upload, history).
- Summary of Care view and download.
- Customized Medical History Report and PDF.
- Download Medical Record Documents.

### Financial

- Billing Summary by date.

### Settings

- Default digital signature, login credentials, theme.

### Experience

- Loading, empty and error states; responsive layout; accessibility.

---

# 31. Product Definition of Done

The portal is ready for demonstration when:

1. A patient can log in with username, password and email, and log out.
2. Invalid login shows a generic error and stays on the login page.
3. The dashboard shows all module cards.
4. Profile shows the correct patient's demographics and insurance.
5. Profile edits can be sent for review and show Pending.
6. Health Snapshot shows the patient's medications, allergies and problems.
7. Past appointments are listed and a new appointment can be scheduled.
8. A secure message can be composed and sent and appears in Sent.
9. A form can be selected, signed and submitted, and appears in Activities.
10. Summary of Care can be viewed; a customized report can be generated.
11. Billing Summary returns results for a date range.
12. Theme can be changed.
13. Each patient sees only their own data.
14. Core workflows work on desktop and mobile layouts.

---

# 32. Product Context Summary

The OpenEMR Patient Portal is the patient-facing side of the OpenEMR EHR.

Core entities:

```text
Patient
Portal Account
Insurance
Provider
Appointment
Immunization
Medication
Prescription
Allergy
Problem
Lab Result
Secure Message
Onsite Document
Pending Change
Report (C-CDA, Patient Report)
```

Core capabilities:

```text
Authenticate
   ↓
View dashboard
   ↓
Review health snapshot
   ↓
Review and update profile
   ↓
Manage appointments
   ↓
Communicate with care team
   ↓
Complete clinical documents
   ↓
Access medical reports
   ↓
Manage settings
```

This document is the product source of truth for building the OpenEMR Patient Portal assurance suite.

---

# Appendix A — Verification Status

Verified on the live demo on 2026-09-15 by signing in as both demo patients (read-only; nothing was submitted):

- ✅ Login fields, language options, invalid-login message, logout redirect.
- ✅ Single session per account (a second login ends the first).
- ✅ Navigation items and dashboard card text.
- ✅ Profile sections, Edit Profile fields and review guidance.
- ✅ Health Snapshot sections, columns and empty states.
- ✅ Appointment lists and Add New Event form fields, options and buttons.
- ✅ Secure Messaging folders, actions and Compose Message fields.
- ✅ Clinical Documents toolbar, form list, Save as Draft / Submit Completed, history columns.
- ✅ Billing Summary form, Medical Reports options, Customized report sections, Settings options.
- ✅ Phil Belford and Susan Underwood data and separation.

Corrected on 2026-09-22 from the first full evidence run and the dashboard's HTML:

- Navigation is a Dashboard tile grid with a top-bar Dashboard button, not a left-side menu; tiles expand in-page cards (Bootstrap collapse), and a page-level entry point table was added.
- Empty Username/Password is reported by browser-native validation, not page text.
- Keyboard-only completion of whole workflows was moved out of the acceptance criteria.
- The shared demo accounts can lose their session to other visitors; signing in again recovers.
- Card tiles do not open their cards in Chrome (jQuery/Bootstrap loaded four times; confirmed in a real headless Chrome, where `$('#lists').collapse('show')` does open it). Standalone pages for each module were verified to load while signed in and added to the entry-point table.

Not yet exercised (would change shared demo data) — confirm during test authoring:

1. What happens after **Save** on a new appointment (status shown, validation messages for past dates or missing fields).
2. Messages delivered after **Send**, and validation messages for a missing recipient or body.
3. Profile **Send for Review** confirmation text and Pending indicator wording.
4. Document **Submit Completed** status values in Activities and signature-required validation.
5. Change credentials behavior (should not be run against shared demo accounts).
6. Mobile layout and keyboard accessibility behavior.
7. Invalid login message: observed through the browser; the portal may show a different message for a wrong email vs a wrong password.
