#==========================
# app/utils/message_blocks/messages.py
#==========================

from datetime import datetime
from typing import Dict, List
import json

from app.utils.message_blocks.constants import EMOJIS, BLOCK_DEFAULTS, COLORS
from app.models import Order


def create_admin_help_blocks() -> List[Dict]:
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['ADMIN']} Admin-Befehle"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Produkt-Verwaltung:*\n"
                    f"• `/admin product add [name]` {EMOJIS['NEW']} Neues Produkt hinzufügen\n"
                    f"• `/admin product list` {EMOJIS['LIST']} Alle Produkte anzeigen\n"
                    f"• `/admin help` {EMOJIS['INFO']} Diese Hilfe anzeigen"
                )
            }
        }
    ]

def create_product_list_blocks(products: List) -> List[Dict]:
    blocks = [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['PRODUCT']} Produktübersicht"),
        BLOCK_DEFAULTS["DIVIDER"]
    ]

    if not products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{EMOJIS['INFO']} Keine aktiven Produkte vorhanden"
            }
        })
        return blocks

    for product in products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"• *{product.name}*"

            #},
            #"accessory": {
            #    "type": "button",
            #    "text": {
            #        "type": "plain_text",
            #        "text": "Bestellen"
            #    },
            #    "value": f"order_{product.product_id}",
            #    "action_id": "order_product"
            }

        })

    return blocks

def create_product_list_blocks() -> List[Dict]:
    """Erstellt Message Blocks für die Produktliste"""
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['PRODUCT']} Verfügbare Produkte"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Produkt*"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Beschreibung*"
                }
            ]
        }
    ]

def create_product_row_block(product) -> Dict:
    """Erstellt einen Block für eine Produktzeile"""
    return {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"{product.name}"
            },
            {
                "type": "mrkdwn",
                "text": f"{product.description or '_Keine Beschreibung_'}"
            }
        ]
    }

def create_order_help_blocks() -> List[Dict]:
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['ORDER']} Bestellhilfe"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Verfügbare Befehle:*\n"
                    f"• `/order add [produkt] [anzahl], ...` - {EMOJIS['NEW']} Neue Bestellung aufgeben\n"
                    f"• `/order remove [produkt] [anzahl], ...` - {EMOJIS['DELETE']} Produkt entfernen~ *COMING SOON!*\n"
                    f"• `/order list` - {EMOJIS['LIST']} Aktuelle Bestellungen anzeigen\n"
                    f"• `/order save [name] [produkt] [anzahl], ...` - {EMOJIS['SAVE']} Bestellung speichern\n"
                    f"• `/order savelist` - {EMOJIS['LIST']} Gespeicherte Bestellungen anzeigen\n"                    
                    f"• `/order help` - {EMOJIS['INFO']} Diese Hilfe\n"
                )
            }
        }
    ]

def create_order_confirmation_blocks(order: Order) -> List[Dict]:
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
        BLOCK_DEFAULTS["CONTEXT"](f"{EMOJIS['INFO']} Verwende `/order list` um deine gesamten Bestellungen anzuzeigen")
    ]

def create_order_list_blocks(orders: List[Order], period_start: datetime, period_end: datetime, latest_order: Order = None) -> List[Dict]:
    """Erstellt Message Blocks für die Bestellübersicht"""
    blocks = [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['LIST']} Bestellübersicht"),
        BLOCK_DEFAULTS["CONTEXT"](
            f"Zeitraum: {EMOJIS['CALENDAR']} {period_start.strftime('%d.%m.%Y')} 10:00 - "
            f"{period_end.strftime('%d.%m.%Y')} 09:59"
        ),
        BLOCK_DEFAULTS["CONTEXT"](
            f"Stand: {EMOJIS['TIME']} " +
            (latest_order.order_date.strftime("%d.%m.%Y %H:%M") if latest_order else "Keine Bestellungen")
        ),
        BLOCK_DEFAULTS["DIVIDER"]
    ]

    if not orders:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{EMOJIS['INFO']} Keine Bestellungen in diesem Zeitraum"
            }
        })
        return blocks

    # Alle Produkte über den gesamten Zeitraum summieren
    product_totals = {}
    for order in orders:
        for item in order.items:
            name = item.product.name
            if name in product_totals:
                product_totals[name] += item.quantity
            else:
                product_totals[name] = item.quantity

    # Header für die Tabelle
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Gesamtbestellung:*"
        }
    })

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

    return blocks

def create_daily_reminder_blocks() -> List[Dict]:
    return [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['REMINDER']} Tägliche Erinnerung"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{EMOJIS['INFO']} Vergiss nicht, deine Bestellung aufzugeben!\n"
                    f"Verwende `/order add [produkt] [anzahl]` um eine neue Bestellung zu erstellen."
                )
            }
        }
    ]

def create_name_blocks(current_name: str = None, new_name: str = None) -> List[Dict]:
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
                    "text": f"*Tipp:* Verwende `/name change [neuer name]` um deinen Namen zu ändern."
                }
            }
        ]

def create_registration_blocks() -> List[Dict]:
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

def create_remove_preview_blocks(order: Order, items_to_remove: List[Dict], preview_items: Dict[str, int], period_start: datetime, period_end: datetime) -> List[Dict]:
    """Erstellt Vorschau-Blöcke für das Entfernen von Produkten"""
    # Button-Value für die Metadaten
    button_value = json.dumps({
        "type": "remove_order",
        "data": {
            "items": items_to_remove,
            "user_id": order.user.slack_id
        }
    })

    blocks = [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['WARNING']} Bestellung ändern"),
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Zu entfernende Produkte:*"
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
        }
    ]

    # Zu entfernende Produkte als Fields
    for remove_info in items_to_remove:
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"{remove_info['name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"{remove_info['quantity']}x"
                }
            ]
        })

    # Bestellung nach Änderung
    blocks.extend([
        BLOCK_DEFAULTS["DIVIDER"],
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bestellung nach Änderung:*"
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
        }
    ])

    if preview_items:
        # Alle verbleibenden Produkte anzeigen, sortiert nach Name
        for product_name, quantity in sorted(preview_items.items()):
            if quantity > 0:  # Nur Produkte mit einer Menge > 0 anzeigen
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"{product_name}"
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
                "text": "_Keine Produkte in der Bestellung_"
            }
        })

    blocks.extend([
        BLOCK_DEFAULTS["CONTEXT"](
            f"{EMOJIS['INFO']} Diese Vorschau ist für 30 Sekunden gültig. Danach wird der Vorgang automatisch abgebrochen."
        ),
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Bestätigen",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": button_value,
                    "action_id": "remove_confirm"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Abbrechen",
                        "emoji": True
                    },
                    "style": "danger",
                    "action_id": "remove_cancel"
                }
            ]
        }
    ])

    return blocks

# Weitere Message-Block-Funktionen bleiben ähnlich,
# werden aber mit den neuen Konstanten und Layouts aktualisiert