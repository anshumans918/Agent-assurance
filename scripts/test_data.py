#!/usr/bin/env python3
"""
Test data for the designed OpenEMR patient portal suite.

`kane-cli testrun` has no --variables flag; members read variables from
.testmuai/variables/*.json. That directory is gitignored, so on a runner it is empty
unless this script fills it.

The site under test is the public OpenEMR demo (https://demo.openemr.io/openemr/portal),
not something this repo starts. Two consequences shape this file:

  * Portal login needs three values — Username, Password and E-Mail Address. Each is
    read from its OPENEMR_PORTAL_* environment variable (a repository secret) when set,
    and otherwise falls back to the demo's publicly documented account
    (https://www.open-emr.org/demo/), so the suite runs without any portal secrets. Set
    the secrets to point it at a private OpenEMR. Passwords are written with
    `secret: true` so kane-cli masks them and routes them to the secrets store.
  * Failed-login tests need credentials that match no account. invalid_username,
    invalid_password and invalid_email are generated at random on every provision, so
    they can never collide with a real account or with each other across runs.
  * There is no server to pre-seed. The demo resets around 08:00 UTC every day and is
    shared with the public (PRD BR-014), so tests must set up anything they need inside
    their own session and must not rely on data created by anyone else.

  provision   write test-data/openemr-portal.json + credentials + start_url to
              .testmuai/variables/ci.json
  check       fail before any browser starts if a member uses a {{variable}} that
              nothing supplies — those tests cannot pass on any re-run
  stubs       report the empty stubs kane-cli design declared in
              .testmuai/variables/assurance.json (names this repo does not supply yet)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import secrets
import sys
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path("test-data/openemr-portal.json")
OUT_FILE = Path(".testmuai/variables/ci.json")
STUB_FILE = Path(".testmuai/variables/assurance.json")
VARIABLE_DIRS = (Path.home() / ".testmuai/kaneai/variables", Path(".testmuai/variables"))

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)(?:\.[^}]*)?\s*\}\}")

# kane-cli resolves these namespaces itself; they never need a pool-file value.
RUNTIME_NAMESPACES = {"smart", "environment", "secrets", "totp"}

# variable name -> (environment variable overriding it, public demo default, secret?)
# Patient 1 is Phil Belford (PRD §26), patient 2 is Susan Underwood (PRD §27). The
# defaults are the demo's published portal logins, not private credentials.
CREDENTIALS = {
    "patient1_username": ("OPENEMR_PORTAL_USER", "Phil1", False),
    "patient1_password": ("OPENEMR_PORTAL_PASSWORD", "phil", True),
    "patient1_email": ("OPENEMR_PORTAL_EMAIL", "heya@invalid.email.com", False),
    "patient2_username": ("OPENEMR_PORTAL_USER_2", "Susan2", False),
    "patient2_password": ("OPENEMR_PORTAL_PASSWORD_2", "susan", True),
    "patient2_email": ("OPENEMR_PORTAL_EMAIL_2", "nana@invalid.email.com", False),
    # Role-named accounts kane-cli design asked for (run 6), mapped onto the demo's
    # accounts per PRD §26-27: Susan has no future appointments and (unlike Phil, whom
    # the scheduling and messaging tests write to) nothing that adds to her mailbox;
    # Phil's past appointments exceed the display limit.
    # Each role account has all three login values pooled, so the next design reuses the
    # _email name instead of signing in with only a username and password.
    "empty_mailbox_username": ("OPENEMR_PORTAL_USER_2", "Susan2", False),
    "empty_mailbox_password": ("OPENEMR_PORTAL_PASSWORD_2", "susan", True),
    "empty_mailbox_email": ("OPENEMR_PORTAL_EMAIL_2", "nana@invalid.email.com", False),
    "patient_no_future_appointments_username": ("OPENEMR_PORTAL_USER_2", "Susan2", False),
    "patient_no_future_appointments_password": ("OPENEMR_PORTAL_PASSWORD_2", "susan", True),
    "patient_no_future_appointments_email": ("OPENEMR_PORTAL_EMAIL_2", "nana@invalid.email.com", False),
    "patient_with_many_past_appointments_username": ("OPENEMR_PORTAL_USER", "Phil1", False),
    "patient_with_many_past_appointments_password": ("OPENEMR_PORTAL_PASSWORD", "phil", True),
    "patient_with_many_past_appointments_email": ("OPENEMR_PORTAL_EMAIL", "heya@invalid.email.com", False),
    # The change-credentials tests sign in as patient 1 and fill the new-password
    # fields. Using patient 1's CURRENT password means an accidental save changes
    # nothing — a real change would lock every later test (and the public) out.
    "new_portal_password": ("OPENEMR_PORTAL_PASSWORD", "phil", True),
    # Staff-side recipient check for Secure Messaging: the demo's published admin login.
    "care_team_username": ("OPENEMR_STAFF_USER", "admin", False),
    "care_team_password": ("OPENEMR_STAFF_PASSWORD", "pass", True),
}


def invalid_credentials() -> dict:
    """Fresh random credentials for failed-login tests; they match no account."""
    token = secrets.token_hex(4)
    return {
        "invalid_username": {"value": f"nouser-{token}"},
        "invalid_password": {"value": secrets.token_urlsafe(12), "secret": True},
        "invalid_email": {"value": f"nouser-{token}@example.invalid"},
        # Only ever typed into the confirm field against new_portal_password.
        "different_portal_password": {"value": f"mismatch-{secrets.token_hex(4)}", "secret": True},
    }


def provision() -> int:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    variables = {k: v for k, v in data.items() if not k.startswith("_")}

    defaulted = []
    for name, (env, default, secret) in CREDENTIALS.items():
        value = os.environ.get(env, "")
        if not value:
            value = default
            defaulted.append(env)
        variables[name] = {"value": value, "secret": secret}
    if defaulted:
        print(f"Using the public OpenEMR demo login for: {', '.join(defaulted)} (not set).")

    variables.update(invalid_credentials())

    if os.environ.get("APP_URL"):
        variables["start_url"] = {"value": os.environ["APP_URL"]}

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(variables, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(variables)} variables to {OUT_FILE}: {', '.join(sorted(variables))}")
    return 0


def supplied_keys() -> set[str]:
    """Names with a real value in any pool file. An empty design stub does not count."""
    keys: set[str] = set()
    for directory in VARIABLE_DIRS:
        for path in sorted(glob.glob(str(directory / "*.json"))):
            try:
                doc = json.loads(Path(path).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"::warning::Could not read {path}: {exc}")
                continue
            for key, entry in doc.items():
                if key.startswith("_"):
                    continue
                value = entry.get("value") if isinstance(entry, dict) else entry
                if value not in (None, ""):
                    keys.add(key)
    return keys


def frontmatter_keys(text: str) -> set[str]:
    """Keys under a root `variables:` block in the test's own frontmatter."""
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return set()
    keys, inside = set(), False
    for line in match.group(1).splitlines():
        if re.match(r"variables:\s*$", line):
            inside = True
        elif inside and (m := re.match(r"  ([A-Za-z_][A-Za-z0-9_]*):", line)):
            keys.add(m.group(1))
        elif inside and line and not line.startswith(" "):
            inside = False
    return keys


