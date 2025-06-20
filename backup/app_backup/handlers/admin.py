#==========================
# app/handlers/admin.py
#==========================

from typing import Optional, Dict, Any, List
from db.db import Session
from db.models import User, Product
from app.utils.constants import ADMIN_ERROR_MESSAGES, ADMIN_COMMANDS, ADMIN_HELP_TEXTS
from app.utils.admin_formatting import create_product_confirmation_blocks, create_product_status_blocks

def check_admin(user_id: str, respond: callable) -> Optional[User]:
    session = Session()
    try:
        user = session.query(User).filter_by(slack_id=user_id, is_admin=True).first()
        if not user:
            respond(ADMIN_ERROR_MESSAGES["NOT_ADMIN"])
            return None
        return user
    finally:
        session.close()

def handle_admin_command(ack: callable, respond: callable, command: Dict[str, Any]) -> None:
    ack()
    user = check_admin(command["user_id"], respond)
    if not user:
        return

    text = command.get("text", "").strip()
    if not text.startswith("admin"):
        respond(ADMIN_ERROR_MESSAGES["INVALID_FORMAT"])
        return

    args = text.split()[1:]  # "admin" entfernen
    if not args:
        respond(ADMIN_ERROR_MESSAGES["INVALID_FORMAT"])
        return

    subcommand = args[0]
    remaining_args = args[1:]

    # Admin-Hilfefunktion
    if subcommand == ADMIN_COMMANDS["HELP"]:
        respond(ADMIN_HELP_TEXTS["GENERAL"])
        return

    # Andere Admin-Befehle
    if subcommand == ADMIN_COMMANDS["PRODUCT_ADD"]:
        handle_product_add(respond, remaining_args)
    elif subcommand == ADMIN_COMMANDS["PRODUCT_DELETE"]:
        handle_product_delete(respond, remaining_args)
    elif subcommand == ADMIN_COMMANDS["PRODUCT_ACTIVATE"]:
        handle_product_status(respond, remaining_args, True)
    elif subcommand == ADMIN_COMMANDS["PRODUCT_DEACTIVATE"]:
        handle_product_status(respond, remaining_args, False)
    elif subcommand == ADMIN_COMMANDS["PRODUCT_LIST"]:
        handle_product_list(respond)
    else:
        respond(ADMIN_ERROR_MESSAGES["INVALID_FORMAT"])

def handle_product_add(respond: callable, args: List[str]) -> None:
    if not args:
        respond(ADMIN_ERROR_MESSAGES["MISSING_PRODUCT_NAME"])
        return

    name = args[0]
    description = " ".join(args[1:]) if len(args) > 1 else None

    session = Session()
    try:
        existing_product = session.query(Product).filter_by(name=name).first()
        if existing_product:
            respond(ADMIN_ERROR_MESSAGES["PRODUCT_EXISTS"].format(product=name))
            return

        blocks = create_product_confirmation_blocks("add", name, description)
        respond(blocks=blocks)
    finally:
        session.close()

def handle_product_delete(respond: callable, args: List[str]) -> None:
    if not args:
        respond(ADMIN_ERROR_MESSAGES["MISSING_PRODUCT_NAME"])
        return

    name = args[0]
    session = Session()
    try:
        product = session.query(Product).filter_by(name=name).first()
        if not product:
            respond(ADMIN_ERROR_MESSAGES["PRODUCT_NOT_FOUND"].format(product=name))
            return

        blocks = create_product_confirmation_blocks("delete", name)
        respond(blocks=blocks)
    finally:
        session.close()

def handle_product_status(respond: callable, args: List[str], activate: bool) -> None:
    if not args:
        respond(ADMIN_ERROR_MESSAGES["MISSING_PRODUCT_NAME"])
        return

    name = args[0]
    session = Session()
    try:
        product = session.query(Product).filter_by(name=name).first()
        if not product:
            respond(ADMIN_ERROR_MESSAGES["PRODUCT_NOT_FOUND"].format(product=name))
            return

        action = "activate" if activate else "deactivate"
        blocks = create_product_status_blocks(action, name)
        respond(blocks=blocks)
    finally:
        session.close()

def handle_product_list(respond: callable) -> None:
    session = Session()
    try:
        products = session.query(Product).all()
        if not products:
            respond("Keine Produkte gefunden.")
            return

        product_list = []
        for product in products:
            status = "✅ aktiv" if product.active else "❌ inaktiv"
            desc = f" - {product.description}" if product.description else ""
            product_list.append(f"• {product.name}{desc} ({status})")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 Produktliste",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(product_list)
                }
            }
        ]
        respond(blocks=blocks)
    finally:
        session.close()