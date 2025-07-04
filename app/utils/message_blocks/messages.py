#==========================
# app/utils/message_blocks/messages.py
#==========================

from typing import Dict, List, Optional
from app.utils.message_blocks.constants import COLORS, EMOJIS, BLOCK_DEFAULTS
from datetime import datetime

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
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Bestellen"
                },
                "value": f"order_{product.product_id}",
                "action_id": "order_product"
            }
        })

    return blocks

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
                    f"• `/order save [name] [produkt] [anzahl], ...` - {EMOJIS['SAVE']} Bestellung speichern\n"
                    f"• `/order savelist` - {EMOJIS['LIST']} Gespeicherte Bestellungen anzeigen\n"
                    f"• `/order list` - {EMOJIS['LIST']} Aktuelle Bestellungen anzeigen\n"
                    f"• `/order help` - {EMOJIS['INFO']} Diese Hilfe\n"
                )
            }
        }
    ]

def create_order_list_blocks(orders: List) -> List[Dict]:
    blocks = [
        BLOCK_DEFAULTS["HEADER"](f"{EMOJIS['LIST']} Bestellübersicht"),
        BLOCK_DEFAULTS["CONTEXT"](f"Stand: {EMOJIS['TIME']} " +
                                datetime.now().strftime("%d.%m.%Y %H:%M")),
        BLOCK_DEFAULTS["DIVIDER"]
    ]

    if not orders:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{EMOJIS['INFO']} Keine aktiven Bestellungen"
            }
        })
        return blocks

    # Bestellungen nach Datum gruppieren
    grouped_orders = {}
    for order in orders:
        date = order.order_date.strftime("%d.%m.%Y")
        if date not in grouped_orders:
            grouped_orders[date] = []
        grouped_orders[date].extend(order.items)

    for date, items in grouped_orders.items():
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{EMOJIS['CALENDAR']} {date}*"
                }
            }
        ])

        # Produkte gruppieren und summieren
        product_totals = {}
        for item in items:
            name = item.product.name
            if name in product_totals:
                product_totals[name] += item.quantity
            else:
                product_totals[name] = item.quantity

        # Sortierte Produktliste ausgeben
        order_list = []
        for product, quantity in sorted(product_totals.items()):
            order_list.append(f"• {product}: {quantity}x")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(order_list)
            }
        })
        blocks.append(BLOCK_DEFAULTS["DIVIDER"])

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

# Weitere Message-Block-Funktionen bleiben ähnlich,
# werden aber mit den neuen Konstanten und Layouts aktualisiert