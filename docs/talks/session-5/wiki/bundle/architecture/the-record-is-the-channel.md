---
type: Concept
title: The opportunity channel — anatomy of the one surface the whole demo runs in
description: "What the record channel is made of, what is real versus rendered, and why running all five acts in one channel is a deliberate choice."
source: ["#Meridian Systems - Platform Expansion FY27 <your record channel> 2026-08-31", "Opportunity details tab showing 86 fields, team and related lists"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, salesforce, channel, demo, architecture]
---
# The opportunity channel

Everything happens in `#Meridian Systems - Platform Expansion FY27` (`<your record channel>`). One
surface, five acts, no tab-hopping. That is a deliberate staging choice: the audience never
has to relocate, so every new capability lands in a place they already understand.

## What is in the frame

```
#Meridian Systems - Platform Expansion FY27   [Opportunity]     <- object badge
 Messages | Opportunity details | Related conversations | Add canvas
          | Opportunity Field History | Contact Roles | +
 ...
 sidebar:  Salesforce      -> this channel, grouped under a Salesforce heading
           Agents & apps   -> onboarding-buddy
           Agentforce      -> Polly PeopleOps                   <- separate section
```

Two things worth pointing at that cost nothing:

- Slack groups the record channel under a **Salesforce** heading in the sidebar, and puts
  **Polly under a separate "Agentforce" heading** from ordinary apps. Slack models Agentforce
  agents as their own class of participant.
- The **Opportunity details** tab shows the record's team and its related lists (Cloud Coach
  Projects, Gong Conversations, Service Orders) — real objects from a real org, which sells
  "this is a CRM, not a toy" faster than saying it.

## Real versus rendered

| Looks like | Actually is |
|---|---|
| A Salesforce record page | a Slack List view over the record, editable, writing back live |
| A live audit trail | a Slack List that **syncs on demand** — empty until you click sync |
| A stage progress ribbon | configured for a *different* label set; it will not highlight our stage |

The path ribbon is the one that reliably embarrasses people. It shows *Identify Lead ·
Qualification · Discovery · Demo · Scoping · Proposal Negotiation · Order Form · Closed* and
highlights **Qualification** — while the record's actual stage is `Proposal/Price Quote`,
which is not on the ribbon at all. Point at the **Stage field**, or at Field History.

## Why not a nicer channel name

`#deal-meridian` exists and reads better. The record panel even offers *"Link an existing
channel"*. **Do not** — the long-named channel is the one that is verified end to end: the
buddy is in it, Polly is in it, `CHANNEL_ID` points at it, the Field History filter is set on
it. A nicer name is not worth re-verifying six things two days out.

Related: [Salesforce and Slack](salesforce-and-slack.md),
[record tabs load lazily](../gotchas/record-tabs-load-lazily.md).
