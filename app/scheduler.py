#==========================
# app/scheduler.py
#==========================

from apscheduler.schedulers.background import BackgroundScheduler
from slack_sdk import WebClient
from db.models import Session, Order, User
import datetime
import os

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
scheduler = BackgroundScheduler()

def send_reminders():
    session = Session()
    users = session.query(User).all()
    for user in users:
        if user.vacation == "on":
            continue
        orders = session.query(Order).filter_by(user_id=user.id).all()
        if not orders:
            continue
        msg = "> Deine Bestellung für Mittwoch:\n"
        for order in orders:
            msg += f"- {order.amount}x {order.kind}\n"
        client.chat_postMessage(channel=user.slack_id, text=msg)
    session.close()

    # Jeden Donnerstag um 14:00 Uhr Erinnerungen senden
    scheduler.add_job(send_reminders, "cron", day_of_week="thu", hour=14, minute=00)
    scheduler.start()