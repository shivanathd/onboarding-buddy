---
type: Concept
title: Events are load balanced, not duplicated
description: An app may hold several socket connections and Slack sends each event to exactly one of them, so two running copies each get a random half.
source: ["docs/how-this-was-built.md", "README.md one worker on shift", "spec EVIDENCE.md E7"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [socket-mode, operations, events]
---
# Events are load balanced, not duplicated

An app may hold up to ten concurrent socket connections, and when several are open Slack sends
each payload to any one of them. Not to all of them. To one.

This is the single most important operational fact about running this kind of worker, because
the failure mode is so much worse than the one people expect. Two copies of a worker do not
both act, which would be annoying and obvious. They each receive a random half of the events,
so the worker answers some mentions and ignores others, ticks some rows and misses others, and
does it differently every time you test it.

Hence one rule, stated in the README and in the boot log: **one worker on shift at a time.**
Stop the local worker before starting the hosted one.

In the recorded deploy this was handled by stopping the laptop worker once the hosted service
had boot log parity, so exactly one connection held the shift.

The reason this constraint exists at all is the transport choice. Socket Mode buys no public
URL, no request signing and no ingress, at the cost of this rule; see
[ADR-6](../decisions/spec-adr-6-socket-mode.md) and
[first run, then the hosted shift](../setup/first-run-then-the-hosted-shift.md).
