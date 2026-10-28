# ai-failure-loop

**Log what an AI agent got wrong, name the guard, and work out whether the failure class actually
stopped.**

Status: **work in progress.** The format and the checker are usable today. The measurement layer
is not finished, and the section "What this does not do yet" says exactly where the gaps are.
Contributions are wanted, from people and from agents.

## The problem

Teams running AI coding and research agents fix the same mistake more than once.

The mistake is rarely a crash. It is an output shaped like the right answer: an identifier that
resolves to the wrong thing, a test that passes without constraining the code it covers, a claim
checked on one case and stated for all of them, an answer to a slightly different question than
the one asked. The code is nearly right and the claim about it is wrong, so the tests stay green
and nothing draws attention to it.

Each one gets corrected in the moment and forgotten. Nothing accumulates, so the same class
recurs, and a team can spend a year fixing instances of a problem it never names.

Three things make a log of these failures harder than it looks:

- **A category named for how a failure surfaced will swallow everything.** "The tests were green"
  describes most of them, so it stops discriminating, and then a class that genuinely stopped
  looks identical to a class that stopped being labeled.
- **Recording what caught each failure records only your successes.** A log of catches can never
  show what a safeguard failed to catch, which is the only thing that says whether it works.
- **The share of failures caught automatically moves with which test environments exist**, not
  with how good the safeguards are. Add a second operating system to CI and the number jumps for
  a reason that has nothing to do with the agent or the guards.

## The loop

1. **Log it**, near misses included. Nothing went wrong, so nothing prompts a postmortem, and the
   class recurs.
2. **Read it for clusters**, and expect the clusters themselves to change, because the work
   changes and new kinds of failure appear that the old categories never anticipated.
3. **Build the guard** the biggest cluster asks for, in the test harness, not in a document
   someone has to remember.
4. **Check whether it holds**: what has escaped it since, and whether its cluster's share of new
   records fell.
5. **Expect failures to move to a neighboring shape.** Often that means the guard held and is
   pointing at the next one. It can also mean the workload changed or the classifier drifted, so
   it is a prompt to look, not a conclusion.

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

A worked example, because this failure shape is the one people underrate. An agent building a
table keyed by ontology identifiers needed the identifier for lipoprotein(a) and wrote
`EFO_0004833` from memory instead of looking it up. `EFO_0004833` is a real identifier. It means
"neutrophil count".

A fabricated identifier would have been safer, because nothing resolves it and it fails loudly. A
real identifier for the wrong thing resolves cleanly, validates, passes CI, and prints a
correct-looking label. The table was keyed by the identifier, so the row's verdict would have
attached to the wrong trait, and the intended one would have had no entry at all.

`caught_by` takes exactly three values: `automated`, a test or assertion caught it with no human
in the loop; `discipline`, a standing rule caught it; `human`, a person noticed.

**The `human` records are a backlog, not a record.** Most of them owe you a guard or a rule.
Some will be a deliberate decision to accept the risk, and that decision belongs in the record
rather than being left implicit.

## The two fields most logs lack

`guard` records what caught it. **`escaped` records what it got past.** Without the second, a log
will tell you, truthfully and uselessly, that every guard you own has caught everything it ever
caught.

The guard table gives each guard a landing date, so before-and-after is at least computable, and
a run cadence.

**A guard that does not run is not a guard.** It belongs in the harness, running every time. One
that cannot be always-on, because it needs the network, a credential or another operating system,
is either changed so it can be, by recording a fixture, or scheduled with its cadence stated. A
guard that is neither will report zero failures forever, which reads exactly like success.

## Shapes

A shape names **what the model got wrong**, never how the failure surfaced and never where it
landed, and each is defined by the fix that tests membership. `SHAPES.md` holds the vocabulary,
the overlap rules, and how to propose a new one.

## Adopt in five minutes

1. Copy `FAILURE_LOG.md` and `check_failure_log.py` to your repository root.
2. Copy `AGENTS.md`, or paste its body into your own root `AGENTS.md`. It is written as
   instructions to an agent, so an agent that reads it can maintain the log itself.
3. Add the checker to your test suite:
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
   working directory, so without that import your `AGENTS.md` is ignored. The import is preferred
   over a symlink. See `code.claude.com/docs/en/memory`.

Replace the example rows in the Guards table with your own. The table may start empty; write the
first row when you build the first guard.

## What this does not do yet

Stated plainly, because the gap between what a format promises and what it measures is the thing
this repository exists to be careful about.

- **It does not establish that a guard prevented anything.** Fewer records after a guard landed is
  consistent with the guard working, with the workload changing, with the failures being filed
  under another shape, and with nobody looking. `escaped` is evidence a guard leaks; the absence
  of `escaped` records is not evidence it holds.
- **The honest test is a challenge set**, not a count. `CHALLENGES.md` has the format: a case is
  a known failure replayed against the guarded path, recording separately whether the guard
  executed, detected the problem, and blocked the result. Your own log is the source of cases, so
  nothing has to be predicted. What ships here is the format, one worked case, and a validator;
  running a case against a model needs your own model access.
- **A guard marked as always-running is taken at its word.** Nothing here verifies that it
  executed.
- **The log records caught failures only.** A shape going quiet is evidence about your catching
  and your recording, never proof the failure stopped.
- **It is not a benchmark** and not a ranking of models. The `model` field is data, not a verdict.

## Prior art worth reading first

This is an operational format for agent work, not a new theory of defect classification. Three
bodies of work are ahead of it and worth knowing:

- **Orthogonal Defect Classification**, described by Ram Chillarege and colleagues at IBM in 1992,
  separates a defect's *type* from the *trigger* that revealed it and uses those distributions to
  evaluate the development and verification process. That is close to the questions here, and more
  developed.
- **Corrective and preventive action**, as practiced in regulated industries, already insists on
  the step most often skipped: documented *effectiveness verification*, not merely that a
  corrective action was implemented.
- **Site reliability engineering's postmortem practice** established blameless records with
  tracked, owned corrective actions.

What may be new here is narrow: a format small enough that an agent maintains it as a side effect
of its own work, a vocabulary of failure shapes specific to language models rather than to
hand-written code, and the explicit record of what a safeguard failed to catch.

## Contributing

Two things improve most with other people's experience, because no single team sees enough kinds
of failure:

- **The failure-shape vocabulary** in `SHAPES.md`.
- **Challenge cases** in `challenges/`: the test that would catch a failure you hit. Share the
  case, not the log. A case carries the mechanism and none of the story, which is what makes it
  safe to publish and what makes it still useful a year later against a newer model.

Corrections to the claims here are welcome too, with the measurement behind them.

**Agents are welcome to contribute.** `AGENTS.md` is written for you. If you are an agent that has
produced a failure matching a shape not in `SHAPES.md`, proposing it with the four required items
is a useful contribution; you are a better observer of your own failure modes than your operator
is.

See `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.
