# Keeping the failure log

This repository keeps a log of what the AI got wrong, at `FAILURE_LOG.md`.

## When to add a record

Whenever an AI-produced mistake is found, **including a near miss caught before it shipped**.
Nothing went wrong, so nothing prompts a postmortem, and the class recurs.

Log it even when a recalled value turned out to be right. The failure is the step that was
skipped, not the luck of the result.

Add it in the same session that found the mistake. Later loses the detail that makes the class
recognizable.

## The record

Append to the end of `FAILURE_LOG.md`:

```
### YYYYMMDD-short-slug · one-line title

- date: YYYY-MM-DD
- caught_by: automated | discipline | human
- model: <exactly as your tooling reports it; blank if unknown>
- class: <a class from the list above, your own, or unclassified>
- guard: <free text: which guard caught it; may be empty>
- escaped: <free text: which guard should have caught it and did not; may be empty>
- reviewed: <blank; the reviewer fills this>

**What the model did.** The concrete artifact: the actual identifier, flag, value or sentence.
"Got a citation wrong" is not a record; the identifier it wrote is.

**What caught it.** One or two sentences.
```

Then run `python check_failure_log.py FAILURE_LOG.md --write`.

## Field rules

- **`caught_by` is exactly one of three values**, with nothing else in the cell. `automated`: a
  test or an assertion caught it. `discipline`: a standing rule, in agent memory or a skill,
  caught it. `human`: a person noticed, and the safeguard was built afterward. Do not write
  `human (added a test)`; that goes in `guard`. Once this cell carries free text nothing can be
  counted, which is the one thing it is for.
- **`model`** exactly as the tooling reports it. Never guess it. Blank is correct when the tooling
  does not report it; an invented value is worse than a blank one.
- **`guard` and `escaped`** are phrases, never validated. A record saying a failure got past a
  guard is evidence that guard leaks. The absence of such records is not evidence it holds; it is
  more often evidence nobody wrote them.
- **Ids are permanent.** `YYYYMMDD-short-slug`, unique forever, never renumbered.

## Capturing is not reviewing

While you are capturing, you do not fill `reviewed`, change another record's class, or decide what
gets a guard. Those belong to the review pass, which happens later with the whole log in view.
Your job here is to record accurately and decide nothing.

You may be asked to do the review pass as a separate task, and that is a legitimate use of an
agent. If so, read every unreviewed record together rather than one at a time, and say what you
changed. A record reviewed in the same breath as it was written has not been reviewed.
