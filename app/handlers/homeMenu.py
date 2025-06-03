#==========================
# app/handlers/homeMenu.py
#==========================

from app.bot import app

def create_home_view():
    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🥨 Willkommen beim BrotBot",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Schnellzugriff auf Funktionen:*"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🛒 Neue Bestellung",
                            "emoji": True
                        },
                        "action_id": "new_order_clicked",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📋 Meine Bestellungen",
                            "emoji": True
                        },
                        "action_id": "my_orders_clicked"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Verfügbare Befehle:*\n\n" +
                           "• `/order add <Produkt> <Menge>` - Neue Bestellung aufgeben\n" +
                           "• `/order list` - Aktuelle Bestellungen anzeigen\n" +
                           "• `/name` - Namen anzeigen/ändern\n" +
                           "• `/help` - Hilfe anzeigen"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🕐 Bestellungen werden jeden Mittwoch um 10:00 Uhr gesammelt"
                    }
                ]
            }
        ]
    }

@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    try:
        client.views_publish(
            user_id=event["user"],
            view=create_home_view()
        )
    except Exception as e:
        logger.error(f"Error publishing home view: {e}")