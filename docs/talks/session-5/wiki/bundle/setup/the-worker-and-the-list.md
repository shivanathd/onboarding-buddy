---
type: Process
title: Mirror the recruiting data into the worker's Slack List
description: "Why the Slack List is mirrored from Salesforce rather than synced back, how the consultant names were added without a re-bootstrap, and the rollup limitation that remains."
source: ["slackLists.items.list on YOUR_LIST_ID 2026-08-31", "seed/onboarding.csv in shivanathd/onboarding-buddy", "get_onboarding_summary reporting '1 new hires'"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, lists, worker, data, setup]
---
# The worker and the List

The worker's memory is a **Slack List**, not a database. 12 rows: four consultants × three
onboarding steps.

## Mirror one way only

Salesforce ⇒ List. Never the reverse. A Slack List belongs to the app that created it, so
nothing else can write it — the direction is forced, not chosen.

## Naming the consultants without a re-bootstrap

The obvious change was to add a `Placement` column and re-bootstrap the List. That was
rejected: a new `LIST_ID` plus six `COL_*` environment variables, the day before a talk, for a
cosmetic gain.

Instead **each step's text was rewritten to name its consultant** — `Sara Okonkwo — Access
badge`. The rename is idempotent (it splits on the separator before re-applying), so running
it twice does not double up.

The payoff is what the audience actually reads:

```
Overdue now
  Sara Okonkwo — Access badge          8 days over
  Rahul Menon — Manager intro call     5 days over
  Priya Raman — Laptop delivery        3 days over
```

Compare the before state, which said only `Access badge, 8 days over` — see the
[screenshots](../screenshots/index.md).

## The limitation that remains

`get_onboarding_summary` still answers **"1 new hires"**, and the report's *By person* section
shows one member with 12 open. The `New hire` column is a Slack **person** column and this
workspace has one human, so twelve rows collapse onto it.

Every line the audience reads names a consultant; only the rollup does not. Say *"one
workspace member, four placements"* and move on. See
[the one-member workspace](../gotchas/one-member-workspace.md).

## Verifying the List state

Check for pollution before a run — extended due dates and stamped thread cells from a previous
rehearsal are what make a chase behave oddly:

```bash
curl -s -H "Authorization: Bearer $BOT_TOKEN" \
  "https://slack.com/api/slackLists.items.list?list_id=$LIST_ID&limit=100"
```

Clean means 12 rows, every `status = open`, **no thread cells**, and the original due dates
(five already overdue, one with no due date).

Related: [onboarding-buddy](../cast/onboarding-buddy.md),
[seed the recruiting data](seed-the-recruiting-data.md).
