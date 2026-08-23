# Onboarding Buddy

A small, real digital worker for Slack. It does four things:

| Job | Trigger | What it does |
|---|---|---|
| Answer | you mention it | replies in the thread, grounded in a Slack List |
| Advance | you react with a tick | flips the row to Done and confirms |
| Chase | a clock it owns | opens a thread when a step is past its grace window |
| Report | Monday morning | posts cohort status from the List |

Those four verbs are generic. Onboarding is just the example. The same skeleton
runs a deal desk, compliance renewals, a candidate pipeline, or contract
expiries. Swap the List and the job description, keep the body.

You are not taking home an onboarding bot. You are taking home a body that any
job description fits into.

Three dependencies. No database. The Slack List is the only durable state, so
you can read everything the worker knows in the Slack interface.

## 15 minute quickstart

You need Python 3.11 or newer and a Slack workspace you can install an app into.

### 1. Create the app, 4 minutes

Go to api.slack.com/apps, choose "From an app manifest", pick your workspace,
and paste the contents of `manifest.json`. Create the app, then:

- Basic Information, App-Level Tokens: generate a token with the
  `connections:write` scope. That is your `SLACK_APP_TOKEN`, starting `xapp-`.
- Install App: install to the workspace and copy the Bot User OAuth Token.
  That is your `SLACK_BOT_TOKEN`, starting `xoxb-`.

The app-level token is not part of the manifest. Slack does not store app level
scopes in a manifest, so that token has to be generated on the page.

### 2. Invite the worker to one channel, 1 minute

Create or pick a channel, then `/invite @onboarding-buddy`. The worker only
knows one channel. If it is not a member, Slack never sends it the mention.

### 3. Fill in the settings, 3 minutes

    git clone https://github.com/shivanathd/onboarding-buddy
    cd onboarding-buddy
    python3 -m venv ../obb-venv && . ../obb-venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

Keep the virtual environment outside the repository. Nothing breaks if you put
it inside, but the checks in this project scan every file in the tree and a
virtual environment drags several thousand unrelated files into that scan.

Open `.env` and fill in the two Slack tokens, your Anthropic key, the channel
id, and your own user id as `MANAGER_ID`. You can leave the List settings empty,
because the next step prints them.

### 4. Create and seed the List, 3 minutes

    python bootstrap.py

That creates a List with six columns, seeds a starter cohort, and prints seven
lines. Paste them over the matching lines in `.env`.

Column ids look like `Col0000000000`. They are opaque and there is no way to
guess them, which is exactly why this step prints a mapping instead of hiding
one. If you would rather build the List by hand, see the manual path below.

### 5. Put the worker on shift, 1 minute

    python app.py

You should see a line saying `worker on shift`. Mention the worker in your
channel and it will answer in the thread.

## Deploy on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template?template=https://github.com/shivanathd/onboarding-buddy)

Same folder, same code, no changes. Your laptop and a hosted service are the
same worker on two shifts. The laptop is where you learn. When the worker earns
a real shift, host it, because a sleeping laptop is a sleeping worker.

Set the same variables from `.env` in the Railway dashboard rather than in a
file. `railway.json` sets the builder and the start command and deliberately
carries no variables, because configuration defined in code overrides the
dashboard and you do not want your tokens in git.

Socket Mode means there is no public URL, no request signing, and no ingress to
configure. The worker dials out.

### Set TZ or read the boot log

A container runs in UTC. A 9am cron in the wrong timezone is the first thing
that surprises people, so set `TZ` to an IANA name such as `Europe/London`. The
worker prints the timezone it is actually using on every boot. Believe the log,
not your assumption.

## One worker on shift at a time

This matters more than it sounds. Slack allows up to ten concurrent Socket Mode
connections per app, and when several are open it will load balance each event
to one of them. Not duplicate. Load balance.

So if your laptop and your hosted service are both connected, each one receives
a random half of the events, and the worker looks broken in a way that is very
hard to debug. Stop one before you start the other.

## Scopes, and why each one

Bot scopes, all eight in `manifest.json`:

| Scope | Why the worker needs it |
|---|---|
| `app_mentions:read` | to hear you mention it |
| `chat:write` | to answer, nudge, and report |
| `reactions:read` | to see the tick that closes a step |
| `lists:read` | to read the List, which is its memory |
| `lists:write` | to tick a row and to write a thread id back to it |
| `channels:history` | to read recent conversation for context |
| `files:read` | to read the canvas holding its job description |
| `canvases:read` | to find that canvas |

App level scope, generated on the app page rather than in the manifest:

| Scope | Why |
|---|---|
| `connections:write` | to open the Socket Mode websocket |

One optional bot scope, not in `manifest.json`:

