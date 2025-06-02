#==========================
# app/utils/formatting.py
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