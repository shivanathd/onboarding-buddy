---
type: Process
title: Build the List by hand
description: The fallback for Enterprise Grid or a plan without Lists, where the API cannot create a List and the six columns have to be made in the interface.
source: ["README.md building the List by hand", "bootstrap.py explain()", "spec EVIDENCE.md E1", "spec REQUIREMENTS.md BOOT-5", "git log 0df1a00"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, enterprise, slack-lists, fallback]
---
# Build the List by hand

Two situations land here, and neither can be fixed from code, so the bootstrap script prints an
explanation and stops. The same path works if you would simply rather click.

- **Enterprise Grid.** The Lists API cannot create a List at all and returns a restriction error.
- **A plan without Lists.** On a free or trial workspace the feature may not be available, which
  surfaces as a refusal that reads like a permission problem. Adding scopes will not help.

Try creating a List by hand first, because that is the test that tells the two apart. If the
Slack interface offers it, you are in the first case and the steps below finish the job. If the
interface does not offer it either, it is a plan limit, this path is closed too, and the List
backed half of the worker cannot run in that workspace at all.

## The six columns

1. Create a List in Slack with six columns:
   - **Step**, text, and set it as the primary column
   - **New hire**, user
   - **Owner**, user
   - **Due**, date
   - **Status**, select, with the options Open, Done and Escalated
   - **Thread**, text
2. Add one row, so the columns actually exist.
3. Read the column ids back with the List items read method. Every field in the response
   carries its `column_id`.
4. Copy the List id and the six column ids into the settings file by hand.

Exactly one column may be the primary column and it must be a text column. That is not a style
preference; the API enforces it, and the primary column cannot be reassigned later.

The option values matter as much as the labels. The code stores lowercase option values and
displays the capitalised labels, and the bootstrap script creates the column with exactly that
mapping. If you build the List by hand, keep the same pairing or the Status reads will come back
empty. A select column read with the wrong reader is precisely how one late defect happened;
see [defects a green suite missed](../verification/defects-a-green-suite-missed.md).

Related: [bootstrap the List](bootstrap-the-list.md),
[a select column needs three fields per choice](../gotchas/select-column-needs-value-label-and-colour.md).
