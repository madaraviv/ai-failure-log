# Failure log

Every time the AI got something wrong. Append new records at the end; never edit or renumber an
existing one. Run `python check_failure_log.py FAILURE_LOG.md --write` after appending.

This records **caught** failures only. A class going quiet is evidence about this team's catching
and recording, never proof the failure stopped.

`reviewed` is dated in a later pass, with the whole log in view, by a person or by an agent given
that task. A record reviewed in the same breath as it was written has not been reviewed.

## Classes

Starting suggestions only. Every team bins differently and prioritizes differently; rewrite this
list for your work. Nothing checks it. A class is a name for a cluster you have seen more than
once, and nothing more.

- **recalled fact**: an external fact stated from memory instead of looked up
- **trusted your own record**: a fact about your system read from a document instead of the system
- **overgeneralized**: a measurement narrower than the claim built on it
- **diagnosis before measurement**: a causal story asserted before the measurement that could refute it
- **partial sweep**: a fix applied to the reported instance while a sibling kept the defect
- **green but unconstrained**: a check that passed without constraining what it was read as proving
- **built but unwired**: code present but never reached at runtime, tests green
- **wrong inference from a clean run**: a correct run and a conclusion that does not follow
- **substituted answer**: the output answers a neighboring question, or a subset, without saying so

## Totals

Generated. Run the checker with `--write`.

<!-- totals:begin -->

**1 record.**

| caught by | records | share |
|---|---|---|
| automated | 0 | 0% |
| discipline | 1 | 100% |
| human | 0 | 0% |

| class | records |
|---|---|
| recalled fact | 1 |

| model | records |
|---|---|
| claude-opus-4-8[1m] | 1 |

unreviewed: 0

<!-- totals:end -->

## Log

### 20260716-ontology-id-from-memory · A real identifier for the wrong thing

- date: 2026-07-16
- caught_by: discipline
- model: claude-opus-4-8[1m]
- class: recalled fact
- guard: the standing rule to resolve every external identifier before it lands
- escaped:
- reviewed: 2026-10-28
- context:

**What the model did.** Building a table of blood biomarkers keyed by ontology identifier, it
wrote `EFO_0004833` for lipoprotein(a) from memory instead of looking it up. `EFO_0004833` is a
real identifier; it means "neutrophil count". A made-up identifier would have been safer, because
nothing resolves it and it fails loudly. A real identifier for the wrong thing resolves cleanly,
validates, passes CI, and prints a correct-looking label. The table was keyed by the identifier,
so "harmful to raise" would have attached to neutrophil count, and lipoprotein(a) would have had
no entry at all.

**What caught it.** The standing rule that any external identifier driving a decision is resolved
and its label matched before it lands, not only checked for format. The rule had covered
citations; it now covers every external identifier.
