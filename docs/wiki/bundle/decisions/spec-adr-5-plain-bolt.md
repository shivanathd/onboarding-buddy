---
type: Decision
title: "ADR-5: plain Bolt over an agent framework"
description: Three dependencies and one function for the model, so every file is readable in one sitting.
source: ["spec DECISIONS.md ADR-5", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, dependencies, architecture]
---
# ADR-5: plain Bolt over an agent framework

**Context.** Agent kits exist and would have supplied a lot of this. The audience was a large,
beginner heavy room taking the repository home.

**Decision.** Slack Bolt, a scheduler, and the model SDK. Nothing else. The model lives behind
one function.

**Consequences.** Every file is readable in one sitting, and the manifest and the scope list
teach the boundary story directly rather than through an abstraction. The model file is the
smallest in the repository, which is itself the lesson: the room expects the model to be the big
part, and it is not. The body is the product.

**Alternatives rejected.** Agent frameworks: dependency weight, and abstraction sitting exactly
over the seams the exercise is trying to show.

See [the module map](../worker/the-module-map.md).
