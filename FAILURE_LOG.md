# Failure log

What the AI got wrong, what caught it, and which guard it got past.
Append new records at the end of this file. Never edit or renumber an existing record; fill
blank fields only. Run `python check_failure_log.py FAILURE_LOG.md --write` after appending.

This log records **caught** failures only. A shape going quiet is evidence about this team's
catching and recording. It is never proof the failure stopped happening. The `automated` share
also moves when test environments are added or removed, so do not compare it across periods
without naming the environments that existed in each.

## Guards

Both rows below are examples. Replace them with your own; the table may start empty.
`runs` must be `always` or `scheduled: <cadence>`. A guard that is neither is not a guard.

| guard | since | kind | runs | where it lives | shapes it targets |
|---|---|---|---|---|---|
| `fetch-verify-identifier` | 2026-01-01 | discipline | always | agent instructions | recalled-fact |
| `second-os-in-ci` | 2026-01-01 | test | always | CI matrix | built-but-unwired |

## Shapes

The vocabulary this log validates against. A shape names **what the model got wrong**, never
how the failure surfaced and never where it landed. Each one is defined by the fix that tests
membership. Add, remove or rename rows to suit your work; `unclassified` is always allowed.

| shape | the fix that tests membership |
|---|---|
| recalled-fact | Fetch it instead of stating it from memory |
| trusted-our-own-record | Re-measure it instead of reading a prior document |
| overgeneralized | Name the population and the n |
| diagnosis-before-measurement | Measure before explaining |
| partial-sweep | Enumerate the class, fix every member |
| green-but-unconstrained | Make the test fail first |
| built-but-unwired | Run the real path end to end |
| substituted-answer | Say the substitution in the answer |

## Totals

Generated. Do not edit by hand; run the checker with `--write`.

<!-- totals:begin -->

**1 record.**

| caught by | records | share |
|---|---|---|
| automated | 0 | 0% |
| discipline | 1 | 100% |
| human | 0 | 0% |

| shape | records |
|---|---|
| recalled-fact | 1 |

| model | records |
|---|---|
| claude-opus-4-8[1m] | 1 |

<!-- totals:end -->

## Log

### 20260716-ontology-id-from-memory · A real identifier for the wrong thing

- date: 2026-07-16
- caught_by: discipline
- guard: fetch-verify-identifier
- escaped:
- shape: recalled-fact
- model: claude-opus-4-8[1m]

**Failure.** Building a table keyed by ontology identifiers, the model wrote the identifier for
lipoprotein(a) from memory as `EFO_0004833` instead of looking it up. `EFO_0004833` is a real
identifier; it means "neutrophil count". A fabricated identifier would have failed loudly,
because nothing resolves it. A real identifier for the wrong thing resolves cleanly, validates,
passes CI, and prints a correct-looking label. The table was keyed by the identifier, so the
row's verdict would have attached to neutrophil count, and lipoprotein(a) would have had no
entry at all.

**Caught.** The standing rule that any external identifier driving a decision is resolved and
its label matched before it lands, rather than only checked for format. The rule had covered
citations; it now covers every external identifier.
