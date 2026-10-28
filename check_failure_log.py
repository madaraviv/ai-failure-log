#!/usr/bin/env python3
"""Check a failure log, and regenerate its totals.

    python check_failure_log.py FAILURE_LOG.md           # check only; exit 1 on a problem
    python check_failure_log.py FAILURE_LOG.md --write   # rewrite the totals block, then check
    python check_failure_log.py FAILURE_LOG.md --scrub-check --denylist my-names.txt

Standard library only. Wire the check form into your test suite so a stale total or a
bad value goes red at the same moment as any other failing test.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

CAUGHT_BY = ("automated", "discipline", "human")
KINDS = ("test", "contract", "discipline", "ruling")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RECORD_ID = re.compile(r"^\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
RUNS = re.compile(r"^(always|scheduled: \S.*)$")
# "### <id>" or "### <id> · <title>"
HEADING = re.compile(r"^###\s+(?P<id>[^\s·|]+)\s*(?:·\s*(?P<title>.*\S))?\s*$")
FIELD = re.compile(r"^- (?P<key>[a-z_]+):\s*(?P<value>.*)$")
# a table row whose first cell is an identifier, back-ticked or not
TABLE_ROW = re.compile(r"^\|(?P<cells>.+)\|\s*$")
REQUIRED = ("date", "caught_by", "guard", "shape", "model")
BEGIN, END = "<!-- totals:begin -->", "<!-- totals:end -->"

# --scrub-check. HARD findings exit 1: these have a shape no public log should carry.
HARD = [
    ("an email address", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b")),
    ("an IPv4 address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("an IPv6 address", re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){3,}[0-9a-fA-F]{0,4}\b")),
    ("a cloud resource id", re.compile(r"\b(?:arn:[\w:-]+|s3://\S+|gs://\S+|i-[0-9a-f]{8,}|AKIA[0-9A-Z]{12,})")),
    ("an absolute path with a username", re.compile(r"(?:/Users/|/home/|[A-Z]:\\Users\\)[^\s/\\`)\]]+")),
    ("a credential-shaped string", re.compile(r"\b(?:[0-9a-f]{32,}|[A-Za-z0-9+/]{40,}={0,2})\b")),
]
# SOFT findings print for review and do not fail; they are noisy by design.
SOFT = [
    ("a URL, check the host", re.compile(r"https?://([^\s/`)\]]+)")),
    ("a tracker reference", re.compile(r"(?:(?<=\s)#\d{1,6}\b|\b[A-Z]{2,}-\d{1,6}\b)")),
    ("a name-shaped pair of words", re.compile(r"(?<=[a-z,] )\b[A-Z][a-z]{2,} [A-Z][a-z]{2,}\b")),
]


def scrub_check(text, denylist=()):
    """Return (hard, soft) lists of 'line N: why -- match' strings."""
    hard, soft = [], []
    for n, line in enumerate(text.splitlines(), 1):
        for why, pat in HARD:
            for m in pat.finditer(line):
                hard.append(f"line {n}: {why} -- {m.group(0)[:60]!r}")
        for why, pat in SOFT:
            for m in pat.finditer(line):
                soft.append(f"line {n}: {why} -- {m.group(0)[:60]!r}")
        low = line.lower()
        for term in denylist:
            if term and term.lower() in low:
                hard.append(f"line {n}: on your denylist -- {term!r}")
    return hard, soft


def _cells(line):
    m = TABLE_ROW.match(line)
    if not m:
        return None
    return [c.strip().strip("`").strip() for c in m.group("cells").split("|")]


def parse(text):
    """Return (records, guards, shapes, problems_found_while_parsing)."""
    guards, shapes, records, cur, section = {}, {}, [], None, None
    dupe_guards, dupe_shapes = [], []
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            cur = None
            continue
        if section == "guards":
            c = _cells(line)
            if c and len(c) >= 3 and DATE.match(c[1]):
                if c[0] in guards:
                    dupe_guards.append(c[0])
                guards[c[0]] = {
                    "since": c[1], "kind": c[2],
                    "runs": c[3] if len(c) > 3 else "",
                }
            continue
        if section == "shapes":
            c = _cells(line)
            if c and len(c) >= 2 and c[0] not in ("shape", "---") and not set(c[0]) <= {"-", ":"}:
                if c[0] in shapes:
                    dupe_shapes.append(c[0])
                shapes[c[0]] = c[1]
            continue
        if section != "log":
            continue
        m = HEADING.match(line)
        if m:
            cur = {"id": m.group("id"), "title": m.group("title") or "", "paragraphs": set()}
            records.append(cur)
            continue
        if cur is None:
            continue
        f = FIELD.match(line)
        if f:
            cur[f.group("key")] = f.group("value").strip()
        elif line.startswith("**Failure.**"):
            cur["paragraphs"].add("Failure")
        elif line.startswith("**Caught.**"):
            cur["paragraphs"].add("Caught")
    pre = [f"guard id {g!r} appears twice in the guard table" for g in sorted(set(dupe_guards))]
    pre += [f"shape {s!r} appears twice in the shape table" for s in sorted(set(dupe_shapes))]
    return records, guards, shapes, pre


def totals(records):
    cb, shape, model = Counter(), Counter(), Counter()
    for r in records:
        cb[r.get("caught_by", "(missing)")] += 1
        shape[r.get("shape", "(missing)")] += 1
        model[r.get("model") or "(not recorded)"] += 1
    n = len(records)
    out = [BEGIN, "", f"**{n} record{'' if n == 1 else 's'}.**", ""]
    out += ["| caught by | records | share |", "|---|---|---|"]
    for k in CAUGHT_BY:
        out.append(f"| {k} | {cb[k]} | {100 * cb[k] / n:.0f}% |" if n else f"| {k} | 0 | n/a |")
    for label, counter in (("shape", shape), ("model", model)):
        out += ["", f"| {label} | records |", "|---|---|"]
        for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
            out.append(f"| {k} | {v} |")
    out += ["", END]
    return "\n".join(out)


def check(text):
    """Return a list of problems. Empty means well formed and the totals are current."""
    records, guards, shapes, problems = parse(text)
    if not records:
        return problems + [
            "no records found: expected a '## Log' heading with '### <id>' records under it"
        ]
    if not shapes:
        problems.append(
            "no shape table found: expected a '## Shapes' heading with rows of | shape | the fix |"
        )

    for g, meta in guards.items():
        if meta["kind"] not in KINDS:
            problems.append(f"guard {g!r}: kind is {meta['kind']!r}, not one of {KINDS}")
        if not RUNS.match(meta["runs"]):
            problems.append(
                f"guard {g!r}: runs is {meta['runs']!r}; it must be 'always' or "
                "'scheduled: <cadence>'. A guard that is neither is not a guard"
            )

    seen = Counter(r["id"] for r in records)
    for rid, n in sorted(seen.items()):
        if n > 1:
            problems.append(f"id {rid!r} is used by {n} records; ids are keys and must be unique")

    for r in records:
        rid = r["id"]
        if not RECORD_ID.match(rid):
            problems.append(f"{rid}: id must look like 20260716-short-slug (date, then a slug)")
        for key in REQUIRED:
            if key not in r:
                problems.append(f"{rid}: missing required field {key!r}")
            elif key != "model" and not r[key]:
                problems.append(f"{rid}: field {key!r} is empty")
        for para in ("Failure", "Caught"):
            if para not in r["paragraphs"]:
                problems.append(f"{rid}: missing the **{para}.** paragraph")
        if r.get("date") and not DATE.match(r["date"]):
            problems.append(f"{rid}: date {r['date']!r} is not ISO (YYYY-MM-DD)")
        elif r.get("date") and not rid.startswith(r["date"].replace("-", "")):
            problems.append(f"{rid}: id does not start with its own date ({r['date']})")
        if r.get("caught_by") and r["caught_by"] not in CAUGHT_BY:
            problems.append(
                f"{rid}: caught_by is {r['caught_by']!r}; it must be exactly one of "
                f"{CAUGHT_BY} with nothing else in the cell. Name the safeguard in 'guard'"
            )
        if shapes and r.get("shape") and r["shape"] not in shapes and r["shape"] != "unclassified":
            problems.append(
                f"{rid}: shape {r['shape']!r} is not in this log's shape table. Add it there "
                "with the fix that tests membership, or use 'unclassified'"
            )
        named = [r.get("guard", "")] + [g.strip() for g in r.get("escaped", "").split(",")]
        for g in [g for g in named if g and g != "none-yet"]:
            if g not in guards:
                problems.append(
                    f"{rid}: names guard {g!r}, which is not in the guard table "
                    "(ids there may be plain or in back-ticks)"
                )
            elif r.get("date") and DATE.match(r["date"]) and guards[g]["since"] > r["date"]:
                problems.append(
                    f"{rid}: dated {r['date']} but guard {g!r} only exists from "
                    f"{guards[g]['since']}; a guard cannot catch, or be escaped by, "
                    "a failure that predates it"
                )

    want = totals(records)
    start, end = text.find(BEGIN), text.find(END)
    if start == -1 or end == -1:
        problems.append(f"no totals block: add {BEGIN} and {END} above the log")
    elif text[start:end + len(END)].strip() != want.strip():
        problems.append("the totals block does not match the records; rerun with --write")
    return problems


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path, write = argv[0], "--write" in argv[1:]
    text = open(path, encoding="utf-8").read()

    if "--scrub-check" in argv[1:]:
        deny = []
        if "--denylist" in argv:
            deny = [
                ln.strip() for ln in open(argv[argv.index("--denylist") + 1], encoding="utf-8")
                if ln.strip() and not ln.startswith("#")
            ]
        else:
            print(f"{path}: no --denylist given. Regexes find shapes; only you know the names.")
        hard, soft = scrub_check(text, deny)
        for f in soft:
            print(f"{path}: REVIEW  {f}")
        for f in hard:
            print(f"{path}: REMOVE  {f}")
        print(
            f"{path}: scrub check -- {len(hard)} to remove, {len(soft)} to review.\n"
            f"{path}: This finds strings with a recognizable shape. It cannot tell that a "
            "sentence describes a customer without naming them. Have a second reader, who is "
            "not the author, read every record before you open the pull request."
        )
        if hard:
            return 1
    if write:
        records, _, _, _ = parse(text)
        start, end = text.find(BEGIN), text.find(END)
        if start == -1 or end == -1:
            print(f"{path}: no totals block to write; add the two marker comments first")
            return 1
        text = text[:start] + totals(records) + text[end + len(END):]
        open(path, "w", encoding="utf-8").write(text)
        print(f"{path}: totals rewritten for {len(records)} record(s)")
    problems = check(text)
    for p in problems:
        print(f"{path}: {p}")
    print(f"{path}: {'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
