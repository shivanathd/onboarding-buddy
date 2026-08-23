"""advance

trigger: a white_check_mark reaction in the channel the worker knows
reads:   the List, matching the reacted message ts against the Thread cell
writes:  Status becomes Done, via slackLists.items.update
surface: one confirmation sentence in the same thread
brain:   yes for the sentence, with a template fallback that always works
"""

import agent
import policy
from tools import blocks, context, lists

def run(client, event, bot_user_id):
    """One emoji, one channel, one meaning. Everything else is ignored.

    UNVERIFIED whether reaction_added fires on the app's own messages, rehearsal
    check 2. A chase thread parent is a bot message, so this is the single most
    important thing the rehearsal has to prove.
    """
    item = event.get("item") or {}
    if (event.get("reaction") != policy.DONE_REACTION
            or item.get("channel") != policy.CHANNEL_ID
            or event.get("user") == bot_user_id):
        return

    adapter = lists.lists_client(client)
    rows = lists.list_items(adapter, policy.LIST_ID)
    match = lists.find_by_text(rows, policy.COLUMNS["thread"], item.get("ts"))
    if match is None:
        return  # people react to things all day. Silence is the right answer.

    step = lists.text_of(match, policy.COLUMNS["step"])
    hire = lists.first_user(match, policy.COLUMNS["hire"])
    if lists.select_value(match, policy.COLUMNS["status"]) == policy.STATUS_DONE.lower():
        print("ADVANCE already done, no-op for %s" % step, flush=True)
        return

    fallback = "Marked %s as done." % step
    try:
        lists.update_cells(adapter, policy.LIST_ID, match["id"],
                           [{"column_id": policy.COLUMNS["status"],
                             "select": [policy.STATUS_DONE.lower()]}])
    except Exception as problem:
        print("ADVANCE could not write the row for %s, %s" % (step, problem), flush=True)
        client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=item.get("ts"),
                                text="I saw the tick but could not write the List row. "
                                     "Try again, or edit the row directly.")
        return

    said = context.mentionise(
        agent.ask("Confirm a finished onboarding step in one short sentence.",
                  "step=%s hire=%s" % (step, context.mention(hire)), fallback) or fallback)
    client.chat_postMessage(channel=policy.CHANNEL_ID, thread_ts=item.get("ts"), text=said,
                            blocks=[blocks.section(":white_check_mark: " + said),
                                    blocks.context("Row updated in the List. The List is the "
                                                   "memory, not this thread.")])
    # Retire the parent. If it carried approve and stand down buttons, they must
    # not outlive the row they were asking about.
    try:
        client.chat_update(channel=policy.CHANNEL_ID, ts=item.get("ts"),
                           text="%s is done." % step,
                           blocks=[blocks.section(":white_check_mark: *%s* is done." % step),
                                   blocks.context("Closed by <@%s>. No decision needed."
                                                  % event.get("user"))])
    except Exception as problem:
        print("ADVANCE could not retire the parent message, %s" % problem, flush=True)
    print("ADVANCE %s is done, row ticked and parent retired" % step, flush=True)
