# Session 5 · Connect the fleet

The talk pack for **"Connect the fleet: Agentforce"** — Slack Community Hyderabad,
2 September 2026, session 5 of 5 in *Slack as your second brain*.

Two Agentforce and Slack runtimes handing work to each other in one channel, with a
human at the end. This folder is everything behind that hour.

## What is here

| File | What it is |
|---|---|
| **`handout.html`** | **Start here.** A build-it-yourself tutorial, written as four rungs. Rung 0 takes five minutes and needs no code, no Agentforce and no extra licence. |
| **`runbook.html`** | The presenter's run of show. Every typed line, what to point at, and the traps — including the ones that only appear live. |
| **`build-log.md`** | The corrections log. Every dead end, in the order I hit them. |
| **`wiki/`** | 30 concepts in [Open Knowledge Format](https://github.com/google/open-knowledge-format) — one fact per file, each with its own provenance. |

## Read the runbook as a script, not a manual

It is written in second person, to me, standing at a keyboard. Slide numbers refer to a
40-slide deck that ships separately. Read it for the warnings rather than the choreography:
the record tabs render empty until synced, an Agentforce reply in a channel is ephemeral to
whoever asked, `app_mention` is intermittent for bot-authored mentions, and a Slack List
created by an app is shared with nobody by default.

## Everything is placeholdered

No workspace, org, channel, user, List or app identifier from my environment is in here, and
no host paths. `handout.html` §0 lists every placeholder and where to get your own value.

## The worker itself

The Python worker these documents describe is the repository this folder sits in. See the
root `README.md` for a 15-minute quickstart and the `Deploy on Railway` button.

## If you only do one thing

Flip **Slack Channels for Records** for one object, bind one channel, and live with it for a
week. Five minutes, no licence, no agent, no code — and it is the change that made everything
else in the talk possible.
