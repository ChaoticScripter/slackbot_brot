#==========================
# app/bot.py
#==========================

from slack_bolt import App
from db.db import Session
from db.models import Order, User
from dotenv import load_dotenv
import os

load_dotenv()

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)


@app.command("/order")
def handle_order(ack, respond, command):
    ack()
    text = command.get("text").strip()
    user_id = command["user_id"]
    session = Session()

    if text.startswith("add"):
        additions = text[4:].split(",")
        summary = []
        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            user = User(slack_id=user_id, name=user_id)
            session.add(user)
            session.commit()
        for item in additions:
            try:
                kind, amount = item.strip().split()
                order = session.query(Order).filter_by(user_id=user.id, item=kind).first()
                if order:
                    order.quantity += int(amount)
                else:
                    order = Order(user_id=user.id, item=kind, quantity=int(amount))
                    session.add(order)
                summary.append(f"• {amount}x {kind}")
            except Exception as e:
                respond(f"Fehler beim Parsen: `{item.strip()}` — {e}")
                session.rollback()
                return
        session.commit()
        updated_orders = session.query(Order).filter_by(user_id=user.id).all()

        # Verbesserte Formatierung
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Zur Bestellung hinzugefügt:*\n" + "\n".join(summary)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Deine aktuelle Bestellung:*\n" +
                            "\n".join([f"• {o.quantity}x {o.item}" for o in updated_orders])
                }
            }
        ]
        respond(blocks=blocks)
    session.close()