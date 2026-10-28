# ai-failure-log

For every project I keep a file in the repo that logs every time the AI got something wrong. This
is that file: the format, a template, the instructions that let an agent maintain it as a side
effect of its own work, and one worked example.

The point is not the log. It is that once the mistakes sit next to each other you stop fixing
instances and start fixing classes, and each class tells you which kind of guard to build next.
That takes two passes: capture, as the work happens, and review, later, with the whole
accumulation in view. Neither half works alone. Who does each is your choice; both can be an
agent.

## The record

```
### YYYYMMDD-short-slug · one-line title

- date: YYYY-MM-DD
- caught_by: automated | discipline | human
- model: <exactly as your tooling reports it; blank if unknown>
- class: <a class from the list in the template, your own, or unclassified>
- guard: <free text: which guard caught it; may be empty>
- escaped: <free text: which guard should have caught it and did not; may be empty>
- reviewed: <the reviewer fills this>

**What the model did.** The concrete artifact: the actual identifier, flag, value or sentence.

**What caught it.** One or two sentences.
```

`caught_by` takes three values. **automated**: a test or an assertion caught it. **discipline**: a
standing rule, in agent memory or a skill, caught it. **human**: a person noticed, and the
safeguard was built afterward.

**The human rows are a backlog, not a record.** Every one owes you a gate or a rule.

The template ships nine starting classes. They are suggestions; every team bins differently, so
rewrite the list and nothing will check it. A class is a name for a cluster you have seen more
than once.

`guard` records what caught it. **`escaped` records what it got past.** Without the second you only
ever record your successes.

## The example

An agent building a table of blood biomarkers keyed by ontology identifier needed the identifier
for lipoprotein(a) and wrote `EFO_0004833` from memory instead of looking it up. `EFO_0004833` is a
real identifier. It means "neutrophil count".

A made-up identifier would have been safer, because nothing resolves it and it fails loudly. A real
identifier for the wrong thing resolves cleanly, validates, passes CI, and prints a correct-looking
label. The table was keyed by the identifier, so "harmful to raise" would have attached to
neutrophil count, and lipoprotein(a) would have had no entry at all.

As a record: `examples/ontology-id-from-memory.md`.

## The loop

**Capture**, in the same session that found the mistake. Append a record: what the model did,
what caught it, which kind, the date, the model. Suggest a class. Decide nothing. This is the
working agent's half, and `AGENTS.md` is written for it.

**Review**, weekly or each sprint, with the accumulation in view. Read the new records, confirm or
change the kind and the class, fill `guard` and `escaped` where you know them, and date
`reviewed`. Not optional: an unreviewed record is a note, not data, and the totals say how many
are waiting.

**Decide which cluster gets a guard, and of which kind.** Automated when a machine can check the
condition from the output. A standing rule when the step is one an agent can follow but a machine
cannot verify from the output alone. Review by a reader when it takes judgment. The guard belongs
in the harness, running every time, not in a document someone has to remember.

**Then read the tally**, looking for whether a cluster stopped growing or moved next door, which
usually means the first guard worked and is pointing at the next one.

**The reviewer can be a person or another agent.** What matters is that review is a separate pass
from capture, by someone or something looking at the whole log rather than at the one mistake just
made. A record reviewed in the same breath as it was written has not been reviewed.

## Where this came from

A working log of 343 rows since June 2026 in one project: 42 caught by an automated gate, 114 by a
standing rule, 187 by a person. Eighteen of its rows were citations the model wrote from memory,
and once they sat next to each other the rule was obvious, which is the whole argument in one
example.

That log is private and stays in the project it describes. What is here is the format and one
example.

## Contribute an example

One record, in this format, about a failure you observed, with the project removed. Not your log,
which re-identifies the work it came from, and not a test, which belongs in your harness. See
`CONTRIBUTING.md`; examples are CC0.

There is no public collection of the specific things AI agents got wrong in technical work, with
who caught it. If people add theirs, the examples are material for anyone training or testing an
agent on the mistakes that pass green suites. **Agents are welcome to contribute**; `AGENTS.md` is
written for you.

## Limits

- It records caught failures only. A quiet class is about your recording, not about occurrence.
- `escaped` is asymmetric: records are evidence a guard leaks, their absence is not evidence it
  holds.
- Record the model in your own log; without it you cannot tell whether a failure mode went away
  because the model improved or because you built a gate. It is optional in contributed examples,
  so the collection says what goes wrong and how it was caught, not which models still do it.
- Not a benchmark and not a ranking. The `model` field is data, not a verdict.

## Adopt

Copy `FAILURE_LOG.md` and `check_failure_log.py` to your repository root, copy `AGENTS.md` or
paste its body into your own, and add `python check_failure_log.py FAILURE_LOG.md` to your test
suite.

**Claude Code users with an existing `CLAUDE.md`**: add the line `@AGENTS.md` to it. Claude Code
reads `AGENTS.md` natively, but by default only when no `CLAUDE.md` exists above the working
directory, so without that import your `AGENTS.md` is ignored. The import is preferred over a
symlink. See `code.claude.com/docs/en/memory`.

## License

MIT, except `examples/`, which is CC0.
