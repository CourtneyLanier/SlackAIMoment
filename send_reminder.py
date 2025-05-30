import pandas as pd
from datetime import datetime, timedelta
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load schedule
df = pd.read_excel("AI Moment Schedule.xlsx")

# Get today and next Monday
today = datetime.today().date()
next_monday = today + timedelta(days=(7 - today.weekday())) if today.weekday() == 3 else None  # Only if today is Thursday

if next_monday:
    presenter_row = df[df['Date'] == pd.Timestamp(next_monday)]
    if not presenter_row.empty:
        presenter_name = presenter_row.iloc[0]['Presenter']
        slack_users = {
            "Julie": "@julie",
            "Dana": "@dana",
            "Donna Lynn": "@donnalynn",
            "Bailey": "@bailey",
            "Brian": "@brian",
            # Add others as needed
        }
        message = f"Hi {presenter_name}, just a reminder that you're up to share in Monday's AI Moment!"
        slack_user = slack_users.get(presenter_name, None)

        if slack_user:
            client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
            try:
                response = client.chat_postMessage(channel=slack_user, text=message)
                print("Message sent:", response["ts"])
            except SlackApiError as e:
                print("Slack API Error:", e.response["error"])
        else:
            print(f"No Slack username found for {presenter_name}")
    else:
        print("No presenter scheduled for next Monday.")
else:
    print("Today is not Thursday. Exiting.")
