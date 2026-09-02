---
type: Process
title: The five acts — the demo path, verbatim
description: "One story in one channel: what to do, what to say, what to expect, and the fallback for each act."
source: ["S5-runbook.html", "live rehearsal of Acts 1 and 4 in <your record channel> 2026-08-31", "sf agent test run S5_Deal_Desk_Suite 36/36"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [demo, runbook, slack, agentforce]
---
# The five acts

Everything happens in `#Meridian Systems - Platform Expansion FY27`. A staffing deal for four
consultants moves from proposal to closed, and two agent runtimes hand work to each other.

| Act | The room sees | Runtime | ~min |
|---|---|---|---|
| 1 | Four Salesforce tabs living in a Slack channel | no code | 8 |
| 2 | An agent answering from real fields, and from the Job | Agentforce | 12 |
| 3 | A write that drafts and waits for consent | Agentforce | 10 |
| 4 | The agent handing work to a Python worker | both | 12 |
| 5 | The worker asking a *human* to close the deal | human | 10 |

---

## Act 1 · the channel is the record

**Say:** "Everything we built in the first four sessions was ours. Today we plug into
something that already exists — a CRM with permissions, an audit trail and other people's
rules. And the first thing to notice is that I wrote no code for this act at all."

**Do:** Point at the channel badge — **Opportunity**. Walk the four tabs: Opportunity details
(*See all 86 fields*, `Next Step` and `Manager Notes` edit in place), Field History, Contact
Roles (change Anita Rao's role live — it writes back), Related conversations.

**Say:** "Nobody built this. It's a per-object switch in Setup, and the thing that took me
longest to find is that it's off **by default, per object**. The error is a full-page 'Slack
isn't set up for Opportunities', and there's no metadata type for the switch — it's a click,
or it's nothing."

**Trap:** the stage path ribbon is configured for different labels and highlights
*Qualification* while the record is `Proposal/Price Quote`. Point at the **Stage field**.

---

## Act 2 · the agent answers from the record

**Do:** `@Polly PeopleOps what's the latest on the Meridian deal?`

**Expect — say this before you press enter:** the channel shows only *"I've privately shared
an answer with @you."* The real answer is **ephemeral, visible to you alone**. It is not
broken.

**Do:** `@Polly PeopleOps post to this channel how many consultants the Meridian deal is for and who is placed. List only, do not hand off and do not tag anyone.`

**Both tails matter.** *"post to this channel"* makes the answer a real message rather than
one only you can see. *"do not hand off and do not tag anyone"* stops her appending a handoff
line and **tagging herself** — her instructions tell her to hand off but never give her the
buddy's handle, so with no name in the ask she fills the slot with the only agent handle she
knows.

**Expect:** 4 openings, and the four consultants — Priya Raman, Rahul Menon, Sara Okonkwo,
Tom Whelan.

**Say:** "It didn't summarise a document. It resolved a name to a record, followed two
lookups, read the fields, and stopped. And note the path — there's no Opportunity field on a
Placement. It had to go through the Job, because that's how the data actually is, not how I
wish it were."

**The permissions half — from Setup, not from a chat bubble.** Setup → Profiles → **Demo AE**
→ Field-Level Security → Opportunity → **Amount, unchecked**. Then Demo Sales Manager →
checked.

**Say:** "The agent's permissions are not the agent's — they're yours. When Priya asks, the
same agent, the same topic, the same action returns a record without an Amount on it, because
field-level security got there first. You don't configure that in the agent. You can't
configure it away in the agent either."

---

## Act 3 · the write, with a gate

**Do:** `@Polly PeopleOps move Meridian to Negotiation/Review.`

**Expect a TWO-step gate.** First in words: *"I'm ready to update the stage of 'Meridian
Systems - Platform Expansion FY27' from 'Proposal/Price Quote' to 'Negotiation/Review'. Would
you like me to proceed?"* Reply `yes`. Then a **record card** — the record, the field, the new
value — with **Confirm**, **Edit Full Record** and **Cancel**. Only clicking Confirm runs
`update_record`, and the card flips to ✓ Confirmed.

**Point at "Edit Full Record".** It is the strongest thing on the screen: the human is not
reduced to yes or no, they can amend the agent's proposal before it commits.

**Say:** "That gate is not a sentence in a prompt asking it to be careful. The update action
is declared with `require_user_confirmation`. The platform holds it. I could not talk it into
skipping that if I tried."

**Confirm inside the thread.** Polly answers in a thread and the pending change lives in that
thread's session. Saying "yes, confirm" as a *new channel message* does nothing — verified: no
write, no history row. Also, **Probability moves 75 → 90 on its own**; that is the Salesforce
stage model, not the agent, and someone will ask.

**Do:** Click Confirm. Open **Opportunity Field History** — **and click the sync icon.** The
tab is a Slack List; it will show stale data or nothing until you sync.

**The bit worth the ticket price. Do:**
`@Polly PeopleOps move Meridian to stage Handshake Pending.`

**Expect:** it refuses to draft at all, lists the valid stages, **zero actions executed**.

**Say:** "This failed when I first tested it. The agent cheerfully drafted a stage that
doesn't exist, because the instruction told it to check the valid values and nothing in its
context contained them. The fix wasn't a better prompt — it was giving it the list. Then the
test caught it."

---

## Act 4 · the handoff

**Do:** `@Polly PeopleOps post the Meridian placement roster to this channel as a message, and in that same message ask @onboarding-buddy to start onboarding them.`

**"Start" is safe to say now.** It used to open with *"I'm not able to start onboarding, I
only read the List and reply here"* and bury the useful part. Fixed — see
[lead with the answer](../gotchas/lead-with-the-answer.md). It now answers *"Onboarding for
the four Meridian placements is already underway, 12 steps tracked, 5 overdue"*, lists them,
and closes with *"Nudges on these go out via the tick, not from me."*

**Expect:** a **real** channel message from Polly, naming the four consultants and mentioning
the buddy, with Slack's *"Action triggered by @you"* appended. Then in Railway:
`MESSAGE handoff from bot <a bot id>, turn 1`. Then the worker's report card —
*Sara Okonkwo — Access badge, 8 days over*.

**Say:** "That's a different action. Its answer to me was private. To speak to the channel it
had to call `SendMessageToSlackChannel` explicitly. Those are two different things and
confusing them cost me an afternoon."

**Say:** "Two runtimes. One is a Salesforce agent I configured with no code. One is a Python
process on Railway I wrote every line of. They just handed work to each other in a channel,
and the only thing they share is the room."

**Do:** approve the escalation when the worker raises it.

---

## Act 5 · the loop closes

**Do:** let the worker post completion. Then **you** type:
`@Polly PeopleOps onboarding is done — move Meridian to Closed Won.` Confirm.

**Say:** "Notice who did that last step. Not the worker. The worker *asked*, and it asked me.
An Agentforce agent in Slack runs every action in the invoking user's Salesforce identity. A
bot doesn't have one. So a bot cannot authorise a CRM write — not because I put a guard in,
but because there's no user for the platform to run as. That's not a gap in the demo. That's
the governance model."

Full reasoning: [the closer](the-closer.md).

---

## Fallbacks

| If this dies | Do this |
|---|---|
| Polly does not answer | Check she is *in* the channel. Then Agent Builder preview on `S5_Deal_Desk` v5 — same topic, same actions, different surface. Say you are switching and why |
| The ephemeral answer never appears | Refresh Slack. The public "privately shared" line is the tell it ran |
| A tab is empty | Click the sync icon. Twice if needed |
| The agent answers wrongly | `S5-slide15-trace.md` — a real captured session, turn by turn |
| The handoff does not wake the worker | *You* type `@onboarding-buddy report`. Act 5 already depends on you for the reverse direction, so it is consistent rather than a gap |
| Railway is down | Acts 1, 2, 3 and 5 need no worker. Cut Act 4 and go to the governance close |
| Everything dies | The [screenshots](../screenshots/index.md) cover Acts 1 and 4; narrate 2, 3 and 5 from the trace table |

Related: [preflight](preflight.md), [reset after the demo](reset-after-the-demo.md).
