---
type: Process
title: Bootstrap the List
description: One script creates the six column List, seeds a starter cohort, and prints a paste ready column mapping instead of hiding it.
source: ["README.md 15 minute quickstart step 4", "bootstrap.py", "spec DECISIONS.md ADR-1", "spec REQUIREMENTS.md BOOT-1 to BOOT-4", "git log 0df1a00"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, slack-lists, bootstrap]
---
# Bootstrap the List

About three minutes.

```bash
python bootstrap.py
```

That creates a List with six columns, seeds a starter cohort of twelve generic rows, and prints
seven lines. Paste them over the matching lines in the settings file, then start the worker.

The printed block looks like this, with real values in place of the zeros:

```
LIST_ID=F0000000000
COL_STEP=Col0000000000
COL_HIRE=Col0000000000
COL_OWNER=Col0000000000
COL_DUE=Col0000000000
COL_STATUS=Col0000000000
COL_THREAD=Col0000000000
```

## Why it prints instead of writing

Column ids are opaque and there is no way to guess them. The script deliberately does not write
the settings file for you, because the mapping is the thing worth learning: it is the moment a
reader understands that a List column is addressed by an id, not by its name. See
[ADR-1](../decisions/spec-adr-1-list-bootstrap.md).

No second call is needed to learn those ids. The create response already carries the generated
column ids under its metadata, so the script prints a complete mapping straight from the
response it already has.

## Who the seed assigns

Two optional settings decide who fills the New hire and Owner columns, each a comma separated
list of user ids: `SEED_HIRES` and `SEED_OWNERS`. Leave both empty and everything lands on the
manager, which on a one person workspace is the right answer; the script says so rather than
leaving it looking broken, and reports how many distinct people ended up in each column.

One piece of advice worth following if you do have colleagues: keep `SEED_OWNERS` as yourself
while you are testing. The worker tags owners, and with the compressed clock it will tag them
every minute. See [DEMO_MODE compresses the clock](../worker/demo-mode-compresses-the-clock.md).

## Preflight, reruns and null cells

Before it creates anything, the script checks that a bot token is present, that a manager id is
set, and that the token actually authenticates. Failing halfway through seeding leaves a
half built List, so these are caught first, and the successful case prints the workspace and
identity it connected as.

Run it a second time with `LIST_ID` already filled in and it refuses, in one line, without
calling Slack. That refusal is deliberate: it is also what makes an unset check meaningful in
the live evals.

The seed intentionally includes one row with no owner and one row with no due date, so the
null contracts have something to prove. Both print a warning line naming the row, and neither
is an error: an unowned row routes to the manager, and a row with no due date is skipped by
Chase and counted under "no due date" in the report.

## If it fails

Two different reasons, and the script names which one it thinks it hit rather than printing a
bare error code.

On an Enterprise Grid organisation the call cannot create a List at all and returns a
restriction error. On a free or trial workspace, Lists may not be on the plan, which surfaces as
one of several less obvious refusals. That distinction matters because the instinct on a
permission shaped error is to add scopes, and a plan limit cannot be fixed with scopes. The test
is whether you can create a List by hand in the Slack interface: if that is not even offered,
the ceiling is the plan.

Either way the manual path is next; see [build the List by hand](build-the-list-by-hand.md).

The shapes this script gets right, which the documentation does not describe, are worth reading
before you change it:
[a select column needs three fields per choice](../gotchas/select-column-needs-value-label-and-colour.md)
and [clearing a text cell](../gotchas/clearing-a-text-cell.md).
