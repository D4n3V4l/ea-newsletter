# Monday "How was your weekend?" greeting

An automated stand-in for the Monday-morning weekend check-in that Agnes used to
post by hand. Every Monday at **09:00 UK time** it posts one randomly chosen
variant of "How was your weekend?" to the `#social` Slack channel
(`C03G0AQ925P`).

## How it works

- **`.github/workflows/monday-weekend-greeting.yml`** — a scheduled GitHub
  Actions workflow. GitHub cron runs in UTC only, so it fires at both `08:00`
  and `09:00` UTC on Mondays.
- **`scripts/weekend_greeting.py`** — a dependency-free Python script (standard
  library only) that:
  1. Checks the current time in `Europe/London` and posts **only** during the 9
     o'clock hour, so exactly one of the two scheduled runs sends — correct
     under both GMT and BST, with no code changes needed at the DST switch.
  2. Picks a random greeting from a list of variants.
  3. Posts it to Slack via `chat.postMessage`.

## One-time setup

1. Create (or reuse) a Slack app with a **bot token** that has the
   `chat:write` scope.
2. Invite the bot to the target channel: `/invite @your-bot` in `#social`.
3. In the GitHub repo, add a repository secret named **`SLACK_BOT_TOKEN`**
   (Settings → Secrets and variables → Actions) containing the bot token
   (`xoxb-...`).

The channel ID is hard-coded as `SLACK_CHANNEL` in the workflow; change it there
if the message should go elsewhere.

## Testing / running manually

Trigger the workflow by hand from the Actions tab (**Run workflow**). Manual
`workflow_dispatch` runs bypass the 9am time check and always post, so you can
verify it end to end.

To dry-run locally:

```sh
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_CHANNEL="C03G0AQ925P"
export FORCE_SEND=1   # skip the "is it 9am in London?" check
python scripts/weekend_greeting.py
```

## Editing the greetings

Add or edit lines in the `GREETINGS` list in `scripts/weekend_greeting.py`.
Slack emoji shortcodes (e.g. `:sunny:`) render normally.
