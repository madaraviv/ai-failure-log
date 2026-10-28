# ai-failure-loop

**Log what your AI agent got wrong, build the guard, measure whether the failure class actually
stopped.**

Teams that work with AI coding and research agents fix the same mistake more than once. The
mistake is rarely a crash. It is an output shaped like the right answer: an identifier that
resolves to the wrong thing, a test that passes without constraining the code it covers, a claim
checked on one case and stated for all of them. Each gets corrected in the moment and forgotten.
This repository is a small, opinionated loop for turning those corrections into guards: log what
the AI got wrong and what caught it, read the log for clusters, build the guard the biggest
cluster asks for into your test harness, and measure whether the cluster stopped. We kept such a
log for four months, 343 records, before anyone asked whether the guards it had produced actually
worked. The log could not answer. This is the version that can.

## The loop

1. **Log it**, near misses included.
2. **Read it for clusters**, and expect the clusters themselves to change, because the work changes.
3. **Build the guard** the biggest cluster asks for, in the harness, not in a document someone
   has to remember.
4. **Measure**: did that cluster's share of new records fall, and what has escaped the new guard?
5. **Expect failures to move to a neighboring shape.** In our experience that is the loop
   working: the first guard held and is pointing at the next one.

## A record

```
### 20260716-ontology-id-from-memory · A real identifier for the wrong thing

- date: 2026-07-16
- caught_by: discipline
- guard: fetch-verify-identifier
- escaped:
- shape: recalled-fact
- model: claude-opus-4-8[1m]
```

The model needed the ontology identifier for lipoprotein(a) and wrote `EFO_0004833` from memory
instead of looking it up. `EFO_0004833` is a real identifier. It means "neutrophil count". A
fabricated identifier would have failed loudly, because nothing resolves it. A real identifier
for the wrong thing resolves cleanly, validates, passes CI, and prints a correct-looking label.

`caught_by` takes exactly three values: `automated`, a test or assertion caught it with no human
in the loop; `discipline`, a standing rule caught it; `human`, a person noticed and a safeguard
was added afterward.

**The `human` column is a backlog, not a record.** Every entry in it owes you a guard or a rule.

## The two fields most logs lack

`guard` records what caught it. **`escaped` records what it got past.** Without the second, a log
will tell you, truthfully and uselessly, that every guard you own has caught everything it ever
caught. A guard table with a `since` date is what makes before-and-after computable.

**A guard that does not run is not a guard.** It belongs in the harness, running every time. One
that cannot be always-on is either changed so it can be or scheduled with its cadence stated. A
guard that is neither will report zero failures forever, which reads exactly like success.

## What we learned the hard way

Each of these is a design rule here, and each is our own history rather than a claim about anyone
else. The numbers we stand behind: **343 records since June 2026; 42 caught by an automated gate,
114 by a standing rule, 187 by a person.**

- **We ran four columns for four months.** No `guard`, no `escaped`. When the question finally
  came, the log held no record of what any guard had failed to catch.
- **One catch-all held 73% of records**, so a category going quiet was indistinguishable from a
  category that had stopped being used. Ours was named for how failures surfaced rather than for
  what the model got wrong, which is why almost everything fit it. That is the rule in
  `SHAPES.md`.
- **Hand-kept totals were stale at six recounts between August and October**, every time under a
  note at the top of the file warning that they would be. The totals here are generated and a
  test fails when they drift.
- **The `automated` share moved when a test runner came and went**, not when the guards improved.
  Our largest single day of automated catches was the day the suite first ran on a second
  operating system.

## Adopt in five minutes

1. Copy `FAILURE_LOG.md` and `check_failure_log.py` to your repository root.
2. Paste the body of `AGENTS.md` into your own root `AGENTS.md`, or copy the file.
3. Add the checker to your test suite. As a CI step:
   ```
   python check_failure_log.py FAILURE_LOG.md
   ```
   Or as a test:
   ```python
   def test_failure_log_is_well_formed():
       import check_failure_log
       assert check_failure_log.check(open("FAILURE_LOG.md").read()) == []
   ```
4. **Claude Code users with an existing `CLAUDE.md`**: add the line `@AGENTS.md` to it. Claude
   Code reads `AGENTS.md` natively, but by default only when no `CLAUDE.md` exists above the
   working directory, so without that import line your `AGENTS.md` is ignored. The import is
   preferred over a symlink. See `code.claude.com/docs/en/memory`.

Replace the two example rows in the Guards table with your own. The table may start empty; write
the first row when you build the first guard.

## What this is not

- **Not proof that a failure stopped.** The log records caught failures only. A shape going quiet
  is evidence about your catching and your recording.
- **Not a benchmark**, and not a ranking of models. The `model` field is data, not a verdict.
- **Not tied to any vendor or tool.** It is a Markdown file and one standard-library script.

## Contributing

The shape vocabulary is the part that improves with other people's experience, because no single
team sees enough kinds of failure. You can also share your own log. See `CONTRIBUTING.md`.

## Where this came from

Extracted from the working log of a biotech research co-pilot project. **The log those numbers
come from is private and stays in the project it describes. What is published here is the method,
the template, and one worked example.**

Which parts are proven: `date`, `caught_by`, `model` and the two paragraphs have carried 343
records over four months in the log this was extracted from. `guard`, `escaped` and `shape` were
added in October 2026, after that log could not answer whether its own guards worked. They are
the repair for a measured gap, not yet a proven practice.
