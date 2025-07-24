#==========================
# app/utils/message_blocks/home_view.py
#==========================

from typing import Dict, List, Any
from datetime import datetime
from app.models import User, Order
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS

# Diese Datei enthält die Funktion zur Erstellung der Home-Ansicht (App Home) für den Slack-Bot.
# Die Home-Ansicht ist die zentrale Übersichtsseite für den User in Slack.
# Sie zeigt Willkommensnachricht, Schnellzugriffe, aktuelle Bestellungen, Feedback-Formular und ggf. Admin-Funktionen.

def create_home_view(user: User, recent_orders: List[Order] = None) -> Dict[str, Any]:
    """
    Erstellt die Home-Ansicht für den BrotBot in Slack.
    Zeigt Willkommensnachricht, Schnellzugriffe, aktuelle Wochenbestellung, Feedback-Formular und Admin-Bereich.
    :param user: User-Objekt (aktueller Slack-User)
    :param recent_orders: Liste der letzten Bestellungen des Users (optional)
    :return: Dictionary mit Slack-Home-View-Blocks
    """
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

        # Schnellzugriff (optional)

        # {
        #     "type": "section",
        #     "text": {
        #         "type": "mrkdwn",
        #         "text": "*Schnellzugriff:*"
        #     }
        # },
        # {
        #     "type": "actions",
        #     "elements": [
        #         {
        #             "type": "button",
        #             "text": {
        #                 "type": "plain_text",
        #                 "text": f"{EMOJIS['WARNING']} Neue Bestellung (WiP)"
        #             },
        #             "style": "danger",
        #             "action_id": "new_order"
        #         },
        #         {
        #             "type": "button",
        #             "text": {
        #                 "type": "plain_text",
        #                 "text": f"{EMOJIS['WARNING']} Meine Bestellungen (WiP)"
        #             },
        #             "style": "danger",
        #             "action_id": "list_orders"
        #         }
        #     ]
        # },


        # Befehle-Übersicht (optional)

        # BLOCK_DEFAULTS["DIVIDER"],
        # {
        #     "type": "section",
        #     "text": {
        #         "type": "mrkdwn",
        #         "text": "*Verfügbare Befehle:*"
        #     }
        # },
        # {
        #     "type": "section",
        #     "text": {
        #         "type": "mrkdwn",
        #         "text": (
        #             f"• `/order add` Neue Bestellung\n"
        #             f"• `/order list` Aktuelle Bestellung anzeigen\n"
        #             f"• `/order save` Bestellung speichern\n"
        #             f"• `/order savelist` Gespeicherte Bestellungen anzeigen\n"
        #             f"• `/order remove` Produkt aus Bestellung löschen\n"
        #             f"• `/order products` Aktive Produkte anzeigen\n"
        #             f"• `/order` Hilfe anzeigen\n\n"
        #             f"• `/user register` In die Datenbank registrieren\n"
        #             f"• `/user name` Name in der Datenbank ändern\n"
        #             f"• `/user` Hilfe anzeigen\n"
        #         )
        #     }
        # },
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{EMOJIS['ORDER']} Aktuelle Wochenbestellung"
            }
        }
    ]

    # Aktuelle Wochenbestellung anzeigen (falls vorhanden)
    if recent_orders:
        # Produkte und Mengen aufsummieren
        product_totals = {}
        for order in recent_orders:
            for item in order.items:
                name = item.product.name
                if name in product_totals:
                    product_totals[name] += item.quantity
                else:
                    product_totals[name] = item.quantity

        if product_totals:
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Produkt*"},
                    {"type": "mrkdwn", "text": "*Menge*"}
                ]
            })
            for product, quantity in sorted(product_totals.items()):
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"{product}"},
                        {"type": "mrkdwn", "text": f"{quantity}x"}
                    ]
                })
        else:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "_Keine aktiven Bestellungen für diese Woche_"}
            })

    # Weitere Blöcke: User-Infos, Feedback, Admin-Bereich
    blocks.extend([
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Allgemeine Infos:*"},
            "fields": [
                {"type": "mrkdwn", "text": f"*Name:*\n{user.name}"},
                {"type": "mrkdwn", "text": f"*Status:*\n{'Abwesend' if user.is_away else 'Anwesend'}"}
            ]
        },
        BLOCK_DEFAULTS["CONTEXT"](
            f"Zuletzt aktualisiert: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        ),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📝 Feedback"}
        },
        {
            "type": "input",
            "block_id": "feedback_title",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_title_input",
                "placeholder": {"type": "plain_text", "text": "Kurze Überschrift für dein Feedback"},
                "max_length": 100
            },
            "label": {"type": "plain_text", "text": "Überschrift"}
        },
        {
            "type": "input",
            "block_id": "feedback_text",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_text_input",
                "multiline": True,
                "placeholder": {"type": "plain_text", "text": "Beschreibe dein Feedback, Verbesserungsvorschläge oder Probleme..."},
                "max_length": 1000
            },
            "label": {"type": "plain_text", "text": "Feedback"}
        },
        {
            "type": "actions",
            "block_id": "feedback_actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Feedback senden", "emoji": True},
                    "style": "primary",
                    "action_id": "submit_feedback"
                }
            ]
        }
    ])

    # Admin-Sektion für Administratoren anzeigen
    if user.is_admin:
        blocks.extend([
            BLOCK_DEFAULTS["DIVIDER"],
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{EMOJIS['ADMIN']} Admin-Funktionen:*"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": (
                    f"• `/admin product add [name] [beschreibung]` {EMOJIS['NEW']} Produkt hinzufügen\n"
                    f"• `/admin product list` {EMOJIS['LIST']} Produkte anzeigen\n"
                    f"• `/admin help` {EMOJIS['INFO']} Admin-Hilfe"
                )}
            }
        ])

    return {
        "type": "home",
        "blocks": blocks
    }