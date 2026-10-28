# Shapes

A shape groups failures by **what the model got wrong**. Each is defined by the fix that tests
membership: if you cannot name a distinct fix, you do not have a shape.

**The structural rule: a shape names what the model got wrong, never how the failure surfaced
and never where it landed.** Our own catch-all was named for how failures surfaced, "the tests
were green", so almost everything fit it and it reached 73% of records. A shape named for the
artifact it landed in ("citation", "fixture") has the same problem from the other direction.

`unclassified` is the only residual, and it is a state, not a shape. A published shape is never
renamed, because other people's logs cite it; a shape found to be two gets a "split into a, b"
note and a one-pull-request relabel.

## The vocabulary

| shape | definition | the fix | not to be confused with |
|---|---|---|---|
| **recalled-fact** | An external fact stated from memory instead of looked up: a citation, an identifier, a flag, a default, a format. | Fetch it. | *trusted-our-own-record*, where the stale fact came from your own document rather than the model's memory. |
| **trusted-our-own-record** | A fact about your own system taken from a prior artifact (a handoff, a spec, a docstring, a manifest) instead of from the system. | Re-measure it. | *recalled-fact*, where nothing was read at all. |
| **overgeneralized** | A real measurement narrower than the claim built on it: one member asserted of the class, a sample presented as the whole. | Name the population and the n. | *diagnosis-before-measurement*, where no measurement was taken. |
| **diagnosis-before-measurement** | A causal story for a symptom asserted before the measurement that could refute it. | Measure before explaining. | *overgeneralized*, where a measurement exists but is too narrow. |
| **partial-sweep** | A correct fix applied to the instance in hand while a sibling, mirror or second copy of the same rule kept the defect. | Enumerate the class and fix every member. | *built-but-unwired*, where the fix reached nothing at all. |
| **green-but-unconstrained** | A test, golden, gate or audit that passed without constraining the behavior it was read as proving. Includes a gate that reports instead of failing, and a fixture authored from the same wrong assumption as the code. | Make it fail first. | *built-but-unwired*, where the code never ran rather than the test never constraining it. |
| **built-but-unwired** | Code present but never reached or never effective at runtime, with the tests green: an unplumbed setting, a dead switch, a guard whose input never arrives. | Run the real path end to end. | *green-but-unconstrained*, where the code ran and the test was blind. |
| **substituted-answer** | The user-facing output states something other than what the system did: narrowed, substituted, or silently withheld. | Say the substitution in the answer. | *overgeneralized*, which is about the breadth of a claim rather than about answering a different question. |

## Proposing a shape

A new shape needs all four, plus the nearest-neighbour line:

1. **A name** that says what the model got wrong.
2. **A one-sentence definition.**
3. **The fix that tests membership**, one imperative sentence. If an existing shape already has
   that fix, it is not a new shape. If the fix is "be more careful" or "test better", there is
   no shape.
4. **One real example**, as a complete record, added to `FAILURE_LOG.md` in the same pull request.

Plus: "not to be confused with *<nearest shape>*, because *<the distinguishing fix>*".

**Evidence of recurrence** is required: at least two records from two contributors, or three from
one. A proposed shape that would absorb more than half the records of any one log is a definition
problem, not a discovery.

**Standing review trigger:** when any one shape exceeds 40% of records across the shared logs,
the maintainers open a discussion about splitting it.
