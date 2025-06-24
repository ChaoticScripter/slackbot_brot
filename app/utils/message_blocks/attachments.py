#==========================
# app/utils/message_blocks/attachments.py
#==========================

from typing import Dict, List

def create_order_confirmation_attachments(order) -> List[Dict]:
    attachments = [
        {
            "color": "#36a64f",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *Bestellung erfolgreich aufgegeben!*"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
    ]

    order_details = []
    for item in order.items:
        order_details.append(f"• {item.product.name}: {item.quantity}x")

    attachments[0]["blocks"].append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Bestelldetails:*\n" + "\n".join(order_details)
        }
    })

    return attachments