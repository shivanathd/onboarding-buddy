---
type: Decision
title: A Slack List created by a bot is invisible to every human until you call slackLists.access.set
description: "The List existed with 12 rows and the worker read it every run, but every human who opened it got 'You don't have access to this list' — because a bot-created List is owned by the bot and shared with nobody."
source: ["files.info on YOUR_LIST_ID 2026-09-01 showing channels:[] groups:[] ims:[] shares:{}", "Slack UI 'You don't have access to this list' for the workspace owner", "slackLists.access.set probe results"]
verified: 2026-09-01
timestamp: 2026-09-01
tags: [slack, lists, permissions, silent-failure, demo-risk]
---
# A bot-owned List is shared with nobody

The worker's memory is a Slack List. It had 12 rows, the worker read and wrote it on
every run, and the report card carried an **Open the onboarding List** button.

Clicking that button, as the **workspace owner**, gave:

> 🔒 **You don't have access to this list.**

## The List was real. It was just shared with no one.

```
files.info on the List
  title      : Onboarding cohort
  filetype   : list
  created by : YOUR_WORKER_USER_ID        <- the bot
  is_public  : False
  channels   : []
  groups     : []
  ims        : []
  shares     : {}
slackLists.items.list             -> ok, 12 rows
```

A List created through the API belongs to the app that created it, and **is not
shared with anybody by default** — not the installer, not the workspace owner, not
the channel the app posts in. Nothing warns you, because from the app's side
everything works perfectly: it can read, write, and link to a List that no human
can open.

That is the trap. **The app is the only party for whom the feature appears to
work.**

## The fix

`slackLists.access.set`. It is not in the obvious place in the docs, and there is
no getter to check your work.

```bash
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data "list_id=$LIST_ID&user_ids=$USER_ID&access_level=write" \
  https://slack.com/api/slackLists.access.set
```

- Requires the **`lists:write`** scope.
- `access_level` is **required** — omitting it returns `invalid_arguments` with
  `missing required field: access_level`. Values seen to work: `read`, `write`.
- Accepts **`channel_ids`** as well as `user_ids`. Granting a channel puts the List
  in that channel's Files, which is the better move for a demo — everyone in the
  room's channel gets it, not one named account.

Probed and rejected along the way: `files.share` (`not_allowed_token_type`),
`slackLists.share` and `slackLists.access.add` (`unknown_method`).

## There is no way to read the access back

`slackLists.access.get`, `slackLists.access.list` and `slackLists.info` are all
`unknown_method`. The only way to verify a grant landed is **`files.info`**, whose
`channels` and `shares` fields fill in afterwards:

```
channels : ['<a channel id>', '<your record channel>']
shares   : {"public": {"<a channel id>": [{"access": "write", "source": "ACCESS_SET", ...}]}}
```

That asymmetry — a setter with no getter — is why this is now a preflight check
rather than a thing to remember.

## Why it went unnoticed for two sessions

Every automated check passed, because every automated check used the **bot token**,
and the bot has always had access. The failure only exists for humans, and the only
human never clicked the button until the day before the talk.

**A check that runs as the app cannot detect a permission the app already holds.**
Where a feature exists for an audience, test it as that audience, or at least assert
the sharing state explicitly.

Related: [the worker and the List](../setup/the-worker-and-the-list.md),
[a one-member workspace](one-member-workspace.md).
