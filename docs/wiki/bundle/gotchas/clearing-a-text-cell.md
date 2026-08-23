---
type: Concept
title: Clearing a text cell is not writing an empty string
description: An empty rich text node is rejected outright; the shape that empties a cell is an empty array.
source: ["docs/how-this-was-built.md", "PROGRESS.md more undocumented shapes (private build log)", "live slackLists.items.update call, 2026-08-23"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [slack-lists, undocumented, api-shapes]
---
# Clearing a text cell is not writing an empty string

A text cell in a Slack List is not a string. It is an array of rich text blocks, so writing to
one means building that structure, and the obvious way to clear one does not work.

Sending an empty text node is rejected:

```
must be more than 0 characters
```

The shape that actually empties the cell is an empty array:

```json
{"column_id": "Col0000000000", "rich_text": []}
```

The asymmetry is the trap. Writing a value and clearing a value are different shapes, not the
same shape with a different payload, and nothing in the documentation says so.

This matters for the Thread column specifically, which is where the worker records that it has
already opened a message about a row. Clearing that cell is how you reset a row so it can be
chased again, and it is exactly the operation the wrong shape breaks.

Related: [the List is the memory](../worker/the-list-is-the-memory.md),
[a select column needs three fields](select-column-needs-value-label-and-colour.md).
