import pandas as pd
from datetime import datetime, timedelta
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

# Map presenter names to Slack user IDs
slack_users = {
    "Julie":      "U8NGAL1M4",
    "Dana":       "U973L6ML7",
    "Bailey":     "U8QACFPGV",
    "Donna Lynn": "UFEEEPMUN",
    "Brian":      "U074A1X5V8B",
}

# Your Slack user ID (not @handle)
admin_user_id = "U05FNJETK99"  # Replace with your real user ID if different

# Load presenter schedule
df = pd.read_excel("AI Moment Schedule.xlsx")

# Check if today is Thursday
today = datetime.today().date()
if today.weekday() != 3:
    print("Today is not Thursday. Exiting.")
    exit()

# Find the upcoming Monday
next_monday = today + timedelta(days=(7 - today.weekday()))

# Find the presenter for that Monday
row = df[df["Date"] == pd.Timestamp(next_monday)]
if row.empty:
    print(f"No presenter found for {next_monday}")
    exit()

presenter = row.iloc[0]["Presenter"]
presenter_id = slack_users.get(presenter)

# Function to find existing DM channel (no need for conversations.open)
def find_existing_dm_channel(user_id):
    try:
        result = client.conversations_list(types="im")
        for channel in result["channels"]:
            if channel.get("user") == user_id:
                return channel["id"]
    except SlackApiError as e:
        print("Error listing conversations:", e.response["error"])
    return None

# Compose the message
reminder_msg = f"👋 Hi {presenter}, just a friendly reminder that you're up to share in Monday’s AI Moment on {next_monday.strftime('%B %d')}."
log_msg = f"✅ Reminder sent to {presenter} for {next_monday.strftime('%Y-%m-%d')}."
error_msg = f"⚠️ Could not send reminder — no existing DM channel found for: {presenter}"

if presenter_id:
    dm_channel = find_existing_dm_channel(presenter_id)

    if dm_channel:
        try:
            # Send reminder
            client.chat_postMessage(channel=dm_channel, text=reminder_msg)
            # Send confirmation to admin
            client.chat_postMessage(channel=admin_user_id, text=log_msg)
            print(log_msg)
        except SlackApiError as e:
            print("Slack API Error:", e.response["error"])
    else:
        # No existing DM channel
        client.chat_postMessage(channel=admin_user_id, text=error_msg)
        print(error_msg)
else:
    # Unknown presenter
    fallback = f"⚠️ Presenter '{presenter}' not found in Slack user map."
    client.chat_postMessage(channel=admin_user_id, text=fallback)
    print(fallback)
