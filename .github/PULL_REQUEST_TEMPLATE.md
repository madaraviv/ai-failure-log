<!-- Delete the section that does not apply. -->

## Shape, example, test or correction

What this changes, and for a new shape, the four items from SHAPES.md plus the
"not to be confused with" line.

## Sharing a log under shared-logs/

- [ ] I ran `check_failure_log.py` and `--scrub-check` with a denylist of every person, host,
      customer and internal system in our private log; no hard findings remain.
- [ ] A second reader who is not the author read every record for anything the check cannot see.
- [ ] No unscrubbed version of this file exists in this branch's history.
- [ ] Every record describes something that really happened; none is invented.
- [ ] The file header carries `license: CC0-1.0` and I agree to the terms under "What you agree
      to by sharing a log here" in CONTRIBUTING.md. If I contribute for an employer, they have agreed.
