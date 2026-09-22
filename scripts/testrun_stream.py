#!/usr/bin/env python3
"""
Read a `kane-cli testrun run` NDJSON stream.

When members have never been authored, testrun authors each one as its own run
(testrun_authored_member_* events) and seals no suite execution: testrun_done carries
an empty execution_id. Run 7 fed the last authored member's pack to coverage and
reported 118 of 146 ACs "blocked". The workflow therefore runs the suite a second time
after an authoring pass, and always locates the suite pack by execution id.

  execution-id <ndjson>   print the sealed suite execution id (empty after authoring only)
  authored <ndjson>       print how many members this stream authored
  failed <ndjson>         print the path of every executed member that did not pass
"""

from __future__ import annotations

import json
import sys


def events(path: str):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("{"):
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def execution_id(path: str) -> str:
    found = ""
    for event in events(path):
        if event.get("type") == "testrun_done":
            found = event.get("execution_id") or ""
        elif event.get("type") == "testrun_summary" and not found:
            found = ((event.get("execution") or {}).get("id")) or ""
    return found


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("execution-id", "authored", "failed"):
        print(__doc__)
        return 2
    command, path = sys.argv[1], sys.argv[2]
    if command == "execution-id":
        print(execution_id(path))
    elif command == "authored":
        print(sum(1 for e in events(path) if e.get("type") == "testrun_authored_member_end"))
    else:
        # Both shapes count: a replay emits testrun_member_end, while a first run that
        # authors its members emits testrun_authored_member_end and can still seal a
        # suite execution (run 11 did, and its 38 failures went unretried because only
        # the replay shape was read here).
        seen = set()
        for event in events(path):
            if event.get("type") in ("testrun_member_end", "testrun_authored_member_end") \
                    and event.get("status") != "passed" and event["path"] not in seen:
                seen.add(event["path"])
                print(event["path"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
