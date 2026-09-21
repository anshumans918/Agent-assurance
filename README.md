# OpenEMR Patient Portal · Agentic Assurance & Evidence in GitHub Actions

A GitHub Actions pipeline that starts from a **healthcare product requirements document** and
ends with a **sealed evidence pack** and a **requirement-level coverage gate**. `kane-cli`
runs every stage, and no tests are written by hand.

This repo is modeled on
[christybmanjila/healthcare-assurance-demo](https://github.com/christybmanjila/healthcare-assurance-demo).
That demo bundles a small Flask clinic site and starts it inside the job. This repo tests a
real open-source EHR instead: the public **OpenEMR demo patient portal**.

App under test: **https://demo.openemr.io/openemr/portal**. It is a shared public demo with
synthetic data only and is reset daily at about 08:00 UTC.

---

## The story in one line

Most QA pipelines can tell you *tests passed*. This one tells you **which requirements are
proven, by which run, with the screenshots to back it**.

```
requirements/openemr-patient-portal-prd.md
        │  kane-cli context ingest + extract
        ▼
   context graph  (use-cases, reviewed, commit-chained)
        │  kane-cli design tests
        ▼
   designed *_test.md  (ACs → scenarios → 1:1 tests)
        │  kane-cli testrun run   (against the live OpenEMR demo)
        ▼
   ONE sealed .evidence pack  ──  kane-cli evidence validate --profile L1
        │  kane-cli cover gaps
        ▼
   designed × proven ribbon  →  PR comment + build gate
```

## The application under test

[OpenEMR](https://www.open-emr.org/) is a widely used open-source electronic health record
(EHR). Its patient portal lets a patient:

- sign in with a username, password and email address
- review a health snapshot (medications, allergies, problems, lab results)
- edit their profile and send the changes for staff review
- view and schedule appointments
- exchange secure messages with the care team
- complete and sign clinical forms
- view billing and medical reports (C-CDA Summary of Care)
- change settings

`requirements/openemr-patient-portal-prd.md` describes all of this. It was verified by hand
against the live demo on 2026-09-15, and Appendix A lists what was verified and what was
not. The two demo patients are **Phil Belford** and **Susan Underwood**. Their data is
recorded in the PRD so the designed tests can check that each patient sees only their own
records.

## What's in the repo

| Path | What it does |
|---|---|
| `requirements/openemr-patient-portal-prd.md` | The single source of truth. Editing it re-opens the graph. |
| `.github/workflows/openemr-portal-assurance-evidence.yml` | The three-stage pipeline. |
| `.github/actions/setup-kane/action.yml` | Installs kane-cli, signs in without a browser, and points it at the runner's Chrome. |
| `scripts/assurance.sh` | Runs ingest → extract → review → design, and treats exit code 3 as a pause, not a failure. |
| `scripts/coverage_gate.py` | Turns the coverage ribbon into a job summary and a pass/fail gate. |
| `scripts/test_data.py`, `test-data/openemr-portal.json` | Supply the tests' `{{variables}}`, including portal credentials from secrets. They refuse to run a suite that is missing any variable. |

## Setup

Add these repository secrets (Settings → Secrets and variables → Actions):

| Secret | Value |
|---|---|
| `LT_USERNAME` | TestMu AI / LambdaTest username |
| `LT_ACCESS_KEY` | TestMu AI / LambdaTest access key |
| `TESTMUAI_PROJECT_ID` | `kane-cli projects list` |
| `TESTMUAI_FOLDER_ID` | `kane-cli folders list` |

The portal logins don't need secrets. `scripts/test_data.py` defaults to the demo's
published accounts from [open-emr.org/demo](https://www.open-emr.org/demo/): Phil Belford
(patient 1) and Susan Underwood (patient 2). To point the pipeline at a private OpenEMR,
set any of these optional secrets and they override the defaults:

| Optional secret | Overrides |
|---|---|
| `OPENEMR_PORTAL_USER` / `_PASSWORD` / `_EMAIL` | Patient 1 login |
| `OPENEMR_PORTAL_USER_2` / `_PASSWORD_2` / `_EMAIL_2` | Patient 2 login |

Then push, open a PR that touches `requirements/`, or run the workflow manually from the
Actions tab.

### Test data

`testrun` reads `{{variables}}` from `.testmuai/variables/*.json`, and that directory is
gitignored. `scripts/test_data.py provision` builds `.testmuai/variables/ci.json` from
three sources:

- `test-data/openemr-portal.json`: expected values from the PRD, such as patient names,
  medications and providers
- `patient1_*` / `patient2_*` logins, taken from secrets when set and otherwise the public
  demo accounts, with passwords marked `secret: true` so kane-cli masks them
- `invalid_username` / `invalid_password` / `invalid_email` for failed-login tests,
  randomly generated on every run so they never match a real account
- `start_url`, taken from `APP_URL`

The one difference from the reference repo is that this runs in the **assurance job too,
before design**. kane-cli 0.8.12+ reuses a variable name that already exists in a pool file
and does not invent a new one. As a result, the designed tests use `patient1_username`
and similar names instead of names nothing supplies. For any name design does invent,
`scripts/test_data.py stubs` emits a warning. The evidence job's preflight
(`test_data.py check`) then stops on it before a browser starts.

The names in `test-data/openemr-portal.json` are a first guess. As the reference repo did
after its first run, reconcile them against the first real `design tests` output.

### Constraints of a shared public demo

These shape the workflow. They are also recorded in the PRD (BR-005, BR-014, Appendix A):

- **One session per account.** A second sign-in with the same patient ends the first
  session. The suite therefore always runs with `--parallel 1`, and workflow concurrency is
  one run at a time repo-wide, not per branch.
- **The demo resets daily at about 08:00 UTC**, and other visitors change data during the
  day. The schedule runs at 09:30 UTC. Tests must create what they need inside their own
  session and must not assume that data created by others exists.
- **Do not change the shared accounts' credentials.** If a designed test actually changes a
  password, not just the mismatch-error check, every later test fails, and so does every
  other visitor to the demo until the next reset. Review designed tests for
  **Manage Login Credentials** before the first run.
- **Tests that write data** (messages, appointments, profile changes, forms) put
  clearly labelled "automated assurance check" data into a public system. That data
  disappears at the next reset.

## The three stages

### 1 · Assurance: requirements to designed tests

```bash
kane-cli context ingest requirements/*.md --mode ci
kane-cli context extract --mode ci
kane-cli context review --approve <ids> --mode agent
kane-cli design tests --use-case uc-... --mode ci --max 8
kane-cli context fsck
```

- `--mode ci` tells kane-cli never to ask questions. The agent assumes documented defaults
  instead of waiting for an answer.
- Exit code 3 means the run paused and can be resumed with
  `kane-cli context extract --resume <sid> --message "..."`. `scripts/assurance.sh` reports
  it as a warning, not a failure.
- The graph and the designed tests are cached between runs (`.context/`, `.kane-state/`).
  Unchanged requirements are not re-extracted and not billed again.

For a governed setup, set `AUTO_APPROVE` to `false`. A person then runs
`kane-cli context review` locally and commits `.context/`.

### 2 · Evidence: one execution, one sealed pack

```bash
kane-cli testrun run .testmuai/tests/*_test.md --dry-run
kane-cli testrun run .testmuai/tests/*_test.md \
  --name "OpenEMR portal regression #42" --parallel 1 --on-failure continue --headless
kane-cli evidence validate .testmuai/evidence/<id>.evidence --profile L1 --json
```

Before any browser starts, the job checks that the demo portal is reachable, so a demo
outage or reset fails fast and clearly. The pack is uploaded with 90-day retention. It is
also published to the TestMu AI Test Manager, and the job summary links to it.

### 3 · Coverage: designed × proven

```bash
kane-cli cover --from <pack> gaps --rollup strict --json
```

Coverage has two axes:

- **Completeness:** was a test designed for every acceptance criterion?
- **Depth:** did a test actually run and pass, according to the evidence pack?

The gate fails the build when proven coverage falls below `COVERAGE_THRESHOLD` (default
80%) and posts the ribbon as a PR comment.

## Running it locally first

```bash
npm install -g @testmuai/kane-cli@0.8.13
kane-cli login --oauth
kane-cli config set-url https://demo.openemr.io/openemr/portal

python scripts/test_data.py provision

kane-cli context ingest requirements/openemr-patient-portal-prd.md
kane-cli context list --type usecase
kane-cli design tests --use-case <uc-id>
kane-cli testrun run .testmuai/tests/*_test.md --parallel 1
kane-cli cover --from <pack> gaps
```

Don't run the suite locally while CI is running. Both sign in as the same demo patients and
would log each other out.

## Keeping it true as requirements change

```bash
kane-cli maintain reconcile      # every proposed change HOLDS as a review card
kane-cli maintain evolve <ref>   # re-design the affected use-case; untouched items preserved
```

## Pointing it at your own OpenEMR

1. Set `APP_URL` to your instance's `/portal` URL.
2. Put your test patients' credentials in the `OPENEMR_PORTAL_*` secrets.
3. Update PRD sections 26–27 and `test-data/openemr-portal.json` with those patients' data.
4. With a private instance, you can split tests by patient and raise `--parallel`.

## Note on versions

CI installs the kane-cli version pinned in `.github/actions/setup-kane/action.yml`
(`0.8.13`; 0.8.12+ is needed for design to reuse pooled variable names). The reference repo
verified the command surface on 0.8.10/0.8.11. Run `kane-cli changelog` before bumping the
pin.
