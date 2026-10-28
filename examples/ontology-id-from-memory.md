### 20260716-ontology-id-from-memory · A real identifier for the wrong thing

- date: 2026-07-16
- caught_by: discipline
- model: claude-opus-4-8[1m]
- class: recalled fact
- guard: the standing rule to resolve every external identifier before it lands
- escaped:
- reviewed: 2026-07-16

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
