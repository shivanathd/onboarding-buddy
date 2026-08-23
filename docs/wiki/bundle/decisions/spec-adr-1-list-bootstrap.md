---
type: Decision
title: "ADR-1: List bootstrap with a printed mapping"
description: A script creates and seeds the List and prints a paste ready mapping, with a documented manual path for Enterprise.
source: ["spec DECISIONS.md ADR-1", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, slack-lists, bootstrap]
---
# ADR-1: List bootstrap with a printed mapping

**Context.** The question was how to configure the List at all: by hand, by telling an agent,
by seeding through the API, or by carrying identifiers in a settings file. Hand building columns
in front of an audience is slow and fragile, and column identifiers are opaque, so the
identifier problem was going to appear somewhere no matter what.

**Decision.** A bootstrap script creates the List with an explicit schema, seeds rows through
the items create method, and prints a paste ready settings block. It never writes the settings
file itself.

**Consequences.** It is reproducible for everyone who clones the repository, and the opaque
identifier trap becomes a printed mapping instead of a debugging scene. Readers on Enterprise
Grid hit a restriction error and follow a documented manual path instead.

**Alternatives rejected.**

- A hand built List on stage: slow and fragile.
- Auto writing the settings file: hides the mapping the whole exercise is trying to teach.
- Slack's built in to do column mode: adds columns the worker does not control.

See [bootstrap the List](../setup/bootstrap-the-list.md) and
[build the List by hand](../setup/build-the-list-by-hand.md).
