# Gotchas

Every one of these cost real time. Ordered by how likely it is to break a live demo.

- [The record tabs load lazily and need a sync](record-tabs-load-lazily.md) — the most demo-dangerous; Act 3 depends on it
- [A bot-owned List is shared with nobody](a-bot-owned-list-is-shared-with-nobody.md) — it existed, the worker read it, and no human could open it; a setter with no getter
- [An agent that opens with what it cannot do reads as broken](lead-with-the-answer.md) — prompt ordering, not model capability; the most common reason an agent feels unhelpful
- [An agent's channel reply is private](agent-replies-are-ephemeral.md) — and an absent agent fails just as silently
- [Both status panels lie](admin-panels-do-not-reflect-runtime-state.md) — verify by mentioning, never by reading a panel
- [Agent Script cannot reach Slack](agent-script-cannot-reach-slack.md) — two stacked constraints, and the ID prefix that proves the second
- [A localAction with no schemas fails silently](local-action-schemas.md) — a green deploy is not evidence
- [app_mention is unreliable for bot mentions](duplicate-bot-mentions.md) — dedupe rather than choosing a listener
- [Two authoring lanes drift silently](two-authoring-lanes-drift.md) — assert shared behaviour in tests
- [Test wording rots](test-wording-rots.md) — whitelists, relative dates, and a grader that passes a contradiction
- [A one-member workspace collapses person columns](one-member-workspace.md) — what to say instead of hiding it
