import sys
import pandas as pd
from datetime import datetime, timedelta
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ——————————————————————————————
# CONFIGURATION
# ——————————————————————————————

# Your Bot Token (make sure it has chat:write & conversations:write scopes)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

# Path to your schedule Excel
SCHEDULE_FILE = "AI Moment Schedule.xlsx"

# Map presenter names → their Slack USER IDs (e.g. "U1234ABCD")
slack_users = {
    "Julie":      "U8NGAL1M4",
    "Dana":       "U973L6ML7",
    "Bailey":     "U8QACFPGV",
    "Donna Lynn": "UFEEEPMUN",
    "Brian":      "U074A1X5V8B",
}

# Your Slack USER ID (not the DM channel). 
# Replace with your actual user ID (starts with U).
admin_user_id = "U05FNJETK99"

# ——————————————————————————————
# SCRIPT LOGIC
# ——————————————————————————————

def open_dm_and_post(user_id: str, text: str):
    """Open (or re-open) a DM and post `text` to it."""
    dm = client.conversations_open(users=[user_id])
    channel_id = dm["channel"]["id"]
    client.chat_postMessage(channel=channel_id, text=text)

def main():
    # Only run on Thursdays
    today = datetime.today().date()
    if today.weekday() != 3:  # 0=Mon, 3=Thu
        print("Today is not Thursday. Exiting.")
        return

    # Next Monday’s date
    next_monday = today + timedelta(days=(7 - today.weekday()))

    # Load schedule & find presenter
    df = pd.read_excel(SCHEDULE_FILE)
    row = df[df["Date"] == pd.Timestamp(next_monday)]
    if row.empty:
        print(f"No presenter found for {next_monday}")
        return

    presenter = row.iloc[0]["Presenter"]
    presenter_id = slack_users.get(presenter)

    if not presenter_id:
        # Notify admin if we can’t map the name
        err = f"⚠️ Could not find Slack USER ID for presenter: {presenter}"
        open_dm_and_post(admin_user_id, err)
        print(err)
        return

    # Compose messages
    reminder_msg = (
        f"👋 Hi {presenter}, just a friendly reminder that you're up to share in "
        f"Monday’s AI Moment on {next_monday.strftime('%B %d')}."
    )
    log_msg = f"✅ Reminder sent to {presenter} for {next_monday.strftime('%Y-%m-%d')}."

    try:
        # Send to presenter
        open_dm_and_post(presenter_id, reminder_msg)
        # Send log to admin
        open_dm_and_post(admin_user_id, log_msg)

    except SlackApiError as e:
        # Print and fail so your CI/action will catch it
        print("Slack API Error:", e.response["error"])
        sys.exit(1)

if __name__ == "__main__":
    main()
