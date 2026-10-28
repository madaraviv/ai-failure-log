# Challenges

A log tells you a failure happened. A challenge tells you whether the guard you built for it
still works.

A challenge is **one case that should trip one guard**, plus what the guard is expected to do. It
is data, not a story: a minimal input and an expected behavior, with the narrative removed. That
makes it safe to share, because the narrative is where confidential detail and re-identification
live, and it makes it more useful than a log entry, because it can be run again next quarter
against a newer model.

Cases live in `challenges/<guard-id>/<case-slug>.md`, one case per file.

## Three outcomes, not one

Record them separately, because they fail for different reasons and have different fixes.

| outcome | question | what a failure here means |
|---|---|---|
| **executed** | did the guard run at all? | it is dormant, or its input never arrives. Nothing else it reports is meaningful |
| **detected** | did it notice the problem? | it ran and is blind to the case |
| **blocked** | did it stop the bad result? | it noticed and only warned. A guard that reports instead of failing is not a gate |

A guard can execute, detect, and still not block. That combination is common enough to be worth
its own column.

## The two kinds of case

### `kind: test` — the guard is code

Deterministic. The case states an input that violates the guard's invariant and the behavior
expected of it.

```
### partition-assertion-off-by-one
- guard: partition-assertion
- kind: test
- shape: green-but-unconstrained

**Input.** 100 rows in, 97 kept, 2 recorded as excluded.

**Expected.** The guard fails loudly, naming the missing row.

**Observed before the fix.** Exit 0, because the assertion compared counts rather than key sets.
```

### `kind: discipline` — the guard is a rule an agent follows

You cannot call a rule. You bait it: give the agent a task designed to provoke the failure, with
the rule loaded, and see what comes out. **The result is a rate over N runs, not a pass or a
fail**, because the behavior is not deterministic. Say what N was.

A case needs a `runs:` count, a bait, an explicit definition of what counts as failing, and the
reason the bait works. That last field matters most: a bait whose difficulty nobody can explain
usually is not difficult.

## Running them

```
python run_challenges.py challenges/            # validate every case
python run_challenges.py challenges/ --prompts  # print the discipline baits, to run yourself
```

**The runner does not execute contributed code, by design.** A repository that runs arbitrary
contributed Python in CI is one pull request away from a much worse problem than a stale log.
Contributed cases are data. `test`-kind cases are wired to your own guard by you, in your own
test suite; the case file says what to assert, and you write the assertion. Discipline cases need
your own model access, which is why they are not run in CI either.

## Recording a result

Results belong in your own repository, not here, because they are about your system:

```
| date | guard | case | runs | executed | detected | blocked |
|---|---|---|---|---|---|---|
| 2026-10-28 | fetch-verify-identifier | ontology-id-near-neighbor | 10 | 10 | 7 | 7 |
```

Three of ten slipped through. That is a number you can act on, and it is not derivable from a
failure log no matter how long you keep one.

## What this does not establish

A challenge set measures whether a guard catches **the cases you thought of**. It does not
measure whether the failure class stopped occurring in the wild. Those are different claims and
conflating them is the mistake this whole repository is organized against. New cases come from
new log records, which is why the log and the challenge set need each other.
