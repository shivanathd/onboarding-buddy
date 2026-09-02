---
type: Process
title: Reset the demo to its start state
description: "Everything to put back after a run or a rehearsal, what cannot be put back, and the two things never to do to this org."
source: ["s5-preflight.sh expected start state", "OpportunityFieldHistory query showing 18 immutable rows", "slackLists.items.list clean-state check"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [demo, reset, hygiene, salesforce, slack]
---
# Reset after the demo

## The record

```bash
export SF_AUTOUPDATE_DISABLE=true
cd <pack>    # must be a DX project root for some sf commands

sf data update record --sobject Opportunity \
  --record-id <the opportunity id> \
  --values "StageName='Proposal/Price Quote' CloseDate=2026-09-30" \
  --target-org s5demo --json
```

`--where "Name like '...'"` fails with `Malformed key=value pair for value: Name.` Use
`--record-id`.

## The Job, if Act 5 moved it

```bash
sf data update record --sobject bpats__Job__c \
  --record-id a07cW00001ERtgcQAD \
  --values "bpats__Openings_Filled__c=4" --target-org s5demo --json
```

## The List

Clean means **12 rows, every `status = open`, no thread cells**, original due dates. An
approved escalation extends a due date by three days and stamps a thread cell; a stamped row is
silenced rather than re-nudged, so it will not misfire during a later run — but it will read
wrongly.

```bash
curl -s -H "Authorization: Bearer $BOT_TOKEN" \
  "https://slack.com/api/slackLists.items.list?list_id=$LIST_ID&limit=100"
```

## The channel

Delete the rehearsal messages so the seed message is the last thing in the channel. There is
no bulk delete in Slack — hover → **⋮** → *Delete message*, once per message. Join/leave
notices are system messages and harmless; leave them.

Keep the seed message: *"Deal desk thread for Meridian Systems - Platform Expansion FY27.
Stage is Proposal/Price Quote…"* — it is a deliberate opening state, not clutter.

## What cannot be reset

**Field history is immutable.** `s5demo` carries 18 rows including staging noise. Filtering is
the only fix: `Field is any of → Stage`, **per Slack account**. Re-apply and confirm it every
time.

**Ephemeral messages** vanish on their own and cannot be retrieved — which is also why they
cannot be verified.

## After the talk

- Archive `#agent-handoff-test` (`<a channel id>`).
- Rotate the `mindcatai` signing secret — that old app is still installed in the workspace.
- Rotate the sandbox password.

## Two things never to do

- **Never refresh `s5demo`.** A refresh drops the Slack connection and every staged record.
- **Never uninstall the Slack app from *production*.** It deletes every user mapping.
- And: **do not uninstall Polly.** Her planner bundle carries the grafted Deal Desk topic and
  she is the only Slack-reachable agent. Acts 2 through 4 depend on her.

Related: [preflight](preflight.md), [the five acts](the-five-acts.md).
