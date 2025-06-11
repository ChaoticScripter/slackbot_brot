#==========================
# app/utils/slack.py
#==========================

from slack_sdk import WebClient
from datetime import datetime, timedelta

def get_slack_user_info(user_id, token):
    client = WebClient(token=token)
    try:
        result = client.users_info(user=user_id)
        return result["user"]["profile"]["display_name"] or result["user"]["real_name"]
    except Exception:
        return user_id

def get_current_order_period():
    now = datetime.now()
    current_wednesday = now
    while current_wednesday.weekday() != 2:
        current_wednesday -= timedelta(days=1)
    current_wednesday = current_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

    if now < current_wednesday:
        current_wednesday -= timedelta(days=7)

    next_wednesday = current_wednesday + timedelta(days=7)
    next_wednesday = next_wednesday.replace(hour=9, minute=59, second=59)

    return current_wednesday, next_wednesday