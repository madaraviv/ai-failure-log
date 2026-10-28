# Contributing

## An example

Send **one record, in the log's format, about a failure you observed, with the project removed.**
It lives at `examples/<slug>.md`.

Not your log: the story in a log re-identifies the work it came from. Not a test: that belongs in
your harness. One record, the way the LinkedIn post this repository accompanies asks for it: one
specific thing, and who caught it instead.

The floor:

- The record format, every key present. `caught_by` is one of the three values. `model` if your
  tooling reports it, blank otherwise, never guessed.
- **What the model did** names the concrete artifact: the identifier, flag, value or sentence,
  with the task in one neutral sentence naming the kind of work and never whose. "Got a citation
  wrong" is not an example; the citation it wrote is.
- **What caught it** says what exposed it, and where you know it, why it passed unnoticed until
  then.
- The two paragraphs together under 150 words. No names, handles, hostnames, paths, tickets, customer or project names, or
  identifiers from restricted data. If the artifact alone would identify your programme,
  generalize it or do not send it. Dates to the month if you prefer.
- It really happened. `python check_failure_log.py examples/<slug>.md --scrub-check` is clean. A
  second person on your side read it.

Checklist for the pull request:

- [ ] The format checks clean and the scrub check is clean.
- [ ] The task sentence names the kind of work, not whose.
- [ ] Nothing confidential, and a second reader confirmed it.
- [ ] It really happened; it is not constructed to illustrate a point.
- [ ] I agree to the terms below. If I contribute for an employer, they have agreed.

**What you agree to.** Your contribution is licensed under this repository's MIT license, so
anyone may copy it, change it, combine it with others, and use it for any purpose, including
training and evaluating AI systems. You confirm you have the right to share it, that it contains
nothing confidential and no one's personal data, and that it describes something that really
happened. Once merged this cannot be undone; we will remove a file if you ask, but copies and git
history persist.

## A class

A class you have seen more than once: a one-line addition to the list in `FAILURE_LOG.md`, plus
one example carrying it. That is how the list grows. When several examples share a class nobody
named, it gets added as another suggestion.

## A correction

Any claim here, with the measurement behind it.

## Not wanted

A fourth `caught_by` value. A new required field. Anything about building guards; that is your
harness and your business.
