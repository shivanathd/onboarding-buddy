"""advance

trigger: a white_check_mark reaction in the channel the worker knows
reads:   the List, matching the reacted message ts against the Thread cell
writes:  Status becomes Done
surface: one confirmation sentence in the same thread
brain:   yes

Your turn. Fill this in, restart the worker, and watch it come alive.
Compare with the finished version on the main branch when you get stuck.
"""


def run(client, event, bot_user_id):
    print("TODO advance is not built yet", flush=True)
