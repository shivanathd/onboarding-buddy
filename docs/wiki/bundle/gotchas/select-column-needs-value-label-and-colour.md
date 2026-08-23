---
type: Concept
title: A select column needs value, label and colour
description: Every choice in a select column must carry all three fields; none of this is documented, and the error messages are how the shape was found.
source: ["docs/how-this-was-built.md", "bootstrap.py SCHEMA", "PROGRESS.md learned against the live API (private build log)", "live slackLists.create call, 2026-08-23"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [slack-lists, undocumented, api-shapes]
---
# A select column needs value, label and colour

Creating a List with a select column requires each choice object to carry a value, a label
**and** a colour. All three are mandatory. Omit any one and the create call fails. None of this
appears in the documentation.

```json
{"key": "status", "name": "Status", "type": "select",
 "options": {"choices": [
   {"value": "open", "label": "Open", "color": "blue"},
   {"value": "done", "label": "Done", "color": "green"},
   {"value": "escalated", "label": "Escalated", "color": "red"}]}}
```

## Read the error, not the docs

This is the redeeming part. Slack's validator returns json-pointer paths naming the exact
missing field, which is genuinely helpful and is how the shape was discovered in the first
place:

```
[ERROR] missing required field: color [json-pointer:/schema/4/options/choices/0]
```

The number after `schema` is the column index and the number after `choices` is the choice
index, so the error tells you exactly which choice in which column is incomplete. Three failed
calls, read carefully, produced the whole shape.

## The consequence downstream

A select cell stores the option **value**, not the label. The code keeps a mapping from
lowercase values to display labels, and the bootstrap script creates the column with exactly
that pairing. Reading a select cell with a text reader returns nothing at all and silently
defaults, which is how one late defect happened; see
[defects a green suite missed](../verification/defects-a-green-suite-missed.md).

The discovery method generalises: the throwaway List used for this schema probe was deleted
afterwards, which turned out to need [a file deletion](a-list-is-a-file.md).
