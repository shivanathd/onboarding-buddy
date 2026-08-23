---
okf_version: "0.3"
---
# How a Slack digital worker was built

An Open Knowledge Format bundle documenting the building of `onboarding-buddy`, a small open
source Slack digital worker: how to set it up, what the API actually does as opposed to what the
documentation says, every decision and why, and what a fully green test suite still failed to
catch.

One concept per file, with its provenance in the file's own frontmatter. Every fact here was
confirmed against a live Slack workspace on 2026-08-23.

New here? Start with [the four jobs](worker/the-four-jobs.md) to see what the thing is, then
[create the app from a manifest](setup/create-the-app-from-a-manifest.md) to build one. If you
are here for the hard won part, go straight to [gotchas](gotchas/index.md).

## Sections

- [worker](worker/index.md): what it is, before how it was set up
- [setup](setup/index.md): the reproducible path to a worker on shift
- [gotchas](gotchas/index.md): behaviour the documentation does not describe
- [decisions](decisions/index.md): the spec's ADRs and the build's ADRs, kept apart
- [verification](verification/index.md): how it was proven, and what the tests missed
- [rehearsal](rehearsal/index.md): the unknowns the spec refused to assert

## Companion documents

Two prose documents in the same repository cover the same ground as narrative rather than as
concepts. This knowledge base complements them and does not replace them.

- `docs/how-this-was-built.md`: the method, in order.
- `docs/provisioning-without-a-browser.md`: the headless provisioning path.
- `README.md`: the fifteen minute quickstart.

## No real identifiers

Every identifier in this bundle is a placeholder. Shapes are shown, values are not. No token,
channel, user, file, List, column, team or app identifier here is real, and no workspace or
person is named.
