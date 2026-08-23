---
type: Concept
title: "Spec defect: H4 needs a channel the bot is in"
description: A scenario expects a redirect from a channel the bot was never invited to, but with no membership there is no mention event at all.
source: ["BUILD_DECISIONS.md spec defect H4 (private build log)", "spec evals/holdout/h4_wrong_inputs.sh", "spec EVIDENCE.md E6", ".env.example WRONG_CHANNEL_ID"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [spec-defect, evals, events]
---
# Spec defect: H4 needs a channel the bot is in

The scenario posts a mention in a deliberately wrong channel and expects the worker to reply with
a one line redirect.

The evidence ledger for the same spec already records the reason that cannot work: an app
receives no mention event at all in a channel it has not joined. Not a filtered event. No event.
So a channel the bot has never joined can never produce a redirect, and the scenario would fail
against a perfectly correct worker.

## The fix

The wrong channel has to be a second channel the bot **is** a member of, and which is simply not
the one channel it is configured to work in. Provisioned that way, the scenario passes all four
of its steps.

That is a change to the test fixture, not to the worker, which is why it was resolved during the
build rather than escalated as an open question.

## Why this one is instructive

The correct fact was already written down in the same spec pack, one document away from the
scenario that contradicted it. The evidence ledger and the scenario list were authored as
separate artefacts and nothing cross checked them, which is exactly the kind of inconsistency a
knowledge base with one concept per file and explicit links is meant to make visible.

Related: [invite the worker to one channel](../setup/invite-the-worker-to-one-channel.md),
[the H3 defect](spec-defect-h3-reads-the-wrong-surface.md).
