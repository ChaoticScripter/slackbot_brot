# ==========================
# app/utils/message_blocks/attachments.py
# ==========================

from typing import Dict, List
from datetime import datetime
from app.models import Order
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS

def create_order_confirmation_attachments(order) -> List[Dict]:
    """Erstellt die Attachments für eine Bestellbestätigung"""
    return [{
        "color": COLORS["SUCCESS"],
        "fallback": "Bestellbestätigung für Ihre Bestellung",
        "blocks": [
            BLOCK_DEFAULTS["HEADER"](
                f"{EMOJIS['SUCCESS']} Bestellung bestätigt"
            ),
            BLOCK_DEFAULTS["CONTEXT"](
                f"Bestellt am: {order.order_date.strftime('%d.%m.%Y %H:%M')}"
            ),
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
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"{EMOJIS['INFO']} Verwende `/order list` um deine Bestellungen anzuzeigen"
                    }
                ]
            }
        ]
    }]

def create_order_list_attachments(orders: List, period_start: datetime, period_end: datetime, latest_order: Order = None) -> List[Dict]:
    """Erstellt die Attachments für die Bestellübersicht"""
    # Bestellungen zusammenfassen
    product_totals = {}
    for order in orders:
        for item in order.items:
            name = item.product.name
            if name in product_totals:
                product_totals[name] += item.quantity
            else:
                product_totals[name] = item.quantity

    return [{
        "color": COLORS["INFO"],
        "fallback": "Bestellübersicht",
        "blocks": [
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
    }]