#!/usr/bin/env python3
"""Post a random "How was your weekend?" greeting to Slack on Monday mornings.

Runs from a GitHub Actions cron schedule. GitHub Actions cron is always in UTC,
so the workflow fires at both 08:00 and 09:00 UTC on Mondays; this script only
actually posts when the current time in Europe/London is the 09:xx hour, so
exactly one of the two runs sends regardless of British Summer Time.
"""
import json
import os
import random
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

GREETINGS = [
    "Morning all! :sunny: How was your weekend?",
    "Happy Monday! Get up to anything good this weekend?",
    "Hope everyone had a lovely weekend — what were the highlights?",
    "New week, fresh start. :seedling: How did you spend your weekend?",
    "Morning team! Did the weekend treat you well?",
    "Back at it! :muscle: What's one good thing from your weekend?",
    "Hey everyone — how were the last couple of days? Anything fun?",
    "Monday's here again. :coffee: How was everyone's weekend?",
    "Hope you all got some proper rest this weekend! What did you get up to?",
    "Good morning! :partly_sunny: Tell me something nice that happened over the weekend.",
    "Happy Monday, folks! Weekend wins — let's hear 'em.",
    "Morning! Recharged and ready? How was the weekend?",
]

SLACK_API_URL = "https://slack.com/api/chat.postMessage"


def within_send_window() -> bool:
    """True if it is the 9 o'clock hour in London, or if sending is forced."""
    if os.environ.get("FORCE_SEND") == "1":
        return True
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return True
    now_london = datetime.now(ZoneInfo("Europe/London"))
    return now_london.hour == 9


def main() -> int:
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL")
    if not token or not channel:
        print("SLACK_BOT_TOKEN and SLACK_CHANNEL must be set", file=sys.stderr)
        return 1

    if not within_send_window():
        now_london = datetime.now(ZoneInfo("Europe/London"))
        print(f"Not the 9am hour in London (currently {now_london:%H:%M %Z}); skipping.")
        return 0

    text = random.choice(GREETINGS)
    payload = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"Failed to reach Slack: {exc}", file=sys.stderr)
        return 1

    if not body.get("ok"):
        print(f"Slack API error: {body.get('error')}", file=sys.stderr)
        return 1

    print(f"Posted to {channel}: {text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
