---
type: Concept
title: A List belongs to the app that created it
description: Lists carry per app access, so a second app reading a List another app created gets a not found error rather than a permission error.
source: ["observed live during the build session, reported 2026-08-23", "spec EVIDENCE.md E3 (documents the read, not the access model)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [slack-lists, undocumented, permissions]
---
# A List belongs to the app that created it

Holding `lists:read` is not enough to read an arbitrary List. Access is scoped per app: a
second app asking for a List that a different app created is told the List does not exist, not
that it is not allowed.

The error is the misleading part. A not found response reads like a wrong identifier, so the
natural reaction is to go and re-check the id, which is correct and which will keep telling you
the id is right. The actual cause is that the requesting app is not the one that owns the List.

Practical consequences:

- Do not plan on two apps sharing one List. If a second app needs the same state, the List has
  to be created in a way that grants it access, or the second app needs its own.
- When you rotate from a throwaway development app to a real one, the real app cannot simply
  pick up the development app's List. Bootstrap a fresh one.
- A not found error on a List you can see in the interface is an ownership question first and
  an identifier question second.

This is a provenance note rather than a documented contract: it was observed against the live
API during the build, and Slack's reference describes the read method without describing this
access model.

Related: [a List is a file](a-list-is-a-file.md),
[the List is the memory](../worker/the-list-is-the-memory.md).
