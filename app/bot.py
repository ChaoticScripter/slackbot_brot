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
            user = User(slack_id=user_id)
            session.add(user)
            session.commit()
        for item in additions:
            try:
                kind, amount = item.strip().split()
                order = session.query(Order).filter_by(user_id=user.id, kind=kind).first()
                if order:
                    order.amount += int(amount)
                else:
                    order = Order(user_id=user.id, kind=kind, amount=int(amount))
                    session.add(order)
                summary.append(f"{amount}x {kind}")
            except Exception as e:
                respond(f"Fehler beim Parsen: `{item.strip()}` — {e}")
                session.rollback()
                return
        session.commit()
        updated_orders = session.query(Order).filter_by(user_id=user.id).all()
        lines = "\n".join([f"|{o.amount:^5}|{o.kind:^20}|" for o in updated_orders])
        respond(f"""> **Zur Bestellung wird folgendes hinzugefügt:**\n{chr(10)}""" +
                f"> {chr(10).join(summary)}\n\n" +
                "> **Deine aktualisierte Bestellung sieht wie folgt aus:**\n" +
                "```|Anzahl|Typ|\n|:--:|:--------------------:|\n" + lines + "\n```")
    session.close()
