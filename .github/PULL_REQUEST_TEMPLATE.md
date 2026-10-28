<!-- Delete the section that does not apply. -->

## A shape, a correction, or a checker test

What this changes. For a new shape, the four items from SHAPES.md plus the
"not to be confused with" line, and the evidence of recurrence.

## A challenge case under challenges/

- [ ] `python run_challenges.py challenges/` passes.
- [ ] The case names one guard and one shape and sits under `challenges/<guard-id>/`.
- [ ] A `discipline` case states `runs:` of at least two.
- [ ] The "why this baits it" paragraph explains the mechanism, rather than asserting the case is
      hard.
- [ ] Nothing confidential: no names, hostnames, customer or project names, ticket references,
      paths with usernames, or identifiers from restricted-access data. I ran
      `python check_failure_log.py <file> --scrub-check` as a backstop and read it myself for the
      detail a pattern match cannot see.
- [ ] It describes a failure I actually observed; it is not invented.
- [ ] I agree to the CC0 terms under "What you agree to by sharing a case" in CONTRIBUTING.md. If
      I contribute for an employer, they have agreed.
