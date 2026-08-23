"""The worker. Three listeners, two clock lines, one socket. One worker on
shift at a time, because Slack load balances events across connections.
"""
import re

from apscheduler.schedulers.background import BackgroundScheduler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import policy
from jobs import advance, answer, approval, chase, report

app = App(token=policy.SLACK_BOT_TOKEN)
BOT_USER_ID = ""


@app.event("app_mention")
def on_mention(event, client):
    if policy.REPORT_ON_MENTION and "run report" in (event.get("text") or "").lower():
        report.run(client)
    else:
        answer.run(client, event)


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
    global BOT_USER_ID
    BOT_USER_ID = app.client.auth_test()["user_id"]
    clock = BackgroundScheduler(timezone=policy.TIMEZONE)
    # The two real cron lines. DEMO_MODE adds the compressed one underneath.
    clock.add_job(lambda: chase.run(app.client), "cron", hour=policy.CHASE_CRON_HOUR)
    clock.add_job(lambda: report.run(app.client), "cron", hour=policy.REPORT_CRON_HOUR,
                  day_of_week=policy.REPORT_CRON_DAY)
    if policy.DEMO_MODE:
        clock.add_job(lambda: chase.run(app.client), "interval",
                      seconds=policy.CHASE_INTERVAL_SECONDS)
    clock.start()  # UNVERIFIED that this coexists with a socket, rehearsal check 5
    print("timezone %s, a container runs UTC unless you set TZ. %s"
          % (policy.TIMEZONE, policy.clock_description()), flush=True)
    print("worker on shift", flush=True)
    SocketModeHandler(app, policy.SLACK_APP_TOKEN).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(start())
