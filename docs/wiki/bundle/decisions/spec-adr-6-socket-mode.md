---
type: Decision
title: "ADR-6: Socket Mode over HTTP events"
description: The worker dials out, so the same folder runs on a laptop and on a hosted service with no public URL and no request signing.
source: ["spec DECISIONS.md ADR-6", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, socket-mode, deploy]
---
# ADR-6: Socket Mode over HTTP events

**Context.** The repository has to run unchanged on a laptop and on a hosted service.

**Decision.** Socket Mode. No public URL, no request signing, and interactive payloads arrive on
the same connection.

**Consequences.** The hosted service needs no ingress at all, which is most of what makes the
quickstart short. The cost is one operational rule that has to be stated rather than discovered:
one worker on shift, because Slack load balances payloads across connections.

**Alternatives rejected.** HTTP mode: needs a public URL and secret rotation, which would end
the fifteen minute quickstart.

See [the app level token](../setup/the-app-level-token.md) and
[events are load balanced](../gotchas/events-are-load-balanced-not-duplicated.md).
