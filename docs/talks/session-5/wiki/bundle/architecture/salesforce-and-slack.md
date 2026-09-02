---
type: Concept
title: Salesforce and Slack — the record channel, and the switch nobody finds
description: "How an Opportunity comes to live inside a Slack channel with editable tabs, the per-object Setup switch that gates it, and the fact that those tabs are Slack Lists that sync on demand."
source: ["#Meridian Systems - Platform Expansion FY27 tab strip 2026-08-31", "Opportunity Field History and Contact Roles tabs after manual sync", "Setup > Slack > Slack Channels for Records"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [salesforce, slack, channels-for-records, architecture]
---
# Salesforce and Slack

This is the part of the demo with **no code and no agent in it at all**, and it reliably gets
the biggest reaction.

## The channel *is* the record

A Slack channel can be bound to a Salesforce record. When it is, the channel carries a badge
naming the object (**Opportunity**) and gains a tab strip:

| Tab | What it holds |
|---|---|
| **Messages** | the normal channel |
| **Opportunity details** | the live record — stage, close date, owner, *See all 86 fields*, editable in place |
| **Opportunity Field History** | the audit trail, filterable |
| **Contact Roles** | contact + role + primary, with editable dropdowns that write back |
| **Related conversations** | other channels mentioning this record |

Editing in the Slack tab writes to Salesforce. There is no sync job to explain, no middleware,
nothing anybody built.

## The switch nobody finds

> "The thing that took me longest to find is not the integration. It's that the integration is
> off **by default, per object**."

Until you enable it for that specific object, the panel returns a full-page *"Slack isn't
currently set up for Opportunities"*. And there is **no metadata type for the switch** — it is
a click in Setup, or it is nothing. You cannot script it, you cannot deploy it, and you cannot
find it by reading the record page.

Steps: [enable Slack channels for records](../setup/enable-slack-channels-for-records.md).

## The tabs are Slack Lists, and they sync on demand

The one that will bite you live. Those record tabs are **Slack Lists backed by Salesforce**,
and they **render empty until synced**. Opening Field History fresh showed a header, a filter
chip, and no rows at all — for 30 seconds — until the sync icon was clicked
(*"Sync list · Just synced from Asymbl"*). Then two rows appeared.

Act 3's whole payoff is "watch the stage change appear in Field History". If you switch to
that tab expecting the new row, you will get stale data or nothing.

**Pre-warm and sync every tab during T-30, and click sync again after the write.** Details:
[record tabs load lazily](../gotchas/record-tabs-load-lazily.md).

## Field history is immutable, so filter it

`s5demo` carries 18 field-history rows, most of them staging noise — `Amount None → 8,400,000`
five times over, an owner reassignment. You cannot delete field history. The only fix is the
view filter `Field is any of → Stage`, which reduces it to two rows.

That filter is **per Slack account**. Re-apply it on the presenting account and confirm it
before the room arrives.

Related: [the record is the channel](the-record-is-the-channel.md),
[Slack and Agentforce](slack-and-agentforce.md).
