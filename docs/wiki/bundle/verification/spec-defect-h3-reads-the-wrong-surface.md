---
type: Concept
title: "Spec defect: the H3 assertion reads the wrong surface"
description: A holdout scenario asserts a reply appears in channel history while the requirement says reply in a thread, and a threaded reply is invisible to that read.
source: ["BUILD_DECISIONS.md spec defect H3 (private build log)", "spec evals/holdout/h3_brain_dark.sh", "spec REQUIREMENTS.md ANS-1", "spec SCENARIOS.md H3"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [spec-defect, evals, contradiction]
---
# Spec defect: the H3 assertion reads the wrong surface

The scenario sets an invalid model key, mentions the worker, then asserts that a specific
template phrase appears in the channel history.

The requirement it is validating says the answer must be posted as a threaded reply. Channel
history returns top level messages only. So a compliant answer is invisible to that assertion,
and the two clauses cannot both be satisfied. The scenario is not testing the worker; it is
testing a contradiction between two parts of its own spec.

## The behaviour itself works

The thing the scenario exists to prove was observed directly by hand: with an invalid key, the
worker replies in the thread with the template line followed by the raw List state, logs the
model failure in one human sentence, and stays alive. Only the assertion's vantage point is
wrong.

## Two ways to fix it, both the spec owner's call

- **Read the thread rather than the channel.** A one line change to the scenario, and it changes
  nothing about the product.
- **Post the answer so it appears in both places.** A one flag change to the worker, and it
  changes the product: every answer would also land in the channel.

The build reported it rather than choosing, because weakening a check you are being measured
against is not the implementer's decision to make. The same discipline produced
[ADR-B2](../decisions/build-adr-b2-dotted-lists-adapter.md), where an adapter was written rather
than the check relaxed.

The general shape is worth recognising: when a scenario cannot pass, check whether it contradicts
a requirement before you change the code. See also
[the H4 defect](spec-defect-h4-needs-channel-membership.md), which is the same class of error
about a different surface.
