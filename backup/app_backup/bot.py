#==========================
# app/slack_bot_init.py
#==========================

from slack_bolt import App
import os
from app.handlers.order import handle_order_add
from app.handlers.name import handle_name
from app.handlers.help import handle_help
from app.handlers.homeMenu import handle_app_home_opened
from app.handlers.registration import handle_register_action
from app.handlers.admin import handle_admin_command
from db.db import Session
from db.models import Product
from app.handlers.admin import check_admin
from app.utils.constants import ADMIN_ERROR_MESSAGES

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

@app.command("/help")
def help_command(ack, respond):
    handle_help(ack, respond)

@app.command("/name")
def name_command(ack, respond, command):
    handle_name(ack, respond, command)

@app.command("/order")
def order_command(ack, respond, command):
    ack()
    text = command.get("text", "").strip()

    if not text:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ Bitte gib einen gültigen Befehl ein.\nVerwende `/help` um alle verfügbaren Befehle anzuzeigen."
                }
            }
        ]
        respond(blocks=blocks)
        return

    if text == "add":
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ Bitte gib mindestens ein Produkt mit Menge an.\nBeispiel: `/order add normal 2, vollkorn 1`"
                }
            }
        ]
        respond(blocks=blocks)
        return

    if text.startswith("add"):
        handle_order_add(ack, respond, command)

    if text.startswith("admin"):
        handle_admin_command(ack, respond, command)
        return

@app.event("app_home_opened")
def app_home_opened_handler(client, event, logger):
    handle_app_home_opened(client, event, logger)

@app.action("register_user")
def register_action(ack, body, respond):
    handle_register_action(ack, body, respond)

@app.action("admin_product_add_confirm")
def handle_admin_product_add_confirm(ack, body, respond):
    ack()
    user = check_admin(body["user"]["id"], respond)
    if not user:
        return

    value = body["actions"][0]["value"]
    name, description = value.split("|")

    session = Session()
    try:
        new_product = Product(name=name, description=description if description else None)
        session.add(new_product)
        session.commit()
        respond({
            "text": f"✅ Produkt *{name}* wurde erfolgreich hinzugefügt!",
            "replace_original": True
        })
    except Exception as e:
        respond({
            "text": ADMIN_ERROR_MESSAGES["DB_ERROR"],
            "replace_original": True
        })
    finally:
        session.close()

@app.action("admin_product_delete_confirm")
def handle_admin_product_delete_confirm(ack, body, respond):
    ack()
    user = check_admin(body["user"]["id"], respond)
    if not user:
        return

    product_name = body["actions"][0]["value"]
    session = Session()
    try:
        product = session.query(Product).filter_by(name=product_name).first()
        if not product:
            respond({
                "text": ADMIN_ERROR_MESSAGES["PRODUCT_NOT_FOUND"].format(product=product_name),
                "replace_original": True
            })
            return

        session.delete(product)
        session.commit()
        respond({
            "text": f"❌ Produkt *{product_name}* wurde erfolgreich gelöscht!",
            "replace_original": True
        })
    except Exception as e:
        respond({
            "text": ADMIN_ERROR_MESSAGES["DB_ERROR"],
            "replace_original": True
        })
    finally:
        session.close()

@app.action("admin_product_activate_confirm")
def handle_admin_product_activate_confirm(ack, body, respond):
    ack()
    user = check_admin(body["user"]["id"], respond)
    if not user:
        return

    product_name = body["actions"][0]["value"]
    session = Session()
    try:
        product = session.query(Product).filter_by(name=product_name).first()
        if not product:
            respond({
                "text": ADMIN_ERROR_MESSAGES["PRODUCT_NOT_FOUND"].format(product=product_name),
                "replace_original": True
            })
            return

        product.active = True
        session.commit()
        respond({
            "text": f"✅ Produkt *{product_name}* wurde erfolgreich aktiviert!",
            "replace_original": True
        })
    except Exception as e:
        respond({
            "text": ADMIN_ERROR_MESSAGES["DB_ERROR"],
            "replace_original": True
        })
    finally:
        session.close()

@app.action("admin_product_deactivate_confirm")
def handle_admin_product_deactivate_confirm(ack, body, respond):
    ack()
    user = check_admin(body["user"]["id"], respond)
    if not user:
        return

    product_name = body["actions"][0]["value"]
    session = Session()
    try:
        product = session.query(Product).filter_by(name=product_name).first()
        if not product:
            respond({
                "text": ADMIN_ERROR_MESSAGES["PRODUCT_NOT_FOUND"].format(product=product_name),
                "replace_original": True
            })
            return

        product.active = False
        session.commit()
        respond({
            "text": f"❌ Produkt *{product_name}* wurde erfolgreich deaktiviert!",
            "replace_original": True
        })
    except Exception as e:
        respond({
            "text": ADMIN_ERROR_MESSAGES["DB_ERROR"],
            "replace_original": True
        })
    finally:
        session.close()

@app.action("admin_product_add_cancel")
@app.action("admin_product_delete_cancel")
@app.action("admin_product_activate_cancel")
@app.action("admin_product_deactivate_cancel")
def handle_admin_product_cancel(ack, respond):
    ack()
    respond({
        "text": "❌ Aktion abgebrochen.",
        "replace_original": True
    })

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")