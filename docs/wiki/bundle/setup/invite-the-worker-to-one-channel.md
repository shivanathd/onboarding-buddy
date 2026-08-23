---
type: Process
title: Invite the worker to one channel
description: The worker knows exactly one channel, and Slack sends no mention event at all in a channel the app has not joined.
source: ["README.md 15 minute quickstart step 2", "spec EVIDENCE.md E6", "spec REQUIREMENTS.md ANS-4"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, channels, events]
---
# Invite the worker to one channel

About one minute. Create or pick a channel, then invite the bot to it.

The worker knows one channel and only one. Its id goes into the settings file as `CHANNEL_ID`,
and a mention arriving from anywhere else gets a one line redirect with no model call.

## Membership is not a nicety

Slack's own documentation is explicit: if your app is mentioned but is not part of the
conversation and has not been invited to join, you do not receive an event. Not a filtered
event, not an event you can choose to ignore. No event at all.

That has two consequences worth carrying:

- A worker that looks completely dead in a channel is usually just not a member of it.
- A test that expects a redirect from a channel the bot has never joined cannot pass, because
  nothing arrives to redirect. That is exactly the shape of one of the
  [spec defects found](../verification/spec-defect-h4-needs-channel-membership.md): the wrong
  channel in that scenario has to be a second channel the bot is a member of.

Direct messages are also out of scope. The mention event is documented never to fire in a
direct message conversation; that would need a different event subscription, which this worker
does not have.
