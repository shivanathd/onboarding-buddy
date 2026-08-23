---
type: Concept
title: Messages from a deleted app cannot be removed
description: Delete the app and its posted messages become unremovable by any app; only a workspace administrator can clear them.
source: ["observed live during the build session, reported 2026-08-23"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [slack-app, cleanup, operations]
---
# Messages from a deleted app cannot be removed

Message deletion is bound to the author. A message posted by an app can be deleted by that app,
and a message posted by a different app cannot. Delete the app and you have removed the only
identity that was allowed to clean up after it, so its messages stay in the channel and no app
can take them out. From that point only a workspace administrator can clear them.

This bites in exactly the situation where you are least expecting it: tidying up. The instinct
after a demo or a test run is to delete the throwaway app first, because that feels like the
big removal. Do it in that order and you are left with a channel full of orphaned bot messages
and no programmatic way to reach them.

The order that works:

1. Delete the messages the app posted, using that app's own token.
2. Delete the List and any canvases it created; those are files, so see
   [a List is a file](a-list-is-a-file.md).
3. Delete the app.

Worth noting for a demo workspace specifically: a channel is cheap. Archiving or deleting the
whole channel is usually a faster cleanup than chasing individual messages, and it does not
depend on the app still existing.

This is a provenance note rather than a documented contract; it was observed during the build
session rather than taken from a reference page.
