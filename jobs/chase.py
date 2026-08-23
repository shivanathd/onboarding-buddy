"""chase

trigger: a daily cron at 09:00, or every 60 seconds in DEMO_MODE
reads:   the List. Status, Due and the Thread cell
writes:  the chase message ts into the Thread cell, via slackLists.items.update
surface: a new channel message tagging the owner
brain:   no for detection, yes only when drafting an escalation
"""

import datetime
import time

import policy
from jobs import approval
from tools import lists

def _seconds_past(due):
    """Detection is a subtraction. No judgement, no model, no surprises."""
    return (datetime.datetime.now()
            - datetime.datetime.combine(due, datetime.time.min)).total_seconds()


def run(client):
    """One shift. Nothing survives in memory between shifts: the Thread cell is
    the only record that a row has already been chased, and the cap is 10 new
    threads so one shift can never flood a room."""
    adapter = lists.lists_client(client)
    try:
        rows = lists.list_items(adapter, policy.LIST_ID)
    except Exception as problem:
        print("SHIFT aborted, the List read failed with %s" % problem, flush=True)
        return
    opened, past, no_due, held = 0, 0, 0, 0
    for item in rows:
        if lists.select_value(item, policy.COLUMNS["status"]) != policy.STATUS_OPEN.lower():
            continue
        due = lists.date_of(item, policy.COLUMNS["due"])
        if due is None:
            no_due += 1
            continue
        over = _seconds_past(due)
        if over <= policy.GRACE_SECONDS:
            continue
        past, days = past + 1, int(over // 86400)
        if lists.text_of(item, policy.COLUMNS["thread"]):
            continue  # already has a thread, nudge or escalation. One per row.
        if over > policy.ESCALATION_SECONDS:
            approval.open_for(client, adapter, item, days)
        elif opened >= policy.MAX_NEW_THREADS_PER_SHIFT:
            held += 1
        else:
            opened += 1
            step = lists.text_of(item, policy.COLUMNS["step"])
            owner = lists.first_user(item, policy.COLUMNS["owner"]) or policy.MANAGER_ID
            posted = client.chat_postMessage(channel=policy.CHANNEL_ID,
                                             text="Day %d: %s is still open. <@%s>, is this moving?"
                                                  % (days, step, owner))
            lists.update_cells(adapter, policy.LIST_ID, item["id"],
                               [{"column_id": policy.COLUMNS["thread"],
                                 "rich_text": lists.text_cell(posted["ts"])}])
            time.sleep(policy.SECONDS_BETWEEN_POSTS)  # one message per second per channel
    print("SHIFT scanned %d rows, %d past grace, %d threads opened, %d held, %d with no due date"
          % (len(rows), past, opened, held, no_due), flush=True)
