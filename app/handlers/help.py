#==========================
# app/handlers/help.py
#==========================

def handle_help(ack, respond):
    ack()
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Brötchenbot Hilfe 🛟",
                "emoji": True
            }
        }
    ]
    attachments = [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Befehle:*\n" +
                                "`/order add <Produkt> <Menge>, <Produkt> <Menge>, ...` - Produkt zur Bestellung hinzufügen\n" +
                                "`/name` - Deinen aktuellen Namen anzeigen\n" +
                                "`/name change <Neuer Name>` - Deinen Namen ändern\n"
                    }
                }
            ]
        }
    ]
    respond(blocks=blocks, attachments=attachments)