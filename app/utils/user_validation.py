#==========================
# app/utils/user_validation.py
#==========================

from db.db import Session
from db.models import User
from app.handlers.name import create_registration_blocks

def check_user_registration(user_id, respond):
    """Überprüft ob ein User registriert ist und zeigt ggf. Registrierungsformular an"""
    session = Session()
    try:
        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            blocks = create_registration_blocks()
            respond(blocks=blocks)
            return None
        return user
    finally:
        session.close()