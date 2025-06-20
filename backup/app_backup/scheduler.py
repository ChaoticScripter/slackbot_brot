#==========================
# app/reminder_jobs.py
#==========================

from apscheduler.schedulers.background import BackgroundScheduler
from slack_sdk import WebClient
from db.db import Session
from db.models import Order, User
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_slack_client() -> Optional[WebClient]:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        logger.error("SLACK_BOT_TOKEN nicht gefunden")
        return None
    return WebClient(token=token)


def send_reminders():
    client = get_slack_client()
    if not client:
        return

    session = Session()
    try:
        users = session.query(User).all()
        for user in users:
            if user.is_on_vacation:
                continue

            orders = session.query(Order).filter_by(user_id=user.id).all()
            if not orders:
                continue

            order_items = [f"• {order.quantity}x {order.item}" for order in orders]

            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🥨 *Erinnerung: Deine Brötchenbestellung*"
                    }
                }
            ]

            attachments = [
                {
                    "color": "#f2c744",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Deine aktuelle Bestellung für Mittwoch:*\n" + "\n".join(order_items)
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "Änderungen können mit `/order` vorgenommen werden"
                                }
                            ]
                        }
                    ]
                }
            ]

            try:
                client.chat_postMessage(
                    channel=user.slack_id,
                    blocks=blocks,
                    attachments=attachments
                )
            except Exception as e:
                logger.error(f"Fehler beim Senden der Nachricht an {user.slack_id}: {e}")

    except Exception as e:
        logger.error(f"Fehler in send_reminders: {e}")
    finally:
        session.close()


def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, "cron", day_of_week="tue", hour=13, minute=2)
    scheduler.start()
    return scheduler