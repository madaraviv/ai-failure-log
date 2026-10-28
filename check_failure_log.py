#!/usr/bin/env python3
"""Check a failure log, and regenerate its totals.

    python check_failure_log.py FAILURE_LOG.md            # check; exit 1 on a problem
    python check_failure_log.py FAILURE_LOG.md --write     # regenerate the totals, then check
    python check_failure_log.py examples/x.md --scrub-check # also checks the format

A file with no "## Log" heading, such as a single contributed record, is read as one
record on its own.

Standard library only. Wire the plain form into your test suite.

It checks the two things a log maintained by agents does not keep by convention: a
three-value column that stays three values, and a tally that matches the records.
It does not check your class names. Those are yours.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

CAUGHT_BY = ("automated", "discipline", "human")
KEYS = ("date", "caught_by", "model", "class", "guard", "escaped", "reviewed")
MUST_HAVE_A_VALUE = ("date", "caught_by", "class")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REC_ID = re.compile(r"^\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING = re.compile(r"^###\s+(?P<id>[^\s·|]+)")
FIELD = re.compile(r"^- (?P<key>[a-z_]+):\s*(?P<value>.*)$")
BEGIN, END = "<!-- totals:begin -->", "<!-- totals:end -->"
# things that should not be in a published record. Shapes only; a pattern cannot tell
# that a sentence describes a customer without naming them, so a person still reads it.
LEAKS = [
    ("an email address", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b")),
    ("an IP address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("a cloud resource id", re.compile(r"\b(?:arn:[\w:-]+|s3://\S+|gs://\S+|AKIA[0-9A-Z]{12,})")),
    ("a path with a username", re.compile(r"(?:/Users/|/home/|[A-Z]:\\Users\\)[^\s/\\`)\]]+")),
    ("a credential-shaped string", re.compile(r"\b(?:[0-9a-f]{32,}|[A-Za-z0-9+/]{40,}={0,2})\b")),
]


def parse(text):
    """Records are '### <id>' blocks under '## Log', each with '- key: value' lines."""
    # a file with no "## Log" heading is a bare record, e.g. one contributed example
    records, cur, in_log = [], None, "## Log" not in text
    for line in text.splitlines():
        if line.startswith("## "):
            in_log = line[3:].strip().lower() == "log"
            cur = None
        elif not in_log:
            continue
        elif m := HEADING.match(line):
            cur = {"id": m.group("id"), "paragraphs": set()}
            records.append(cur)
        elif cur is None:
            continue
        elif f := FIELD.match(line):
            cur[f.group("key")] = f.group("value").strip()
        elif m := re.match(r"^\*\*(What the model did|What caught it)\.\*\*", line):
            cur["paragraphs"].add(m.group(1))
    return records


def totals(records):
    n = len(records)
    cb = Counter(r.get("caught_by", "(missing)") for r in records)
    out = [BEGIN, "", f"**{n} record{'' if n == 1 else 's'}.**", ""]
    out += ["| caught by | records | share |", "|---|---|---|"]
    out += [f"| {k} | {cb[k]} | {100 * cb[k] / n:.0f}% |" if n else f"| {k} | 0 | n/a |"
            for k in CAUGHT_BY]
    for label, key in (("class", "class"), ("model", "model")):
        c = Counter(r.get(key) or "(not recorded)" for r in records)
        out += ["", f"| {label} | records |", "|---|---|"]
        out += [f"| {k} | {v} |" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
    out += ["", f"unreviewed: {sum(1 for r in records if not r.get('reviewed'))}", "", END]
    return "\n".join(out)


def check(text):
    """Return a list of problems. Empty means well formed and the tally is current."""
    records, problems = parse(text), []
    if not records:
        return ["no records found: expected '## Log' with '### <id>' records under it"]
    for rid, k in Counter(r["id"] for r in records).items():
        if k > 1:
            problems.append(f"id {rid!r} is used by {k} records; ids are keys, renumber the later one")
    for r in records:
        rid = r["id"]
        if not REC_ID.match(rid):
            problems.append(
                f"{rid}: id must look like 20260716-short-slug. Note that every '###' heading "
                "under '## Log' is read as a record"
            )
        for key in KEYS:
            if key not in r:
                problems.append(f"{rid}: missing the {key!r} line (the value may be blank)")
            elif key in MUST_HAVE_A_VALUE and not r[key]:
                hint = "; write 'unclassified' if you do not know" if key == "class" else ""
                problems.append(f"{rid}: {key!r} is blank and must have a value{hint}")
        for para in ("What the model did", "What caught it"):
            if para not in r["paragraphs"]:
                problems.append(f"{rid}: missing the **{para}.** paragraph")
        for key in ("date", "reviewed"):
            if r.get(key) and not DATE.match(r[key]):
                problems.append(f"{rid}: {key} {r[key]!r} is not ISO (YYYY-MM-DD)")
        if r.get("date") and DATE.match(r["date"]) and not rid.startswith(r["date"].replace("-", "")):
            problems.append(f"{rid}: id does not start with its own date ({r['date']})")
        if r.get("caught_by") and r["caught_by"] not in CAUGHT_BY:
            problems.append(
                f"{rid}: caught_by is {r['caught_by']!r}; it is exactly one of {CAUGHT_BY} with "
                "nothing else in the cell. Put the safeguard in 'guard'"
            )
    if "## Log" not in text:          # a bare record file keeps no tally
        return problems
    want, start, end = totals(records), text.find(BEGIN), text.find(END)
    if start == -1 or end == -1:
        problems.append(f"no totals block: add {BEGIN} and {END}")
    elif text[start:end + len(END)].strip() != want.strip():
        problems.append("the totals do not match the records; rerun with --write")
    return problems


def scrub(text):
    return [f"line {n}: {why} -- {m.group(0)[:60]!r}"
            for n, line in enumerate(text.splitlines(), 1)
            for why, pat in LEAKS for m in pat.finditer(line)]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = argv[0]
    text = open(path, encoding="utf-8").read()
    leaks = scrub(text) if "--scrub-check" in argv else []
    if "--scrub-check" in argv:
        for f in leaks:
            print(f"{path}: REMOVE {f}")
        print(f"{path}: {len(leaks)} to remove. This finds strings with a recognizable shape. It "
              "cannot tell that a sentence describes a customer without naming them, so have "
              "someone else read it too.")
    if "--write" in argv:
        start, end = text.find(BEGIN), text.find(END)
        if start == -1 or end == -1:
            print(f"{path}: no totals block; add the two marker comments first")
            return 1
        text = text[:start] + totals(parse(text)) + text[end + len(END):]
        open(path, "w", encoding="utf-8").write(text)
        print(f"{path}: totals rewritten")
    problems = check(text)
    for p in problems:
        print(f"{path}: {p}")
    print(f"{path}: {'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems or leaks else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
