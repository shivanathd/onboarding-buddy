# Provisioning without a browser

Everything below was done from a terminal. No clicking, which matters if you
want any of this to be repeatable, scriptable, or runnable on a machine with no
screen.

## The command line tool signs in without a browser

The Slack command line tool supports a two step sign in. Ask for a ticket, and
it prints a slash command. Run that slash command in any Slack channel, approve
the modal, and Slack shows a short challenge code. Feed the ticket and the code
back and the session is stored.

    slack auth login --no-prompt
    slack auth login --ticket <ticket> --challenge <code>

That is the only human step in the whole chain, and it happens once.

## One undocumented call returns every token you need

The tool has no command for creating tokens, but tracing what it does while
running an app reveals a single call that returns all three: the bot token, a
user token, and the app level token needed for a socket connection.

    POST https://slack.com/api/apps.developerInstall
    Authorization: Bearer <configuration token>
    Content-Type: application/json
    {"app_id": "...", "bot_scopes": [...], "user_scopes": [...]}

Two things to know. It only grants scopes the app manifest already declares, so
the sequence is always update the manifest first, then install. And it grants
additively: reinstalling with fewer scopes does not take the old ones away.

This is not a documented endpoint. It can change without notice. It is
excellent for a scripted test environment and it is not something to build a
product on, which is why the quickstart in the main README teaches the ordinary
route through the app settings pages instead.

## App level scopes are not a manifest concept

A manifest may carry an app level scope entry, and Slack will accept the
document, but round tripping it shows the entry has been dropped. The socket
connection scope has to be granted where app level tokens are created. Any
guide that tells you to put it in a manifest is wrong, including an earlier
draft of ours.

## Everything else is ordinary API calls

Creating the channel, creating and seeding the List, creating the canvas that
holds the job description, and resolving user ids were all normal calls with a
temporary scope grant, immediately handed back afterwards. The worker itself
runs with only the eight scopes documented in the README, so the demo runs on
exactly the permissions the reader gets.
