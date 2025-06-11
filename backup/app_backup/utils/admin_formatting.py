#==========================
# app/utils/admin_formatting.py
#==========================

from typing import List, Dict, Any


def create_product_confirmation_blocks(action: str, name: str, description: str = None) -> List[Dict[str, Any]]:
    """Erstellt Bestätigungsblöcke für Produkt-Aktionen"""
    action_text = "hinzufügen" if action == "add" else "löschen"
    color = "success" if action == "add" else "danger"

    description_text = f"\n\nBeschreibung: {description}" if description else ""

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"⚠️ Produkt {action_text}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Möchtest du das folgende Produkt wirklich {action_text}?\n\n"
                        f"*{name}*{description_text}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Bestätigen",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": f"admin_product_{action}_confirm",
                    "value": f"{name}|{description if description else ''}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Abbrechen",
                        "emoji": True
                    },
                    "style": "danger",
                    "action_id": f"admin_product_{action}_cancel"
                }
            ]
        }
    ]


def create_product_status_blocks(action: str, name: str) -> List[Dict[str, Any]]:
    """Erstellt Bestätigungsblöcke für Produkt-Status-Änderungen"""
    action_text = "aktivieren" if action == "activate" else "deaktivieren"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"⚠️ Produkt {action_text}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Möchtest du das folgende Produkt wirklich {action_text}?\n\n"
                        f"*{name}*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Bestätigen",
                        "emoji": True
                    },
                    "style": "primary",
                    "action_id": f"admin_product_{action}_confirm",
                    "value": name
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Abbrechen",
                        "emoji": True
                    },
                    "style": "danger",
                    "action_id": f"admin_product_{action}_cancel"
                }
            ]
        }
    ]