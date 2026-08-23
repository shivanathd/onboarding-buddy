---
type: Concept
title: App level scopes are stripped from a manifest
description: A manifest may carry an app level scope entry and Slack accepts the document, but round tripping shows the entry has been silently dropped.
source: ["docs/provisioning-without-a-browser.md", "README.md 15 minute quickstart step 1", "spec EVIDENCE.md E8"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [manifest, scopes, socket-mode, undocumented]
---
# App level scopes are stripped from a manifest

Socket Mode needs an app level token carrying `connections:write`. You cannot declare that
scope in a manifest, and the way you find out is unpleasant: Slack accepts the document without
complaint, then round tripping the manifest shows the entry has been dropped.

Silent acceptance is what makes this expensive. Nothing fails. There is no error to read and no
warning to search for. You get an app that looks correctly configured and a socket connection
that will not open, and the manifest you are staring at appears to say the right thing.

The scope has to be granted where app level tokens are created, on the app's Basic Information
page. Any guide that tells you to put it in a manifest is wrong, including an earlier draft of
the one in this repository.

Two corollaries:

- A manifest is not a complete description of an app's permissions. Bot scopes it can carry;
  app level scopes it cannot.
- The scripted provisioning route cannot grant it either, for the same reason: that path installs
  the scopes the manifest declares, and this is not one of them. See
  [provisioning from a terminal](../setup/provisioning-from-a-terminal.md).

Related: [the app level token](../setup/the-app-level-token.md),
[create the app from a manifest](../setup/create-the-app-from-a-manifest.md).
