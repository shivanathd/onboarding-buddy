"""answer

trigger: a mention of the worker in the channel it knows
reads:   the List, then the brief, then the recent conversation
writes:  nothing
surface: a threaded reply, with a visible working status while it thinks
brain:   yes, with a template that carries the raw state when it fails
"""

import agent
import policy
from tools import blocks, context

MENU = ("I keep the onboarding List moving. Ask me where a step or a person "
        "stands, react with a tick to close a step, or say run report.")


def run(client, event, bot_user_id=""):
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
    # Strip only the worker's own mention. Anyone else named in the question is
    # the point of the question and has to survive.
    question = " ".join(w for w in (event.get("text") or "").split()
                        if bot_user_id not in w)
    if not question.strip():
        client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=parent, text=MENU)
        return

    # Show that the worker picked this up. Native indicator when the optional
    # scope is granted, otherwise a plain message we edit into the answer.
    native = blocks.thinking(client, policy.CHANNEL_ID, parent)
    status = None if native else client.chat_postMessage(
        channel=policy.CHANNEL_ID, thread_ts=parent, text="Reading the List...",
        blocks=[blocks.context(":hourglass_flowing_sand: Reading the List and the job "
                               "description...")])
    known = context.assemble(client, policy.CHANNEL_ID, event.get("thread_ts"))
    pretty = context.state_markdown(known["items"])
    fallback = ("I could not compose an answer just now. Here is the raw state:\n"
                + "\n".join(pretty))
    reply = agent.ask(known["brief"] + "\n\nAnswer in under forty words. One short "
                      "paragraph, never two. Only use the state below. If a name is "
                      "not in it, say so and list the names you do know.",
                      "State:\n%s\n\nRecent conversation:\n%s"
                      % (known["state"], known["conversation"]),
                      question, fallback=fallback)
    reply = context.mentionise(reply)
    body = [blocks.section(reply),
            blocks.context("Grounded in %d steps from the List" % len(known["items"]))]
    if native:
        blocks.thinking(client, policy.CHANNEL_ID, parent, on=False)
        client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=parent,
                                text=reply, blocks=body)
    else:
        client.chat_update(channel=policy.CHANNEL_ID, ts=status["ts"], text=reply, blocks=body)
    print("ANSWER replied in thread %s, %d rows of state" % (parent, len(known["items"])), flush=True)
