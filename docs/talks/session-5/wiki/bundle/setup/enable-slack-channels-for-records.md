---
type: Process
title: Enable Slack channels for a Salesforce object
description: "The per-object switch that turns an ordinary Slack channel into a record surface with editable tabs — and why it cannot be scripted."
source: ["Setup > Slack > Slack Channels for Records in s5demo", "full-page error 'Slack isn't currently set up for Opportunities' 2026-08-30", "#Meridian Systems - Platform Expansion FY27 tab strip"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [salesforce, slack, setup, channels-for-records]
---
# Enable Slack channels for records

The highest reaction-per-effort item in the whole demo. Also the one that is easiest to
believe is broken.

## Prerequisites

- The Salesforce org is connected to the Slack org (Setup → **Slack** → Salesforce for Slack /
  Slack Connect setup).
- The presenting Slack account is mapped to a Salesforce user. In a sandbox, **map manually** —
  automatic mapping matches on email and sandbox emails carry an `.invalid` suffix.

## The switch

Setup → **Slack** → *Slack Channels for Records* → enable for the object you want
(**Opportunity**).

**It is off by default, per object.** With it off, opening the record's Slack panel returns a
full-page *"Slack isn't currently set up for Opportunities"* — which reads like a licensing or
connection failure and is neither.

There is **no metadata type for this switch**. It cannot be deployed, scripted, or captured in
a package. It is a click, or it is nothing. Budget a click, and check it after any org change.

## Then create the channel from the record

Open the Opportunity → the **Slack** button in the record header → create or link a channel.
The channel gains the object badge and the tab strip the first time you post from the record.

## Afterwards, two per-account chores

1. **Filter Field History.** Set the view filter `Field is any of → Stage`. Field history is
   immutable, so filtering is the only way to hide staging noise. **The filter is per Slack
   account** — set it on the account you will present from.
2. **Pre-warm and sync every tab.** They are Slack Lists that render empty until synced. See
   [record tabs load lazily](../gotchas/record-tabs-load-lazily.md).

Related: [Salesforce and Slack](../architecture/salesforce-and-slack.md),
[the opportunity channel](../architecture/the-record-is-the-channel.md).