def stored_in_run(text: str) -> set[str]:
    """Names the test itself establishes as it runs via explicit "store X as name" /
    "note ... as name" phrasing. `baseline_*` names get no free pass: the reference
    healthcare demo found kane-cli leaves an uncaptured baseline unresolved."""
    return set(re.findall(r"\b(?:as|note)\s+['\"`]?([A-Za-z_][A-Za-z0-9_]*)", text))


def missing_emails(used: set[str]) -> list[str]:
    """`<prefix>_username` names used without their `<prefix>_email`. Portal login needs
    all three values (PRD BR-002); run 6 designed sign-ins with only a username and
    password for role-named accounts, which cannot reach the Dashboard."""
    gaps = []
    for name in sorted(used):
        if name.endswith("_username"):
            email = name[: -len("_username")] + "_email"
            if email in CREDENTIALS and email not in used:
                gaps.append(f"{name} without {email}")
    return gaps


def check(members_file: str, runnable_out: str | None = None) -> int:
    members = [line.strip() for line in Path(members_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    supplied = supplied_keys()
    missing: dict[str, list[str]] = defaultdict(list)
    blocked: set[str] = set()

    for member in members:
        text = Path(member).read_text(encoding="utf-8").replace("\r\n", "\n")
        used = set(PLACEHOLDER.findall(text))
        known = supplied | frontmatter_keys(text) | stored_in_run(text) | RUNTIME_NAMESPACES
        for name in sorted(used - known):
            missing[name].append(member)
            blocked.add(member)
        for gap in missing_emails(used):
            print(f"::warning title=Sign-in without email::{Path(member).name} signs in with {gap}; "
                  "portal login needs Username, Password and E-Mail Address, so this test is likely to fail.")

    runnable = [m for m in members if m not in blocked]
    if runnable_out:
        Path(runnable_out).write_text("".join(f"{m}\n" for m in runnable), encoding="utf-8")

    if not missing:
        print(f"Test data OK: every variable used by {len(members)} member(s) is supplied.")
        return 0

    for name, tests in sorted(missing.items()):
        where = "scripts/test_data.py" if name in CREDENTIALS or name.startswith("invalid_") else str(DATA_FILE)
        level = "warning" if runnable_out else "error"
        print(f"::{level} title=Missing test data::{{{{{name}}}}} is used by {len(tests)} test(s) "
              f"but nothing supplies it — add \"{name}\" to {where}.")
        for test in tests:
            print(f"    {test}")

    # With --runnable-out, one unsupplied variable no longer stops the whole suite
    # (run 6 lost all 58 tests to 13 names): only the tests that use it are left out,
    # and their acceptance criteria show up as not run in the coverage ribbon.
    if runnable_out and runnable:
        print(f"{len(missing)} variable(s) unsupplied; leaving out {len(blocked)} test(s), "
              f"running the other {len(runnable)}.")
        return 0
    print(f"{len(missing)} variable(s) unsupplied; stopping before any browser minute is spent.")
    return 1


def stubs() -> int:
    if not STUB_FILE.exists():
        print("kane-cli declared no new variables.")
        return 0
    doc = json.loads(STUB_FILE.read_text(encoding="utf-8"))
    supplied = supplied_keys()
    empty = sorted(k for k in doc if not k.startswith("_") and k not in supplied)
    if not empty:
        print(f"Every variable declared in {STUB_FILE} is supplied.")
        return 0
    for name in empty:
        entry = doc[name] if isinstance(doc[name], dict) else {}
        print(f"::warning title=Variable needs a value::{name} — {entry.get('description', 'no description')}. "
              f"Add it to {DATA_FILE}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("provision")
    sub.add_parser("stubs")
    check_parser = sub.add_parser("check")
    check_parser.add_argument("members", help="file listing one *_test.md path per line")
    check_parser.add_argument("--runnable-out", help="write the members whose variables are all supplied "
                              "here and succeed if there is at least one, instead of failing on any gap")
    args = parser.parse_args()
    if args.command == "provision":
        return provision()
    if args.command == "stubs":
        return stubs()
    return check(args.members, args.runnable_out)


if __name__ == "__main__":
    sys.exit(main())
