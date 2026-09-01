"""Boundaries you can read, not vibes in a prompt.

Every number the worker uses to decide something lives here, and every id it
needs comes from the environment. Nothing else in the repo reads configuration.

DEMO_MODE=true compresses the calendar so a live audience does not wait until
9am. The real values sit right next to the compressed ones on purpose.
"""

import os
import pathlib

# The worker loads .env itself so that `python app.py` just works. setdefault
# means a real environment variable always wins, which is how Railway behaves.
# An empty value counts as unset, so a half filled .env cannot mask a real one.
_ENV_FILE = pathlib.Path(__file__).with_name(".env")
if _ENV_FILE.is_file():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _value = _line.split("=", 1)
        _value = _value.strip().strip(chr(34)).strip(chr(39))
        if _value:
            os.environ.setdefault(_key.strip(), _value)


def _flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


DEMO_MODE = _flag("DEMO_MODE")

# How long past its due date a step may sit before the worker says something.
GRACE_SECONDS = 120 if DEMO_MODE else 2 * 24 * 60 * 60

# How long past due before the worker stops nudging and asks a human instead.
# This is NOT compressed by DEMO_MODE. If it were, every row due yesterday would
# already be past it, and the plain nudge would never be seen.
ESCALATION_SECONDS = 5 * 24 * 60 * 60

# How much air an approved extension buys.
EXTENSION_DAYS = 3

# The clock. In production these are two cron lines. DEMO_MODE swaps chase onto
# a short interval and lets a mention trigger the report on demand.
CHASE_CRON_HOUR = 9
REPORT_CRON_HOUR = 9
REPORT_CRON_DAY = "mon"
CHASE_INTERVAL_SECONDS = 60 if DEMO_MODE else 0
# Asking for the report always works. It is read only, writes nothing and calls
# no model, so there was nothing to protect. Gating it behind DEMO_MODE only
# produced a confusing silence: you asked for a report and got a chatty answer.
REPORT_ON_MENTION = True

# Politeness limits. chat.postMessage allows about one message per second to a
# channel, and no single shift should ever flood a room.
MAX_NEW_THREADS_PER_SHIFT = 10
SECONDS_BETWEEN_POSTS = 1

# Status values, matching the select options bootstrap.py creates.
STATUS_OPEN = "Open"
STATUS_DONE = "Done"
STATUS_ESCALATED = "Escalated"

# The select column stores lowercase option values and shows these labels.
# bootstrap.py creates the column with exactly this mapping.
STATUS_LABELS = {"open": STATUS_OPEN, "done": STATUS_DONE, "escalated": STATUS_ESCALATED}

DONE_REACTION = "white_check_mark"

# Channels the worker will answer in. CHANNEL_ID stays the single primary channel
# it posts reports and chases to; CHANNELS is the set it will *answer* in, so a
# demo can run in the Salesforce record channel without silencing the original.
CHANNELS = {c.strip() for c in os.environ.get("CHANNEL_ID", "").split(",") if c.strip()}

# Only these bot ids may wake the worker by mentioning it in a channel. Empty
# means allow any bot, which is fine for a demo but not for a shared workspace.
HANDOFF_BOT_IDS = {b.strip() for b in os.environ.get("HANDOFF_BOT_IDS", "").split(",") if b.strip()}

# The Slack user id of the Agentforce agent in this channel. The worker cannot
# touch Salesforce and never will, so when someone asks it to move a deal it
# hands the ask to whoever can. Empty means there is no such agent here and the
# worker simply says what it cannot do, which is the old behaviour.
AGENTFORCE_USER_ID = os.environ.get("AGENTFORCE_USER_ID", "").strip()

# How many times one bot-to-bot thread may bounce before the worker stops.
MAX_HANDOFF_TURNS = int(os.environ.get("MAX_HANDOFF_TURNS", "2"))

# Ids and secrets. No defaults, no literals in code. app.py checks these at boot
# and refuses to start half configured.
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").split(",")[0].strip()
MANAGER_ID = os.environ.get("MANAGER_ID", "")
CANVAS_FILE_ID = os.environ.get("CANVAS_FILE_ID", "")
LIST_ID = os.environ.get("LIST_ID", "")
TIMEZONE = os.environ.get("TZ", "") or "UTC"

# Column ids. Opaque by nature, which is why bootstrap.py prints the mapping.
COLUMNS = {
    "step": os.environ.get("COL_STEP", ""),
    "hire": os.environ.get("COL_HIRE", ""),
    "owner": os.environ.get("COL_OWNER", ""),
    "due": os.environ.get("COL_DUE", ""),
    "status": os.environ.get("COL_STATUS", ""),
    "thread": os.environ.get("COL_THREAD", ""),
}

# What must be present before the worker will start a shift.
REQUIRED = (
    "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "CHANNEL_ID", "MANAGER_ID",
    "LIST_ID", "COL_STEP", "COL_HIRE", "COL_OWNER", "COL_DUE",
    "COL_STATUS", "COL_THREAD",
)


def missing():
    """Names of required settings that are still empty."""
    return [name for name in REQUIRED if not os.environ.get(name, "").strip()]


def clock_description():
    """One line for the boot log, so the room can see which clock is running."""
    if DEMO_MODE:
        return ("DEMO_MODE on: grace %ds, chase every %ds. Escalation still %d days, "
                "uncompressed. The report answers whenever asked."
                % (GRACE_SECONDS, CHASE_INTERVAL_SECONDS, ESCALATION_SECONDS // 86400))
    return ("DEMO_MODE off: grace %d days, escalation %d days, chase daily at "
            "%02d:00, report Mondays %02d:00" % (GRACE_SECONDS // 86400,
                                                 ESCALATION_SECONDS // 86400,
                                                 CHASE_CRON_HOUR, REPORT_CRON_HOUR))
