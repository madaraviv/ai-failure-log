# Contributing

## What is wanted

- **A new shape**, with the four items in `SHAPES.md`.
- **A better real example** for an existing shape.
- **A constructed-failure test** for a check the checker lacks.
- **A correction** to a claim in the README, with the measurement behind it.
- **A challenge case**: the test that would catch a failure you hit. See below.

## What is not wanted

- A fourth `caught_by` value. Three values are the whole point; a fourth makes the column
  uncountable, which is how ours drifted to 28 distinct values.
- A new required field.
- Renaming a published shape; other people's logs cite it.
- Vendor-specific hooks, a dashboard, or a web interface.

## Sharing a challenge case

**Share the case that would catch your failure, not the log that recorded it.** A case is a
minimal input and an expected behavior; the narrative is removed. See `CHALLENGES.md` for the
format and `challenges/` for a worked example.

This is deliberate, and it is a change from an earlier plan to accept whole logs. A log is written
for colleagues by people who knew the names, and scrubbing it is harder than it looks: a
combination of dates, model versions and project details can identify an unpublished programme
without containing a single name. Aviation and healthcare reporting systems use trained
de-identification for exactly this reason, and generalize or remove contextual identifiers rather
than trusting a pattern match. We are not set up to do that, so we do not ask you to try.

A case avoids the problem by construction. It carries the mechanism and none of the story, and it
is worth more than a log entry anyway, because you can run it again next quarter against a newer
model.

**You do not need to predict anything.** Your own log is the source of cases: every record is a
failure you already observed, so a case is that same request replayed. A case that failed before
your guard landed and still fails afterwards tells you the guard did not hold for it.

### What we accept

- The case validates: `python run_challenges.py challenges/`.
- It names one guard and one shape, and lives under `challenges/<guard-id>/`.
- A `discipline` case has a `runs:` count of at least two, because the behavior is not
  deterministic and one run measures nothing.
- **The "why this baits it" paragraph explains the mechanism.** A bait whose difficulty nobody can
  explain usually is not difficult. This is the field we read hardest.
- Nothing confidential: no names, hostnames, customer or project names, ticket references, paths
  with usernames, or identifiers from restricted-access data. Run
  `python check_failure_log.py <file> --scrub-check` over it as a backstop, remembering that it
  finds shapes and cannot tell that a sentence describes a customer without naming them.
- It describes a real failure you observed. Invented cases are not useful and we cannot verify
  them, so the sign-off asserts it.

### What you agree to by sharing a case

You are placing it in the public domain under CC0. Anyone may copy it, change it, combine it with
others, and use it for any purpose, including training and evaluating AI systems, without asking
you and without crediting you. You confirm you have the right to share it, that it contains
nothing confidential and no one's personal data, and that it describes something that really
happened. Once merged this cannot be undone; we will remove a file if you ask, but copies and git
history will persist. If you are contributing for an employer, confirm they have agreed.

### Reviewing a case

Validate it. Read it for meaning-level detail no pattern match can see. Check that the bait's
mechanism is explained rather than asserted. Confirm the guard and shape exist, or that the pull
request adds them properly.
