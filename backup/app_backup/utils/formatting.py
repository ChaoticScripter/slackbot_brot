#==========================
# app/utils/slack_messages.py
#==========================

def format_order_summary(items):
    return "\n".join([f"• {total}x {name}" for name, total in items])


def create_order_blocks(user_name, summary, items, period_start, period_end):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🥨 Hey {user_name}, deine Bestellung wurde aktualisiert!",
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
                        "text": "*Hinzugefügt:*\n" + "\n".join(summary)
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Deine aktuelle Bestellung:*\n" + format_order_summary(items)
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Bestellzeitraum: {period_start.strftime('%d.%m.%Y %H:%M')} - {period_end.strftime('%d.%m.%Y %H:%M')}"
                        }
                    ]
                }
            ]
        }
    ]
    return blocks, attachments


def create_help_blocks():
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
                        "text": "*Verfügbare Befehle:*\n\n" +
                                "• `/order add <Produkt> <Menge>, ...`\n" +
                                "  _Fügt Produkte zur Bestellung hinzu_\n\n" +
                                "• `/name`\n" +
                                "  _Zeigt deinen aktuellen Namen_\n\n" +
                                "• `/name change <Neuer Name>`\n" +
                                "  _Ändert deinen angezeigten Namen_"
                    }
                }
            ]
        }
    ]
    return blocks, attachments


def create_name_blocks(current_name=None, new_name=None):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "👤 Namen-Verwaltung",
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
                        "text": (f"*Aktueller Name:* {current_name}\n\n" if current_name else "") +
                                (f"*Neuer Name:* {new_name}" if new_name else "") +
                                (
                                    f"\n\n_Tipp: Mit `/name change <neuer Name>` kannst du deinen Namen ändern._" if not new_name else "")
                    }
                }
            ]
        }
    ]
    return blocks, attachments