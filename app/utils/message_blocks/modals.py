#==========================
# app/utils/message_blocks/modals.py
#==========================

from typing import Dict, List

# Diese Datei enthält Hilfsfunktionen zur Erstellung von Slack Modals (Dialogen).
# Modals werden für interaktive Eingaben wie Bestellungen oder Feedback genutzt.


def create_order_modal(trigger_id: str) -> Dict:
    """
    Erstellt ein Modal für die Eingabe einer neuen Bestellung.
    :param trigger_id: Slack Trigger-ID für das Öffnen des Modals
    :return: Dictionary mit Modal-Definition
    """
    return {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Neue Bestellung"},
            "submit": {"type": "plain_text", "text": "Bestellen"},
            "close": {"type": "plain_text", "text": "Abbrechen"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "product_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "product_input",
                        "placeholder": {"type": "plain_text", "text": "z.B. Brötchen"}
                    },
                    "label": {"type": "plain_text", "text": "Produkt"}
                },
                {
                    "type": "input",
                    "block_id": "quantity_block",
                    "element": {
                        "type": "number_input",
                        "action_id": "quantity_input",
                        "is_decimal_allowed": False,
                        "min_value": "1"
                    },
                    "label": {"type": "plain_text", "text": "Anzahl"}
                }
            ]
        }
    }

def create_feedback_modal() -> List[Dict]:
    """
    Erstellt einen Modal-Dialog für Feedback.
    :return: Liste von Block-Objekten für das Feedback-Modal
    """
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📝 Feedback"}
        },
        {
            "type": "input",
            "block_id": "feedback_title",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_title_input",
                "placeholder": {"type": "plain_text", "text": "Kurze Überschrift für dein Feedback"},
                "max_length": 100
            },
            "label": {"type": "plain_text", "text": "Überschrift"}
        },
        {
            "type": "input",
            "block_id": "feedback_text",
            "element": {
                "type": "plain_text_input",
                "action_id": "feedback_text_input",
                "multiline": True,
                "placeholder": {"type": "plain_text", "text": "Beschreibe dein Feedback, Verbesserungsvorschläge oder Probleme..."},
                "max_length": 1000
            },
            "label": {"type": "plain_text", "text": "Feedback"}
        },
        {
            "type": "actions",
            "block_id": "feedback_actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Feedback senden", "emoji": True},
                    "style": "primary",
                    "action_id": "submit_feedback"
                }
            ]
        }
    ]
