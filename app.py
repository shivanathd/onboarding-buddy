"""The worker. Three listeners, two clock lines, one socket. One worker on
shift at a time, because Slack load balances events across connections.
"""
import collections
import re

from apscheduler.schedulers.background import BackgroundScheduler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import policy
from jobs import advance, answer, approval, chase, report
from tools import context

app = App(token=policy.SLACK_BOT_TOKEN)
BOT_USER_ID = ""
MY_BOT_ID = ""
# {channel:thread -> turns} so a two-bot exchange cannot run away.
_handoffs = {}
# Event timestamps already dispatched, so the same message cannot be answered
# twice. Needed because app_mention and the message listener BOTH deliver a
# bot's channel mention: verified live, two near-identical replies 0.6s apart to
# one handoff. It also covers Slack's own event retries, which is why the guard
# lives here rather than being fixed by dropping one listener.
_seen = collections.OrderedDict()
_SEEN_MAX = 500


@app.event("app_mention")
def on_mention(event, client):
    _dispatch_mention(event, client)


# app_mention and a bot's channel mention: the behaviour is INTERMITTENT, so this
# worker listens on both paths and dedupes.
#
# First observation: an Agentforce agent posted a real bot_message with correct
# <@bot> markup and app_mention did not fire at all - no reply, no log line.
# That is why the message listener below was added.
# Second observation, same setup: BOTH fired, producing two near-identical
# replies 0.6s apart to one handoff.
#
# Do not "fix" this by deleting a listener. Keeping both plus the ts guard in
# _dispatch_mention is correct under either behaviour, and also absorbs Slack's
# event retries. Register the string "message", never "message.channels":
# Bolt's _verify_message_event_type raises on any type starting "message.".
@app.event("message")
def on_message(event, client):
    """Wake on a bot's mention. Everything app_mention gave for free is re-done
    here, because a message listener sees every message in every channel."""
    if event.get("subtype") not in (None, "bot_message"):
        return                                   # joins, edits, file shares
    author_bot = event.get("bot_id")
    if not author_bot:
        return                                   # humans already arrive via app_mention
    if author_bot == MY_BOT_ID:
        return                                   # never answer ourselves
    if BOT_USER_ID not in (event.get("text") or ""):
        return                                   # not addressed to us
    if policy.HANDOFF_BOT_IDS and author_bot not in policy.HANDOFF_BOT_IDS:
        print("MESSAGE ignored a mention from unlisted bot %s" % author_bot, flush=True)
        return                                   # allowlist, so only the deal desk can wake us
    # Loop guard. Two bots that can each mention the other will ping-pong for as
    # long as the room lets them, and nothing in the answer path rate limits
    # itself: MAX_NEW_THREADS_PER_SHIFT only caps chase.
    key = "%s:%s" % (event.get("channel"), event.get("thread_ts") or event.get("ts"))
    if _handoffs.get(key, 0) >= policy.MAX_HANDOFF_TURNS:
        print("MESSAGE loop guard stopped handoff %s" % key, flush=True)
        return
    _handoffs[key] = _handoffs.get(key, 0) + 1
    print("MESSAGE handoff from bot %s, turn %d" % (author_bot, _handoffs[key]), flush=True)
    _dispatch_mention(event, client)


def _dispatch_mention(event, client):
    # Both listeners land here, so this is the only place the guard has to be.
    key = "%s:%s" % (event.get("channel"), event.get("ts"))
    if key in _seen:
        print("DUPLICATE dropped a second delivery of %s" % key, flush=True)
        return
    _seen[key] = True
    while len(_seen) > _SEEN_MAX:
        _seen.popitem(last=False)   # bounded, so a long shift cannot grow it forever
    said = (event.get("text") or "").lower()
    if policy.REPORT_ON_MENTION and "run report" in said:
        report.run(client)
    elif "run chase" in said:
        # A manual trigger for the clock. The daily cron is the real path, but a
        # cron you cannot invoke is a cron you cannot demo, and waiting until
        # 09:00 in front of a room is not an option.
        #
        # Safe to call repeatedly: chase skips any row that already carries a
        # thread id, and MAX_NEW_THREADS_PER_SHIFT caps how many it opens. So a
        # second "run chase" with nothing newly past grace posts nothing at all.
        print("CHASE invoked by mention", flush=True)
        chase.run(client)
    else:
        answer.run(client, event, BOT_USER_ID)


@app.event("reaction_added")
def on_reaction(event, client):
    advance.run(client, event, BOT_USER_ID)


@app.action(re.compile("^obb_"))
def on_click(ack, body, client):
    ack()  # acknowledge the envelope first, always
    approval.decide(client, body["actions"][0], body["user"]["id"], body["message"]["ts"])


def start():
    gaps = policy.missing()
    if gaps:
        print("Not starting. These settings are empty: %s" % ", ".join(gaps), flush=True)
        return 1
    global BOT_USER_ID, MY_BOT_ID
    who = app.client.auth_test()
    BOT_USER_ID = who["user_id"]
    # Our own bot_id, so the message listener can tell our posts from another
    # bot's. Bolt's IgnoringSelfEvents already covers app_mention, but a plain
    # message listener sees everything and has to check for itself.
    MY_BOT_ID = who.get("bot_id") or ""
    clock = BackgroundScheduler(timezone=policy.TIMEZONE)
    # The two real cron lines. DEMO_MODE adds the compressed one underneath.
    clock.add_job(lambda: chase.run(app.client), "cron", hour=policy.CHASE_CRON_HOUR)
    clock.add_job(lambda: report.run(app.client), "cron", hour=policy.REPORT_CRON_HOUR,
                  day_of_week=policy.REPORT_CRON_DAY)
    if policy.DEMO_MODE:
        clock.add_job(lambda: chase.run(app.client), "interval", seconds=policy.CHASE_INTERVAL_SECONDS)
    clock.start()  # UNVERIFIED that this coexists with a socket, rehearsal check 5
    context.brief(app.client)  # read the brief once now, so a bad canvas shows up here
    # Door two. Imported here, not at module scope, so a missing MCP dependency
    # cannot stop the worker from taking its shift.
    try:
        from mcp_server import server as mcp_server
        mcp_server.start_in_background()
    except Exception as exc:
        print("MCP: not started (%s). Buddy runs on." % exc, flush=True)
    print("timezone %s, a container runs UTC unless you set TZ. %s\nworker on shift"
          % (policy.TIMEZONE, policy.clock_description()), flush=True)
    SocketModeHandler(app, policy.SLACK_APP_TOKEN).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(start())
