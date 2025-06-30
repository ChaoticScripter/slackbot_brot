#==========================
# app/utils/message_blocks/home_view.py
#==========================

from typing import Dict, List, Any
from datetime import datetime
from app.models import User, Order
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS

def create_home_view(user: User, recent_orders: List[Order] = None) -> Dict[str, Any]:
    """Erstellt die Home-Ansicht für den Bot"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{EMOJIS['ORDER']} BrotBot Home"
            }
        },
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Willkommen, {user.name}!*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Schnellzugriff:*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"{EMOJIS['NEW']} Neue Bestellung"
                    },
                    "style": "primary",
                    "action_id": "new_order"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"{EMOJIS['LIST']} Meine Bestellungen"
                    },
                    "action_id": "list_orders"
                }
            ]
        },
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Verfügbare Befehle:*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"• `/order add [produkt] [anzahl]` {EMOJIS['NEW']} Neue Bestellung\n"
                    f"• `/order list` {EMOJIS['LIST']} Bestellungen anzeigen\n"
                    f"• `/order save [name]` {EMOJIS['SAVE']} Bestellung speichern\n"
                    f"• `/order help` {EMOJIS['INFO']} Hilfe anzeigen"
                )
            }
        }
    ]

    # Letzte Bestellungen anzeigen, wenn vorhanden
    if recent_orders:
        blocks.extend([
            BLOCK_DEFAULTS["DIVIDER"],
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{EMOJIS['TIME']} Letzte Bestellungen:*"
                }
            }
        ])

        for order in recent_orders:
            order_items = []
            for item in order.items:
                order_items.append(f"• {item.product.name}: {item.quantity}x")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{order.order_date.strftime('%d.%m.%Y %H:%M')}*\n"
                        f"{'\n'.join(order_items)}"
                    )
                }
            })

    # Status-Sektion
    blocks.extend([
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Status:*"
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Name:*\n{user.name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{'Abwesend' if user.is_away else 'Anwesend'}"
                }
            ]
        },
        BLOCK_DEFAULTS["CONTEXT"](
            f"Zuletzt aktualisiert: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
    ])

    # Admin-Sektion für Administratoren
    if user.is_admin:
        blocks.extend([
            BLOCK_DEFAULTS["DIVIDER"],
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{EMOJIS['ADMIN']} Admin-Funktionen:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"• `/admin product add [name]` {EMOJIS['NEW']} Produkt hinzufügen\n"
                        f"• `/admin product list` {EMOJIS['LIST']} Produkte anzeigen\n"
                        f"• `/admin help` {EMOJIS['INFO']} Admin-Hilfe"
                    )
                }
            }
        ])

    return {
        "type": "home",
        "blocks": blocks
    }