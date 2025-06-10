#==========================
# app/handlers/registration.py
#==========================

from db.db import Session
from db.models import User

def create_registration_blocks():
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Du bist nicht registriert. Gib deinen gewünschten Anzeigenamen ein und klicke auf 'Registrieren'."
            }
        },
        {
            "type": "input",
            "block_id": "name_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "display_name",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Dein Anzeigename"
                },
                "min_length": 1
            },
            "label": {
                "type": "plain_text",
                "text": "Anzeigename"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Jetzt registrieren",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": "register_user",
                    "value": "register_with_name"
                }
            ]
        }
    ]

def register_new_user(user_id, display_name, session):
    new_user = User(slack_id=user_id, name=display_name)
    session.add(new_user)
    session.commit()
    return new_user

def handle_register_action(ack, body, respond):
    ack()
    user_id = body["user"]["id"]
    display_name = body["state"]["values"]["name_input"]["display_name"]["value"]

    if not display_name:
        respond({
            "text": "Bitte gib einen Anzeigenamen ein.",
            "replace_original": True
        })
        return

    session = Session()
    try:
        user = register_new_user(user_id, display_name, session)
        respond({
            "text": f"Du hast dich erfolgreich mit dem Namen *{display_name}* in der Datenbank registriert! 🎉",
            "replace_original": True
        })
    except Exception as e:
        respond({
            "text": "Fehler bei der Registrierung. Bitte versuche es erneut.",
            "replace_original": True
        })
    finally:
        session.close()