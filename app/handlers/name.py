#==========================
# app/handlers/name.py
#==========================

from db.db import Session
from db.models import User

def handle_name(ack, respond, command):
    ack()
    user_id = command["user_id"]
    text = command.get("text", "").strip()
    session = Session()

    try:
        if text.startswith("change"):
            new_name = text[len("change"):].strip()
            if not new_name:
                respond("Bitte gib einen neuen Namen an.")
                return

            user = session.query(User).filter_by(slack_id=user_id).first()
            if not user:
                respond("Du bist nicht registriert. Bitte melde dich zuerst an.")
                return

            user.name = new_name
            session.commit()
            respond(f"Dein Name wurde auf `{new_name}` aktualisiert!")
            return

        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            respond("Du bist nicht registriert. Bitte melde dich zuerst an.")
            return

        respond(f"Dein aktueller Name ist `{user.name}`.\n\nMit `/name change <neuer Name>` kannst du deinen Namen ändern.")

    finally:
        session.close()