| Scope | Why you might add it |
|---|---|
| `assistant:write` | lets the worker use Slack's own thinking indicator while it reads the List, instead of posting a status message it later edits. Purely cosmetic. Without it the worker behaves identically. |
| `users:read` | lets the worker put a person's name next to their id when it reads the List, so you can ask about someone by name rather than by mention. Without it, ask using an at mention instead. |

That table is the employment contract. It is short on purpose. A worker that
can only do these things cannot surprise you in a new category.

## The job description lives in a canvas

The worker reads a canvas at run time and uses it as its brief: tone, priorities,
how to phrase an escalation. Point `CANVAS_FILE_ID` at a canvas and anyone who
can edit it can change how the worker behaves, with no deploy and no code.

That is the point, and it is also a governance question. Whoever can edit that
canvas can reprogram the worker. Treat canvas permissions accordingly. Hard
limits belong in `policy.py` and in the scopes above, not in the brief.

If the canvas cannot be read, the worker falls back to `seed/job-description.md`
in this repository and says so loudly in the log. There is no official API that
returns canvas text, so this path is deliberately defensive.

## DEMO_MODE

Nobody wants to wait until 9am to see a clock fire. `DEMO_MODE=true` does
exactly three things:

- grace windows shrink from days to minutes
- chase runs every 60 seconds instead of on the daily cron
- report runs when you mention the worker and say "run report"

The real cron lines stay visible in `app.py`, directly above the demo override.
The escalation threshold is not compressed, so you still see the difference
between a nudge and an escalation.

## Settings

Every id lives in `.env`, never in code. `.env` is gitignored.

| Variable | What it is |
|---|---|
| `SLACK_BOT_TOKEN` | bot token, starts `xoxb-` |
| `SLACK_APP_TOKEN` | app level token, starts `xapp-` |
| `ANTHROPIC_API_KEY` | leave empty to run on templates only |
| `ANTHROPIC_MODEL` | swap the brain here, one line |
| `CHANNEL_ID` | the one channel the worker knows |
| `MANAGER_ID` | who gets escalations and unassigned rows |
| `CANVAS_FILE_ID` | the canvas holding the job description, optional |
| `LIST_ID` | the List that is the worker's memory |
| `COL_STEP` | the Step column, primary and text |
| `COL_HIRE` | the New hire column |
| `COL_OWNER` | the Owner column |
| `COL_DUE` | the Due column |
| `COL_STATUS` | the Status column |
| `COL_THREAD` | the Thread column, where a chase writes its message id |
| `DEMO_MODE` | true compresses the clock |
| `TZ` | IANA timezone name for the scheduler |

## Building the List by hand

`bootstrap.py` calls the Lists API. On an Enterprise Grid organisation that
call returns `enterprise_is_restricted` and cannot create a List at all. If you
hit that, or if you would simply rather click:

1. Create a List in Slack with six columns: Step (text, the primary column),
   New hire (user), Owner (user), Due (date), Status (select with the options
   Open, Done and Escalated), Thread (text).
2. Add one row so the columns exist.
3. Read the column ids back with `slackLists.items.list` and copy them into
   `.env`. Each field in the response carries its `column_id`.

Exactly one column may be the primary column, and it must be a text column.

## What is in here

    app.py          sixty lines: three listeners, two clock lines, one socket
    agent.py        the brain, one function, the smallest file here
    policy.py       grace windows and thresholds, plus every setting
    bootstrap.py    creates and seeds the List, prints the mapping
    jobs/           answer, advance, chase, report, approval
    tools/lists.py  the only file that talks to the Lists API
    tools/context.py  the List, then the brief, then the conversation
    seed/           a generic starter cohort and a starter job description
    manifest.json   the app definition, scopes annotated above
    railway.json    builder and start command for the hosted path

Every job file opens with the same five lines: trigger, reads, writes, surface,
and whether it uses the brain. Read those and you know the whole worker.

`agent.py` is the smallest file in the repository. That is deliberate. The room
expects the model to be the big part. It is not. The body is the product.

## When not to use this

If your job is "remind someone when a date passes", close this repository and
build a Slack workflow instead. This is overkill for that, and a workflow will
be running in five minutes.

A worker earns its keep when the job crosses one of these lines:

1. it has to compose from several sources at once
2. the judgement is in the message, not just in the trigger
3. it needs a human approval loop and has to act on the answer
4. it writes state back and matches later events to it

This worker knows one channel and one List. It does not know your CRM and it
does not know its colleagues exist. Routing between workers is still a human
habit.

The brain is rented by the token. Chase and Report cost nothing to run because
they never call it. Answer costs what judgement costs.

## Licence

MIT. See LICENSE.
