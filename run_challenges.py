#!/usr/bin/env python3
"""Validate challenge cases, and print the discipline baits for you to run.

    python run_challenges.py challenges/             # validate every case
    python run_challenges.py challenges/ --prompts   # print the discipline baits
    python run_challenges.py challenges/ --guard G   # only cases for guard G

Standard library only.

This does NOT execute contributed code, deliberately. A repository that runs arbitrary
contributed Python in CI is one pull request away from a much worse problem than a stale
log. Cases are data: you wire a `test`-kind case to your own guard in your own test
suite, and a `discipline`-kind case needs your own model access.
"""
from __future__ import annotations

import pathlib
import re
import sys
from collections import Counter

KINDS = ("test", "discipline")
HEADING = re.compile(r"^###\s+(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\s*$")
FIELD = re.compile(r"^- (?P<key>[a-z_]+):\s*(?P<value>.*)$")
# the labelled paragraphs each kind must carry
NEEDED = {
    "test": ("Input", "Expected"),
    "discipline": ("Bait", "Counts as the failure", "The guard held if", "Why this baits it"),
}


def parse_case(path):
    text = path.read_text(encoding="utf-8")
    case = {"path": path, "paragraphs": set(), "slug": None}
    for line in text.splitlines():
        m = HEADING.match(line)
        if m and case["slug"] is None:
            case["slug"] = m.group("slug")
            continue
        f = FIELD.match(line)
        if f:
            case[f.group("key")] = f.group("value").strip()
            continue
        label = re.match(r"^\*\*(?P<label>[^*]+?)\.?\*\*", line)
        if label:
            case["paragraphs"].add(label.group("label").rstrip("."))
    return case


def validate(case):
    p, problems = case["path"], []
    where = f"{p.parent.name}/{p.name}"
    if not case["slug"]:
        problems.append(f"{where}: no '### case-slug' heading")
    elif case["slug"] != p.stem:
        problems.append(f"{where}: heading {case['slug']!r} does not match the filename {p.stem!r}")

    kind = case.get("kind")
    if kind not in KINDS:
        problems.append(f"{where}: kind is {kind!r}; it must be one of {KINDS}")
    for key in ("guard", "shape"):
        if not case.get(key):
            problems.append(f"{where}: missing required field {key!r}")
    if case.get("guard") and case["guard"] != p.parent.name:
        problems.append(
            f"{where}: guard is {case['guard']!r} but the directory says "
            f"{p.parent.name!r}; a case lives under the guard it challenges"
        )
    if kind == "discipline":
        runs = case.get("runs", "")
        if not runs.isdigit() or int(runs) < 2:
            problems.append(
                f"{where}: a discipline case needs 'runs:' of 2 or more. The behavior is not "
                "deterministic, so one run measures nothing; the result is a rate"
            )
    elif kind == "test" and "runs" in case:
        problems.append(f"{where}: a test case is deterministic; drop 'runs:'")
    for label in NEEDED.get(kind, ()):
        if label not in case["paragraphs"]:
            problems.append(f"{where}: missing the **{label}.** paragraph")
    return problems


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    root = pathlib.Path(argv[0])
    only = argv[argv.index("--guard") + 1] if "--guard" in argv else None
    cases = [parse_case(f) for f in sorted(root.rglob("*.md")) if f.name != "README.md"]
    if only:
        cases = [c for c in cases if c.get("guard") == only]
    if not cases:
        print(f"{root}: no cases found")
        return 0

    problems = [p for c in cases for p in validate(c)]
    for p in problems:
        print(p)

    kinds = Counter(c.get("kind") for c in cases)
    guards = sorted({c.get("guard") for c in cases if c.get("guard")})
    print(
        f"{root}: {len(cases)} case(s) over {len(guards)} guard(s) -- "
        + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()) if k)
        + (f"; {len(problems)} problem(s)" if problems else "; all valid")
    )

    if "--prompts" in argv:
        disc = [c for c in cases if c.get("kind") == "discipline"]
        print(f"\n{len(disc)} discipline case(s) to run yourself. Each needs its own model access.")
        for c in disc:
            print(f"\n{'=' * 70}\n{c['guard']} / {c['slug']}  ({c.get('runs')} runs)\n{'=' * 70}")
            print(c["path"].read_text(encoding="utf-8").strip())
        print(
            "\nRecord executed / detected / blocked per case, and the rate over the runs. "
            "Results belong in your own repository; they describe your system, not this format."
        )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
