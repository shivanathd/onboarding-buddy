"""answer

trigger: a mention of the worker in the channel it knows
reads:   the List, then the brief, then the recent conversation
writes:  nothing
surface: a threaded reply under the mention, with a visible working status first
brain:   yes, with a template that carries the raw state when it fails
"""

import agent
import policy
from tools import context

MENU = ("I keep the onboarding List moving. Ask me where a step or a person "
        "stands, react with a tick to close a step, or say run report.")


def run(client, event):
    """Reply in the thread of the mention, grounded in the List first.

    UNVERIFIED whether an app_mention payload carries thread_ts for a mention
    made inside a thread, rehearsal check 2b. Both are handled.
    """
    if event.get("channel") != policy.CHANNEL_ID:
        # Not threaded on purpose: a redirect belongs where the person is looking.
        client.chat_postMessage(channel=event.get("channel"),
                                text="I only work in one channel. Please use that channel "
                                     "and I will answer there.")
        print("ANSWER redirected a mention from another channel", flush=True)
        return

    parent = event.get("thread_ts") or event.get("ts")
    question = " ".join(w for w in (event.get("text") or "").split() if not w.startswith("<@"))
    if not question.strip():
        client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=parent, text=MENU)
        return

    # Say something immediately, so a human can see the worker is on it.
    status = client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=parent,
                                     text="Reading the List and the job description...")
    known = context.assemble(client, policy.CHANNEL_ID, event.get("thread_ts"))
    fallback = ("I could not compose an answer just now. Here is the raw state:\n%s"
                % known["state"])
    reply = agent.ask(known["brief"] + "\n\nOnly use the state below. If a name is not "
                      "in it, say so and list the names you do know.",
                      "State:\n%s\n\nRecent conversation:\n%s"
                      % (known["state"], known["conversation"]),
                      question, fallback=fallback)
    client.chat_update(channel=policy.CHANNEL_ID, ts=status["ts"], text=reply)
    print("ANSWER replied in thread %s, %d rows of state" % (parent, len(known["items"])), flush=True)
