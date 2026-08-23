"""approval

trigger: chase finds a row past the escalation threshold, then a human clicks
reads:   the List and the stuck thread
writes:  Due extended on approve, Status becomes Escalated on stand down
surface: a channel message carrying two buttons, then a reply in the thread
brain:   yes for the wording, never for the decision
"""

import datetime

import agent
import policy
from tools import context, lists

APPROVE, DENY = "obb_approve", "obb_stand_down"
def _button(action_id, label, row_id, style=None):
    button = {"type": "button", "action_id": action_id, "value": row_id,
              "text": {"type": "plain_text", "text": label}}
    return dict(button, style=style) if style else button


def open_for(client, adapter, item, days_over):
    """Ask a human. The worker proposes, a human disposes, and the thread is the
    paper trail. One open approval per row, per APR-5."""
    if (lists.select_value(item, policy.COLUMNS["status"]) == policy.STATUS_ESCALATED.lower()
            or lists.text_of(item, policy.COLUMNS["thread"])):
        return  # already escalated, or a thread is already open on this row
    step = lists.text_of(item, policy.COLUMNS["step"])
    thread = lists.text_of(item, policy.COLUMNS["thread"])
    said = "\n".join(context.thread_replies(client, policy.CHANNEL_ID, thread)) if thread else ""
    draft = agent.ask("Say what is blocking this step. Two sentences at most, plain "
                      "words, no preamble and no hedging.",
                      "step=%s days past grace=%d\nthread:\n%s" % (step, days_over, said),
                      "What is blocking it?",
                      fallback="Escalation: %s is %d days past grace and I could not read a "
                               "reason from the thread." % (step, days_over))
    posted = client.chat_postMessage(
        channel=policy.CHANNEL_ID, text="Escalation for %s" % step,
        blocks=[{"type": "section", "text": {"type": "mrkdwn",
                                             "text": "<@%s> %s" % (policy.MANAGER_ID, draft)}},
                {"type": "actions", "elements": [
                    _button(APPROVE, "Approve extension", item["id"], "primary"),
                    _button(DENY, "Stand down", item["id"])]}])
    lists.update_cells(adapter, policy.LIST_ID, item["id"],
                       [{"column_id": policy.COLUMNS["thread"],
                         "rich_text": lists.text_cell(posted["ts"])}])
    print("ESCALATE %s is %d days past grace, buttons posted for a human"
          % (step, days_over), flush=True)


def decide(client, action, clicker, message_ts):
    """Act on the click. UNVERIFIED how reliably the original message can be
    updated after a click over Socket Mode, rehearsal check 10."""
    adapter = lists.lists_client(client)
    rows = lists.list_items(adapter, policy.LIST_ID)
    item = next((r for r in rows if r["id"] == action["value"]), None)
    if item is None:
        return
    step = lists.text_of(item, policy.COLUMNS["step"])
    if action["action_id"] == APPROVE:
        due = (lists.date_of(item, policy.COLUMNS["due"]) or datetime.date.today()
               ) + datetime.timedelta(days=policy.EXTENSION_DAYS)
        cells = [{"column_id": policy.COLUMNS["due"], "date": lists.date_cell(due)}]
        said = "<@%s> approved an extension on %s. New due date %s." % (clicker, step, due)
    else:
        cells = [{"column_id": policy.COLUMNS["status"],
                  "select": [policy.STATUS_ESCALATED.lower()]}]
        said = "<@%s> chose to stand down on %s." % (clicker, step)
    try:
        lists.update_cells(adapter, policy.LIST_ID, item["id"], cells)
    except Exception as problem:
        client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=message_ts,
                                text="I could not write the row, so nothing changed. %s" % problem)
        return
    client.chat_update(channel=policy.CHANNEL_ID, ts=message_ts, text=said,
                       blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": said}}])
    print("DECIDED %s on %s by %s" % (action["action_id"], step, clicker), flush=True)
