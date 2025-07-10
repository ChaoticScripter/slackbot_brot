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
                        "text": f"{EMOJIS['WARNING']} Neue Bestellung (WiP)"
                    },
                    "style": "danger",
                    "action_id": "new_order"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"{EMOJIS['WARNING']} Meine Bestellungen (WiP)"
                    },
                    "style": "danger",
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
                    f"• `/order add` Neue Bestellung\n"
                    f"• `/order list` Aktuelle Bestellung anzeigen\n"
                    f"• `/order save` Bestellung speichern\n"
                    f"• `/order savelist` Gespeicherte Bestellungen anzeigen\n"
                    f"• `/order remove` Produkt aus Bestellung löschen\n"
                    f"• ~`/order products` Aktive Produkte anzeigen\n"
                    f"• `/order` Hilfe anzeigen\n\n"
                    f"• `/user register` In die Datenbank registrieren\n"
                    f"• `/user name` Name in der Datenbank ändern\n"
                    f"• `/user` Hilfe anzeigen\n"
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

        weekday_map = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

        for order in recent_orders:
            order_items = []
            for item in order.items:
                order_items.append(f"• {item.product.name}: {item.quantity}x")

            weekday = weekday_map[order.order_date.weekday()]  # 0=Mo, ..., 6=So

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{weekday}, {order.order_date.strftime('%d.%m.%Y - %H:%M')}*\n"
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
                "text": "*Allgemeine Infos:*"
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