#==========================
# app/handlers/name.py
#==========================

from db.db import Session
from db.models import User
from app.utils.formatting import create_name_blocks
from app.handlers.registration import create_registration_blocks

def handle_name(ack, respond, command):
    ack()
    user_id = command["user_id"]
    text = command.get("text", "").strip()
    session = Session()

    try:
        user = session.query(User).filter_by(slack_id=user_id).first()

        if not user:
            blocks = create_registration_blocks()
            respond(blocks=blocks)
            return

        if text.startswith("change"):
            new_name = text[len("change"):].strip()
            if not new_name:
                respond("Bitte gib einen neuen Namen an.")
                return

            old_name = user.name
            user.name = new_name
            session.commit()

            blocks, attachments = create_name_blocks(current_name=old_name, new_name=new_name)
            respond(blocks=blocks, attachments=attachments)
            return

        blocks, attachments = create_name_blocks(current_name=user.name)
        respond(blocks=blocks, attachments=attachments)

    finally:
        session.close()