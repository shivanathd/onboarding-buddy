---
type: Concept
title: A List is a file
description: A Slack List is a file object, so the ordinary file deletion method removes one and there is no List deletion method to look for.
source: ["docs/how-this-was-built.md", "PROGRESS.md learned against the live API (private build log)", "live files.delete call on a List, 2026-08-23"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [slack-lists, undocumented, files]
---
# A List is a file

There is no List deletion method, and looking for one wastes time. A Slack List is a file
object, so the ordinary file deletion method removes it. That is how the throwaway List created
during the select column schema probe was cleaned up.

The identifier shape gives it away once you notice: a List id has the same prefix as a file id,
not a channel id. So does a canvas id, for the same reason, which is why the canvas read path
goes through the file information method at all.

Two things follow from the same fact:

- A List is subject to file permissions and file retention, not to channel membership.
- Anything that enumerates files will enumerate your Lists and your canvases too.

This is a good example of a general rule for this platform: when a method you expect does not
exist, ask what primitive the object actually is. Several Slack surfaces that read like their
own thing are files underneath, and the file methods are the ones that work on them.

Related: [canvas content has no read API](canvas-content-has-no-read-api.md),
[a List belongs to the app that created it](a-list-belongs-to-the-app-that-created-it.md).
