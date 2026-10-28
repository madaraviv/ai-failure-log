# Contributing

## What is wanted

- **A new shape**, with the four items in `SHAPES.md`.
- **A better real example** for an existing shape.
- **A constructed-failure test** for a check the checker lacks.
- **A correction** to a claim in the README, with the measurement behind it.
- **Your own log**, shared under `shared-logs/`. See below.

## What is not wanted

- A fourth `caught_by` value. Three values are the whole point; a fourth makes the column
  uncountable, which is how ours drifted to 28 distinct values.
- A new required field.
- Renaming a published shape; other people's logs cite it.
- Vendor-specific hooks, a dashboard, or a web interface.

## Sharing your log

You can share your own failure log under `shared-logs/<your-org-or-handle>/FAILURE_LOG.md`, in
the same format as the template, dedicated to the public domain under CC0.

**Why share one.** Nobody has a public collection of AI failures in technical work annotated with
what caught them. If more than one team shares theirs, three things become possible that one team
cannot do alone: a shape vocabulary grounded in several teams' experience rather than one;
base rates, such as whether a person catching more than half of all failures is typical or just
us; and an evaluation set, because a record naming the concrete failing artifact is the seed of a
test asking whether an agent still makes that mistake and whether anything catches it. Guards
that held across teams are candidate rules for anyone's agent instructions. Shapes that recede
across model generations, and shapes that do not, become visible only with the model recorded.
That is the intent and the invitation. Today the folder holds what people have chosen to share,
and we promise nothing about what it will hold.

**Scrub it first, before your first commit on the branch.** The first push is publication; a
later force-push does not unpublish a pull request's history. Your log was written for colleagues,
in the moment, by people who knew the names. Remove:

- people: names, handles, emails, reviewer names, "I asked ...";
- machines and accounts: hostnames, IP addresses, cloud resource ids, bucket and account names,
  absolute paths containing a username, tunnel and VPN names;
- trackers: ticket and issue numbers, internal document or decision ids, internal wiki links;
- business: customers, partners, vendors under contract, unreleased product and project names,
  unpublished numbers, anything under agreement;
- data: identifiers from restricted-access datasets, patient- or sample-level values, credentials.

Keep: the model id, the concrete technical artifact that failed (a flag, an identifier, a
formula), dates, and public documentation links.

Then run:

```
python check_failure_log.py FAILURE_LOG.md --scrub-check --denylist my-names.txt
```

`my-names.txt` is a local file you never commit, listing every person, host, customer and
internal system that appears in your private log. The denylist is the load-bearing half: regexes
find shapes, and only you know the names.

> **The scrub check finds strings with a recognizable shape. It cannot tell that a sentence
> describes a customer's project without naming them. Two people from your side read every
> record before you open the pull request, and the second reader is not the author.**

**What we accept.** At least ten records. Every record names the concrete thing that failed, so
"got a citation wrong" is declined but the identifier it wrote is accepted. Every record names
what caught it, in a form someone else could adopt. `caught_by` is one of the three values.
`shape` comes from your file's own table or is `unclassified`, with `unclassified` at most one
record in four. `model` is filled exactly as your tooling reports it, or blank with a one-line
header note saying your tooling does not report it; a guessed model is worse than a blank one.
Every record is something that really happened. We decline a log that is mostly a verdict on a
vendor; the `model` field is data, not a judgment.

**What you agree to by sharing a log here.** You are placing this file in the public domain under
CC0. Anyone may copy it, change it, combine it with others, and use it for any purpose, including
training and evaluating AI systems, without asking you and without crediting you. You confirm
that you have the right to share it, that it contains nothing confidential and no one's personal
data, and that every record describes something that really happened. Once merged this cannot be
undone; we will remove a file if you ask, but copies and git history will persist. If you are
contributing on behalf of an employer, confirm they have agreed.

## Reviewing a shared log

Run both checks. Read every record for meaning-level leaks the regexes cannot see. Spot-check
three records against the shape definitions. Confirm no pasted third-party text. Confirm the
header carries the license line and the sign-off. Confirm the branch history contains no
unscrubbed version.
