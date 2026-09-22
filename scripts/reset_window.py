#!/usr/bin/env python3
"""
Keep suite executions clear of the public OpenEMR demo's daily reset.

The demo at demo.openemr.io resets around 08:00 UTC and answers 502 Bad Gateway for
roughly twenty minutes (run 4 lost 11 tests between 08:03 and 08:19 UTC). Members run
one at a time at about SECONDS_PER_TEST each, so a suite's duration is predictable
enough to plan around the window.

  wait <members>     sleep until the window has passed if running <members> now would
                     overlap it, unless that wait exceeds MAX_WAIT_MIN (then run anyway)
  clear <members>    exit 0 if <members> can run now without overlapping the window
  failed <ndjson>    print the path of every member that did not pass in a testrun stream
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time

SECONDS_PER_TEST = 160
RESET_START = dt.time(7, 45)
RESET_END = dt.time(8, 30)
MAX_WAIT_MIN = 150


def overlap(now: dt.datetime, members: int) -> dt.datetime | None:
    """The end of the reset window this run would overlap, or None."""
    end = now + dt.timedelta(seconds=members * SECONDS_PER_TEST)
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for d in (day, day + dt.timedelta(days=1)):
        lo = dt.datetime.combine(d.date(), RESET_START, tzinfo=dt.timezone.utc)
        hi = dt.datetime.combine(d.date(), RESET_END, tzinfo=dt.timezone.utc)
        if now < hi and end > lo:
            return hi
    return None


def wait(members: int) -> int:
    now = dt.datetime.now(dt.timezone.utc)
    hi = overlap(now, members)
    duration = dt.timedelta(seconds=members * SECONDS_PER_TEST)
    if hi is None:
        print(f"No overlap with the demo reset (suite ~{duration}, now {now:%H:%M} UTC).")
        return 0
    minutes = (hi - now).total_seconds() / 60
    if minutes > MAX_WAIT_MIN:
        print(f"::warning title=Reset overlap::The suite (~{duration}) overlaps the demo reset, "
              f"but waiting {minutes:.0f} min is too long; running now.")
        return 0
    print(f"The suite (~{duration}) would overlap the demo reset; waiting {minutes:.0f} min until {hi:%H:%M} UTC.")
    sys.stdout.flush()
    time.sleep(max(0.0, (hi - now).total_seconds()))
    return 0


def clear(members: int) -> int:
    return 0 if overlap(dt.datetime.now(dt.timezone.utc), members) is None else 1


def failed(stream: str) -> int:
    for line in open(stream, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        event = json.loads(line)
        if event.get("type") == "testrun_member_end" and event.get("status") != "passed":
            print(event["path"])
    return 0


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("wait", "clear", "failed"):
        print(__doc__)
        return 2
    command, arg = sys.argv[1], sys.argv[2]
    if command == "failed":
        return failed(arg)
    return wait(int(arg)) if command == "wait" else clear(int(arg))


if __name__ == "__main__":
    sys.exit(main())
