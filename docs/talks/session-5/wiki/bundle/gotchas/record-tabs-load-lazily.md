---
type: Decision
title: The record tabs are Slack Lists that render empty until you click sync
description: "Field History and Contact Roles both showed a header and no rows for 20-30 seconds, until the sync icon was clicked. Act 3's payoff depends on knowing this."
source: ["Opportunity Field History tab on <your record channel> empty then 2 rows after Sync list 2026-08-31", "Contact Roles tab empty then 2 rows after sync", "tooltip 'Sync list / Just synced from Asymbl'"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, salesforce, lists, sync, demo-risk]
---
# The record tabs load lazily and need a sync

The most demo-dangerous thing found, because it looks exactly like the integration being
broken.

## What happens

Open **Opportunity Field History** fresh. You get a title, *"related to Meridian Systems -
Platform Expansion FY27"*, a filter chip — and **no rows at all**. It stays that way.

Click the sync icon (top right; tooltip *"Sync list · Just synced from Asymbl"*) and two rows
appear:

```
Aug 31, 2026  Stage  Shivanath…  Negotiation/Review   -> Proposal/Price Quote
Aug 31, 2026  Stage  Shivanath…  Proposal/Price Quote -> Negotiation/Review
```

**Contact Roles behaved identically** — empty, then after a sync and roughly 20 seconds, Anita
Rao and David Mensah with their editable Role dropdowns and Primary checkbox.

Salesforce had the data the whole time; both were verified by SOQL minutes earlier.

## Why it matters

Act 3's entire payoff is *"watch the stage change appear in the audit trail"*. Switch to that
tab expecting the new row and you will get stale data or an empty pane, live, in front of a
room.

## What to do

- **Pre-warm every tab during T-30** — open each one, click sync, confirm rows.
- **Click sync again after the write** in Act 3. Do not assume the tab is live.
- Budget the wait. It is tens of seconds, not instant.

## The underlying model

These tabs are **Slack Lists backed by Salesforce**, not embedded Salesforce pages. That
explains the `Edit view` control, the `Field is any of 1 value` filter chip, the lock icons on
column headers, and the manual sync. It also explains why the Field History filter is
**per Slack account** rather than a Salesforce setting.

Related: [Salesforce and Slack](../architecture/salesforce-and-slack.md),
[preflight](../demo/preflight.md).
