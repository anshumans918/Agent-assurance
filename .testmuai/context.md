# OpenEMR patient portal (public demo) — standing instructions

These apply to every test in this project, while authoring and while replaying.

## Signing in

- The patient portal login at https://demo.openemr.io/openemr/portal needs all three of
  **Username**, **Password** and **E-Mail Address**. A sign-in with the E-Mail Address
  left empty is rejected and the login page stays on screen.
- If a step gives only a username and password, also fill E-Mail Address with that
  account's address:
  - `Phil1` → `heya@invalid.email.com`
  - `Susan2` → `nana@invalid.email.com`
- Signing in is done when the **Dashboard** heading is visible. If the login page is
  still shown after Log In, reload the login page once and sign in again with all three
  values. The demo accounts are shared with the public, so another visitor's sign-in can
  also end a session; signing in again recovers it.
- The staff application (https://demo.openemr.io/openemr) is a different login with
  Username and Password only.

## Opening a module

- Known demo defect: the green tile buttons on the Dashboard for Appointments, Secure
  Messaging, Health Snapshot, Profile, Billing Summary, Medical Reports, Settings and
  Help do not open their card (the page stays on the tile grid). Try the tile once; if
  the card heading does not appear, do not keep clicking — open the module's page
  directly instead, while signed in:

  | Module | Page (under https://demo.openemr.io/openemr/portal/) |
  |---|---|
  | Secure Messaging | `messaging/messages.php` |
  | Health Snapshot — Current Problems | `get_problems.php` |
  | Health Snapshot — Current Medications | `get_medications.php` |
  | Health Snapshot — Medication Allergies | `get_allergies.php` |
  | Health Snapshot — Active Prescriptions | `get_prescriptions.php` |
  | Health Snapshot — Lab Results | `get_lab_results.php` |
  | Profile | `patient/patientdata?pid=<pid>&user=<username>` |
  | Billing Summary | `report/pat_ledger.php` |
  | Customized Medical History Report | `report/portal_patient_report.php?pid=<pid>` |
  | Download Medical Record Documents | `get_patient_documents.php` |
  | Manage Login Credentials | `account/index_reset.php` |
  | Clinical Documents | the Clinical Documents tile (it is a normal link) |

  `<pid>` is the signed-in patient's id: `1` for Phil1, shown in the Clinical Documents
  tile link. Appointments, Patient Immunization, Select Theme, Default Digital Signature
  and Help have no page of their own; if their card does not open, report that as the
  result rather than looking for another route.

## Shared data — do not change

- Never save a new portal password. On Manage Login Credentials, fill the fields the
  step asks for and only submit when the step expects the change to be **rejected**
  (for example mismatched passwords).
- Messages, appointments and profile changes created by tests should use the reason,
  subject or comment text the step provides ("Automated assurance check - please
  ignore").
