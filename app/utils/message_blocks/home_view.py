#==========================
# app/utils/message_blocks/home_view.py
#==========================

from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models import User, Order
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS

def create_unregistered_home_view() -> Dict[str, Any]:
    """Erstellt die Home-Ansicht für nicht registrierte Benutzer"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Willkommen beim BrotBot! 🥨"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Bevor du den Bot nutzen kannst, musst du dich registrieren."
            }
        },
        {
            "type": "input",
            "block_id": "registration_name",
            "element": {
                "type": "plain_text_input",
                "action_id": "registration_name_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Dein Name"
                },
                "min_length": 1
            },
            "label": {
                "type": "plain_text",
                "text": "Registriere dich mit deinem Namen"
            }
        },
        {
            "type": "actions",
            "block_id": "registration_actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Registrieren",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": "submit_registration"
                }
            ]
        }
    ]

    return {
        "type": "home",
        "blocks": blocks
    }

def create_home_view(user: Optional[User] = None, recent_orders: List[Order] = None) -> Dict[str, Any]:
    """Erstellt die Home-Ansicht für den Bot"""
    if user is None:
        return create_unregistered_home_view()

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Willkommen, {user.name}!"
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

    # Aktuelle Wochenbestellung anzeigen
    if recent_orders:
        # Alle Produkte über den gesamten Zeitraum summieren
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
                    {
                        "type": "mrkdwn",
                        "text": "*Produkt*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Menge*"
                    }
                ]
            })

            # Produktliste in Tabellenform ausgeben
            for product, quantity in sorted(product_totals.items()):
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"{product}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{quantity}x"
                        }
                    ]
                })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Keine aktiven Bestellungen für diese Woche_"
                }
            })


    blocks.extend([
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{EMOJIS['USER']}Infos zu dir"
            }
        },
        {
            "type": "section",
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
        ),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{EMOJIS['SETTINGS']} Hilfe & Befehle"
            }
        },

        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "Für Hilfe zu den verfügbaren Befehlen, verwende folgende Befehle:\n\n"
                    f"• `/user` {EMOJIS['USER']} Benutzerbefehle\n"
                    f"• `/order` {EMOJIS['ORDER']} Bestellbefehle\n" +
                    (f"• `/admin` {EMOJIS['ADMIN']} Admin-Befehle\n" if user.is_admin else "")
                )
            }
        },
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📝 Feedback"
            }
        },
        {
            "type": "input",
            "block_id": "feedback_title",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_title_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Kurze Überschrift für dein Feedback"
                },
                "max_length": 100
            },
            "label": {
                "type": "plain_text",
                "text": "Überschrift"
            }
        },
        {
            "type": "input",
            "block_id": "feedback_text",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_text_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Beschreibe dein Feedback, Verbesserungsvorschläge oder Probleme..."
                },
                "max_length": 1000
            },
            "label": {
                "type": "plain_text",
                "text": "Feedback"
            }
        },
        {
            "type": "actions",
            "block_id": "feedback_actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Feedback senden",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": "submit_feedback"
                }
            ]
        }
    ])
    # Füge Footer hinzu
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Bot erstellt von *{'Benedict Benge' if user.slack_id == 'U08LZK84FFZ' else ""}, *im Auftrag von *Tobias Schenck* der Schenck.de AG"
            }
        ]
    })

    return {
        "type": "home",
        "blocks": blocks
    }