---
type: Process
title: Create the app from a manifest
description: Paste the repository manifest into the Slack app creation flow, which sets the scopes, the events and Socket Mode in one step.
source: ["README.md 15 minute quickstart step 1", "manifest.json", "spec REQUIREMENTS.md OPS-10"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, slack-app, manifest]
---
# Create the app from a manifest

About four minutes. You need a Slack workspace you can install an app into, and Python 3.11
or newer for the later steps.

1. Go to the Slack app directory for developers and choose to create an app **from an app
   manifest**.
2. Pick your workspace.
3. Paste the contents of `manifest.json` from the repository.
4. Create the app.

The manifest carries everything that can be declared as a document: the display name, the eight
bot scopes, the two event subscriptions (`app_mention` and `reaction_added`), interactivity
enabled, and Socket Mode enabled. Doing it this way means the scopes cannot drift from the
repository, which is why one of the checks asserts the manifest and the documented scope list
agree.

Two things the manifest cannot do for you:

- It cannot grant the app level scope Socket Mode needs. That entry is silently dropped, which
  is a trap in its own right. See [the app level token](the-app-level-token.md) and
  [app level scopes are stripped from a manifest](../gotchas/app-level-scopes-are-stripped-from-a-manifest.md).
- It cannot join a channel. See [invite the worker to one channel](invite-the-worker-to-one-channel.md).

Next: on the Install App page, install to the workspace and copy the bot user token. That is
the first of the two Slack values the settings file needs.

There is also a scripted route that never opens a browser, useful for a test environment;
see [provisioning from a terminal](provisioning-from-a-terminal.md).
