---
type: Credential
title: The app level token for Socket Mode
description: Socket Mode needs an app level token carrying connections:write, generated on the app page and never declared in a manifest.
source: ["README.md 15 minute quickstart step 1", "docs/provisioning-without-a-browser.md", "spec EVIDENCE.md E8", ".env.example"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, credentials, socket-mode]
---
# The app level token for Socket Mode

The worker needs two Slack tokens, and they come from different places for different reasons.

| Setting | What it is | Where it comes from |
| --- | --- | --- |
| `SLACK_BOT_TOKEN` | the bot user token, carrying the eight bot scopes | the Install App page, after installing to the workspace |
| `SLACK_APP_TOKEN` | an app level token carrying `connections:write` | Basic Information, App Level Tokens |

No value for either belongs in this knowledge base, in the repository, or in a commit. Both
live only in the settings file, which is ignored by git, or in the hosting dashboard.

## The app level token is not a manifest concept

This is the part that costs people time. `connections:write` is an app level scope, and app
level scopes are not stored in a manifest. You may put such an entry in a manifest document and
Slack will accept it, but round tripping the manifest shows the entry has been dropped. Any
guide that tells you to declare it there is wrong. The scope is granted where app level tokens
are created, and nowhere else. See
[app level scopes are stripped from a manifest](../gotchas/app-level-scopes-are-stripped-from-a-manifest.md).

## Why Socket Mode at all

The app dials out over a websocket, so there is no public URL, no request signing and no
ingress to configure. That is what makes the same folder run unchanged on a laptop and on a
hosted service. The cost is one operational rule: exactly one worker on shift, because Slack
load balances events across connections rather than duplicating them. See
[ADR-6](../decisions/spec-adr-6-socket-mode.md) and
[events are load balanced](../gotchas/events-are-load-balanced-not-duplicated.md).
