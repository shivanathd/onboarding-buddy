---
type: Concept
title: The eight bot scopes
description: The exact bot permission set the worker runs on, and the single reason each one exists.
source: ["README.md scopes table", "manifest.json", "spec REQUIREMENTS.md OPS-10", "spec EVIDENCE.md E1 to E11"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, scopes, permissions, governance]
---
# The eight bot scopes

This table is the employment contract. It is short on purpose: a worker that can only do these
eight things cannot surprise you in a new category.

| Scope | Why the worker needs it |
| --- | --- |
| `app_mentions:read` | to hear you mention it |
| `chat:write` | to answer, nudge, and report |
| `reactions:read` | to see the tick that closes a step |
| `lists:read` | to read the List, which is its memory |
| `lists:write` | to tick a row, and to write a message id back into it |
| `channels:history` | to read recent conversation for context |
| `files:read` | to read the canvas holding its job description |
| `canvases:read` | to find that canvas |

`files:read` and `canvases:read` look redundant and are not. The `canvases:read` scope is
compatible with exactly one method, which returns section identifiers rather than document
text; the actual read goes through the file download path, which needs `files:read`. See
[canvas content has no read API](../gotchas/canvas-content-has-no-read-api.md).

There is no `users:read`. Resolving a user id to a display name would need it, and the worker
does not need it: mention markup renders as a name on the client for free.

## One optional scope, left out on purpose

`assistant:write` lets the worker use Slack's own thinking indicator instead of posting a status
message it later edits. It is purely cosmetic and the worker behaves identically without it, so
it is not in the manifest. Adding it would also change the exact scope set that one of the
checks asserts. See [a working status, then edited](../decisions/build-adr-b6-working-status-then-edit.md).

The app level scope is separate and is not a bot scope at all; see
[the app level token](the-app-level-token.md).
