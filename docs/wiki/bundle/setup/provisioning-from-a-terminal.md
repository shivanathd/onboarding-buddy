---
type: Process
title: Provisioning from a terminal
description: The scripted, browser free route used to build the test environment, including one undocumented call that returns every token.
source: ["docs/provisioning-without-a-browser.md", "PROGRESS.md provisioned already, all headless (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, provisioning, headless, undocumented]
---
# Provisioning from a terminal

Everything used to build the live test environment was done from a terminal, with no clicking.
That matters if you want any of it to be repeatable, scriptable, or runnable on a machine with
no screen. It is not the route the quickstart teaches, and the reason is at the bottom of this
page.

## Signing in without a browser

The Slack command line tool supports a two step sign in. Ask for a ticket and it prints a slash
command. Run that slash command in any Slack channel, approve the dialog, and Slack shows a
short challenge code. Feed the ticket and the code back, and the session is stored. That is the
only human step in the whole chain, and it happens once.

## One undocumented call returns every token

The tool has no command for creating tokens, but tracing what it does while running an app
reveals a single call that returns all three at once: the bot token, a user token, and the app
level token a socket connection needs. It takes a configuration token in the authorization
header and a body naming the app and the scopes.

Two things to know about it:

- It only grants scopes the app manifest already declares, so the sequence is always update the
  manifest first, then install.
- It grants additively. Reinstalling with fewer scopes does not take the old ones away.

## Everything else is ordinary API calls

Creating the channel, creating and seeding the List, creating the canvas that holds the job
description, and resolving user ids were all normal calls, made with a temporary scope grant
that was handed back immediately afterwards. The worker itself runs on only
[the eight bot scopes](the-eight-bot-scopes.md), so the demo runs on exactly the permissions a
reader gets.

## Why the quickstart does not teach this

That token call is not a documented endpoint and can change without notice. It is excellent for
a scripted test environment and it is not something to build a product on, which is why
[the manifest route](create-the-app-from-a-manifest.md) is what the repository README teaches.

One related trap: the app level scope cannot be provisioned this way either, because it is not a
manifest concept at all. See
[app level scopes are stripped from a manifest](../gotchas/app-level-scopes-are-stripped-from-a-manifest.md).
