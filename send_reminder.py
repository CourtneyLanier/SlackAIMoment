import pandas as pd
from datetime import datetime, timedelta
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

# Load presenter schedule
df = pd.read_excel("AI Moment Schedule.xlsx")

# Check if today is Thursday
today = datetime.today().date()
if today.weekday() != 3:
    print("Today is not Thursday. Exiting.")
    exit()

# Find the upcoming Monday
next_monday = today + timedelta(days=(7 - today.weekday()))  # 0=Monday, 3=Thursday

# Find the presenter for that Monday
row = df[df["Date"] == pd.Timestamp(next_monday)]
if row.empty:
    print(f"No presenter found for {next_monday}")
    exit()

presenter = row.iloc[0]["Presenter"]

# Map presenter names to Slack usernames (update as needed)
slack_users = {
    "Julie": "@julieh",
    "Dana": "@Dana",
    "Donna Lynn": "@DonnaLynn",
    "Bailey": "@Bailey Dawson",
    "Brian": "@Brian Huang"
}

# Your Slack handle to send log message to
admin_user = "@Courtney"

# Compose and send the reminder
presenter_handle = slack_users.get(presenter)
reminder_msg = f"👋 Hi {presenter}, just a friendly reminder that you're up to share in Monday’s AI Moment on {next_monday.strftime('%B %d')}."

if presenter_handle:
    try:
        # Send reminder to presenter
        client.chat_postMessage(channel=presenter_handle, text=reminder_msg)

        # Log message to you
        log_msg = f"✅ Reminder sent to {presenter} for {next_monday.strftime('%Y-%m-%d')}."
        client.chat_postMessage(channel=admin_user, text=log_msg)

    except SlackApiError as e:
        print("Slack API Error:", e.response["error"])
else:
    # If user not found, notify you
    error_msg = f"⚠️ Could not find Slack handle for presenter: {presenter}"
    client.chat_postMessage(channel=admin_user, text=error_msg)
    print(error_msg)
