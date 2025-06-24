#==========================
# app/utils/message_blocks/messages.py
#==========================

from typing import Dict, List

def create_admin_help_blocks() -> List[Dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Admin Befehle:*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "• `/admin product add [name]` - Neues Produkt hinzufügen\n"
                       "• `/admin product list` - Alle Produkte anzeigen\n"
                       "• `/admin help` - Diese Hilfe anzeigen"
            }
        }
    ]

def create_product_list_blocks(products: List) -> List[Dict]:
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Aktive Produkte:*"
            }
        }
    ]

    if not products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Keine aktiven Produkte vorhanden"
            }
        })
        return blocks

    product_list = []
    for product in products:
        product_list.append(f"• {product.name}")

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "\n".join(product_list)
        }
    })

    return blocks

def create_order_help_blocks() -> List[Dict]:
    return [
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
                    "• `/order add [produkt] [anzahl]` - Neue Bestellung aufgeben\n"
                    "• `/order list` - Deine Bestellungen anzeigen\n"
                    "• `/order help` - Diese Hilfe anzeigen"
                )
            }
        }
    ]

def create_order_list_blocks(orders: List) -> List[Dict]:
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "📋 *Deine Bestellung für diese Woche:*"
            }
        },
        {
            "type": "divider"
        }
    ]

    all_items = {}
    for order in orders:
        for item in order.items:
            product_name = item.product.name
            if product_name in all_items:
                all_items[product_name] += item.quantity
            else:
                all_items[product_name] = item.quantity

    if all_items:
        order_details = []
        for product_name, quantity in sorted(all_items.items()):
            order_details.append(f"• {product_name}: {quantity}x")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(order_details)
            }
        })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "❌ Keine aktiven Bestellungen vorhanden."
            }
        })

    return blocks

def create_name_blocks(current_name: str, new_name: str = None) -> List[Dict]:
    blocks = []

    if new_name:
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ Dein Name wurde geändert von *{current_name}* zu *{new_name}*"
                }
            }
        ])
    else:
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Dein aktueller Name ist: *{current_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Um deinen Namen zu ändern, nutze:\n`/name change <neuer_name>`"
                }
            }
        ])

    return blocks

def create_registration_blocks() -> List[Dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Du bist noch nicht registriert! Bitte registriere dich zuerst mit:\n`/name <dein_name>`"
            }
        }
    ]

def create_daily_reminder_blocks() -> List[Dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔔 *Tägliche Erinnerung*\nVergiss nicht, deine Bestellung aufzugeben!"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Nutze `/order add [produkt] [anzahl]` um zu bestellen."
            }
        }
    ]