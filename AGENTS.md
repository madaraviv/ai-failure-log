# Keeping the failure log

This repository keeps a log of what AI agents got wrong, at `FAILURE_LOG.md`. These are the
operative instructions for maintaining it. The reasoning is in `README.md`; the shape
vocabulary is in `SHAPES.md`.

## When to add a record

Add one whenever an AI-produced mistake is found, **including a near miss caught before it
shipped**. Near misses matter because nothing went wrong, so nothing prompts a postmortem, and
the class recurs.

Add it in the same session that found the mistake. A record written later loses the detail that
makes the class recognizable.

## The record

Append to the end of `FAILURE_LOG.md`:

```
### YYYYMMDD-short-slug · A short title

- date: YYYY-MM-DD
- caught_by: automated | discipline | human
- guard: <guard id from the Guards table, or none-yet>
- escaped: <guard ids that already existed and should have caught this; may be empty>
- shape: <a shape from the Shapes table, or unclassified>
- model: <the model that produced the failure, exactly as the tooling reports it; blank if unknown>

**Failure.** What the model did. Name the concrete artifact: the actual flag, identifier, value
or sentence. "Got a citation wrong" is not a record; the identifier it wrote is.

**Caught.** What caught it, and what safeguard was added in response.
```

Then run `python check_failure_log.py FAILURE_LOG.md --write`.

## Field rules

- **`caught_by` takes exactly one of three values**, with nothing else in the cell.
  `automated` means a test or assertion caught it with no human in the loop. `discipline` means
  a standing rule caught it. `human` means a person noticed; whether a safeguard followed is
  recorded in `guard`, which is `none-yet` until one does. Do not write `human (added a test)`;
  name the safeguard in `guard`. Once this cell holds free text it stops being countable, which
  is the one thing it is for.
- **`guard`** is what caught it, or `none-yet` when nothing did. A `human` record with
  `none-yet` is a backlog item: it most likely owes this repository a guard or a rule. Some are
  instead a deliberate decision to accept the risk; write that decision into the **Caught.**
  paragraph rather than leaving it implicit, so a reader can tell an accepted risk from an
  unfinished one.
- **`escaped`** is what the failure got past, and the key is always present even when the value
  is empty, because a blank you can see is different from a field nobody filled in. `guard`
  records successes; without `escaped` the log can never show that a guard leaks. Note the
  asymmetry: `escaped` records are evidence a guard leaks, while no `escaped` records are not
  evidence it holds.
- **`model`** is recorded exactly as the tooling reports it. Never guess it. A blank field is
  correct when the tooling does not report it; an invented value is worse than a blank one.
- **`shape`** must appear in the Shapes table of `FAILURE_LOG.md` or be `unclassified`. When two
  shapes both seem to fit, `SHAPES.md` has the tie-break rules; do not invent a combined shape.
- **Ids are permanent.** `YYYYMMDD-short-slug`, unique forever, never renumbered, because other
  text cites them.

## Guards

A guard added in response to a record gets a row in the Guards table with the date it landed.
That date is what makes "before this guard" and "after this guard" computable.

**A guard that does not run is not a guard.** Put it in the test harness so it runs every time,
not in a document someone has to remember. A guard that cannot be always-on, because it needs
the network, a credential or another operating system, is either changed so it can be, by
recording a fixture, or scheduled with its cadence stated in the `runs` column. A guard that is
neither always-on nor scheduled will report zero failures forever, which reads exactly like
success.

## Reading the log

Periodically: group the records by shape, and build the guard the largest group asks for.
Expect the vocabulary itself to need revision, because the work changes and new shapes appear
that the old values never anticipated. One shape holding most of the records is the signal to
split it, and also a warning, because a class that looks like it stopped may only have stopped
being labeled.

Failures moving to a neighboring shape after a guard lands is the loop working: the guard held,
and it is pointing at the next one.
