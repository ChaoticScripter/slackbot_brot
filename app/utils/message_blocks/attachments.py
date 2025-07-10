# ==========================
# app/utils/message_blocks/attachments.py
# ==========================

from typing import Dict, List
from datetime import datetime
from app.models import Order
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS

# Diese Funktionen wurden in messages.py verschoben
'''
def create_order_confirmation_blocks(order) -> List[Dict]:
    """Erstellt Message Blocks für eine Bestellbestätigung"""
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['SUCCESS']} Bestellung bestätigt"),
        BLOCK_DEFAULTS["CONTEXT"](f"Bestellt am: {order.order_date.strftime('%d.%m.%Y %H:%M')}"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bestelldetails:*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Produkt*"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Menge*"
                }
            ]
        },
        *[{
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"{item.product.name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"{item.quantity}x"
                }
            ]
        } for item in order.items],
        BLOCK_DEFAULTS["DIVIDER"],
        BLOCK_DEFAULTS["CONTEXT"](f"{EMOJIS['INFO']} Verwende `/order list` um deine gesamte Bestellungen anzuzeigen")
    ]

def create_order_list_blocks(orders: List, period_start: datetime, period_end: datetime, latest_order: Order = None) -> List[Dict]:
    """Erstellt Message Blocks für die Bestellübersicht"""
    # Bestellungen zusammenfassen
    product_totals = {}
    for order in orders:
        for item in order.items:
            name = item.product.name
            if name in product_totals:
                product_totals[name] += item.quantity
            else:
                product_totals[name] = item.quantity

    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['LIST']} Bestellübersicht"),
        BLOCK_DEFAULTS["CONTEXT"](
            f"Zeitraum: {EMOJIS['CALENDAR']} {period_start.strftime('%d.%m.%Y')} 10:00 - "
            f"{period_end.strftime('%d.%m.%Y')} 09:59"
        ),
        BLOCK_DEFAULTS["CONTEXT"](
            f"Stand: {EMOJIS['TIME']} " +
            (latest_order.order_date.strftime("%d.%m.%Y %H:%M") if latest_order else "Keine Bestellungen")
        ),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "\n".join([f"• {product}: {quantity}x"
                             for product, quantity in sorted(product_totals.items())])
                ) if product_totals else f"{EMOJIS['INFO']} Keine Bestellungen in diesem Zeitraum"
            }
        }
    ]

def create_name_blocks(current_name: str = None, new_name: str = None) -> List[Dict]:
    """Erstellt Message Blocks für Namen/Namensänderung"""
    if new_name:
        # Name change confirmation
        return [
            BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['SUCCESS']} Name geändert"),
            BLOCK_DEFAULTS["DIVIDER"],
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Alter Name:* {current_name}\n*Neuer Name:* {new_name}"
                }
            }
        ]
    else:
        # Show current name
        return [
            BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['USER']} Benutzer-Information"),
            BLOCK_DEFAULTS["DIVIDER"],
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Aktueller Name:* {current_name or 'Nicht gesetzt'}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Tipp:* Verwende `/user changename [neuer name]` um deinen Namen zu ändern."
                }
            }
        ]

def create_registration_blocks() -> List[Dict]:
    """Erstellt Message Blocks für die Registrierungsaufforderung"""
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['NEW']} Registrierung erforderlich"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{EMOJIS['INFO']} Du bist noch nicht registriert!\n"
                    f"Bitte registriere dich zuerst, um den Bot verwenden zu können.\n\n"
                    f"*Verwende:* `/user register [dein name]`"
                )
            }
        }
    ]
'''
