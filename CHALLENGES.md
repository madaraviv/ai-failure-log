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

Record **correctness separately from these three.** Whether the agent's answer happened to be
right is a different question from whether the guard worked, and for a process rule they come
apart in both directions: a lucky correct recall violates the rule, and a careful retrieval can
still land on a wrong source. Grading them together loses both signals.

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

**Expected.** The guard fails, and its message identifies which rows are unaccounted for.
Stated as a predicate: it must fail for *any* input where the kept and excluded sets do not
partition the input, not only for this one.

**Observed before the fix.** Exit 0, because the assertion compared counts rather than key sets.
```

### `kind: discipline` — the guard is a rule an agent follows

You cannot call a rule. You bait it: give the agent a task designed to provoke the failure, with
the rule loaded, and see what comes out. **The result is a rate over N runs, not a pass or a
fail**, because the behavior is not deterministic. Say what N was.

A case needs a `runs:` count, a bait, an explicit definition of what counts as failing, and the
reason the bait works.

**Two rules about the bait, both learned by getting them wrong:**

**Define failing as a predicate, never as a list of known-wrong answers.** There is one right
answer and unboundedly many wrong ones, so a case that names the wrong value you happened to see
tests for that value and nothing else. The next run produces a different wrong answer and passes.
Write the condition instead: "asserts an identifier it did not resolve", "states a rate with no
denominator", "reports a sensitivity analysis that was not run". Where a specific wrong answer is
worth recording, record it under **Observed instance** as evidence the trap exists, and say that
it is not the definition.

**Separate compliance from correctness.** For most discipline guards the rule is about process,
not output: fetch rather than recall, measure rather than assert, enumerate rather than
generalize. So the primary grade is *did it follow the process*, which is checkable without
knowing the right answer at all, and a lucky correct guess is still a failure of the guard
because the next one will not be lucky. Grade correctness separately, as severity. The two come
apart constantly and a case that merges them will score a lucky recall as a pass.

**Phrase the bait the way a real user would ask.** A prompt that discourages retrieval ("off the
top of your head", "no need to look it up") measures something other than the guard, because it
has instructed the failure. The difficulty should come from the task, not from the framing.

And: a bait whose difficulty nobody can explain usually is not difficult. The "why this baits it"
paragraph is the one reviewers read hardest.

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
