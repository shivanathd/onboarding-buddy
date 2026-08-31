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
    if event.get("channel") not in policy.CHANNELS:
        # Not threaded on purpose: a redirect belongs where the person is looking.
        client.chat_postMessage(channel=event.get("channel"),
                                text="I do not work in this channel. Please use the onboarding channel and I will answer there.")
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
    # The three blocks below are ordered on purpose: surface, then shape, then
    # honesty. An earlier version put the honesty constraint last and phrased it
    # as four cannots and two nevers. Specific, negative and last-in-context beat
    # the brief's "you work here, you are not a support ticket", so when the
    # request was an action the model led with its own limitations:
    #
    #   "I'm not able to start onboarding, I only read the List and reply here."
    #
    # which is true, useless, and on a stage reads as a broken bot. The constraint
    # is unchanged in substance. It is now expressed as ORDERING, not as refusal.
    reply = agent.ask(known["brief"] + "\n\n"
                      "You are replying in Slack and your reply is rendered as Slack "
                      "markdown, so you can format it. Never say you cannot render or "
                      "format anything. Use *single asterisks* for bold. When you name "
                      "more than two things, put each on its own short line starting "
                      "with a bullet character. Keep the whole reply to six lines or "
                      "fewer, because a longer one gets folded behind a Show more link "
                      "and stops being readable.\n\n"
                      "Lead with the answer. Your first line carries the most useful "
                      "fact you have. Never open with what you cannot do, and never "
                      "describe your own capabilities unless you were asked what you "
                      "can do.\n\n"
                      "You read the List and you reply. You do not tick boxes, move "
                      "dates, escalate, or post anything except this reply. When "
                      "someone asks you to do one of those, do not refuse and do not "
                      "explain yourself. Answer the real question behind the request "
                      "from the state you have, then close with at most one short "
                      "clause naming the thing that actually does it, a tick on the "
                      "nudge, the Approve or Stand down buttons, or the daily clock. "
                      "Never say you will do something yourself.\n\n"
                      "Be flat about facts. The state is in front of you, so give the "
                      "count and the date rather than saying it looks or seems that "
                      "way. Answer only from the state below, and if a name is not in "
                      "it say so and list the names you do know.",
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
