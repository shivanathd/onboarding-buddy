---
okf_version: "0.3"
---
# Session 5 · Connect the fleet — Agentforce, Salesforce and Slack

How the Session 5 demo was built, configured and rehearsed: a staffing deal for four
consultants moving from proposal to closed, with an Agentforce agent and a hand-written Python
worker handing work to each other inside a single Slack channel.

An Open Knowledge Format bundle. One concept per file; provenance in each file's frontmatter.

## Start here

- **Building a deck?** [The cast](cast/cast-of-players.md), then [the five acts](demo/the-five-acts.md).
- **Presenting?** [Preflight](demo/preflight.md), [the five acts](demo/the-five-acts.md), [the closer](demo/the-closer.md).
- **Reproducing the setup?** [Setup](setup/index.md), in order.
- **Something broke?** [Gotchas](gotchas/index.md), ordered by demo risk.
- **Need a slide?** [Screenshots](screenshots/index.md) — 14 captures of real state.

## Sections

- [cast](cast/index.md) — who is who on every surface, including who Polly actually is
- [architecture](architecture/index.md) — the three pairings, and how the two bots interact
- [setup](setup/index.md) — how it was configured, in the order it has to happen
- [demo](demo/index.md) — the five acts, preflight, the closer, reset
- [gotchas](gotchas/index.md) — everything that cost real time
- [screenshots](screenshots/index.md) — captured 2026-08-31 from live systems

## The one-paragraph version

Slack can bind a channel to a Salesforce record, giving you editable record tabs with no code —
gated by a per-object switch that cannot be scripted. An Agentforce agent can be installed into
that Slack org as a bot user and will answer from real fields under **the asking user's**
permissions, drafting rather than writing when the action demands confirmation. It can hand work
to another bot by posting a real channel message, because its conversational reply is private to
the asker. But a bot cannot hand work back: an Agentforce session is bound to the invoking
user's Salesforce identity, and a bot has none. So two agents can do the work and still need a
human to close the deal. That last sentence is the demo.
