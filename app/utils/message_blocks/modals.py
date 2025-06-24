#==========================
# app/utils/message_blocks/modals.py
#==========================

from typing import Dict, List

def create_order_modal(trigger_id: str) -> Dict:
    return {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Neue Bestellung"
            },
            "submit": {
                "type": "plain_text",
                "text": "Bestellen"
            },
            "close": {
                "type": "plain_text",
                "text": "Abbrechen"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "product_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "product_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "z.B. Brötchen"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Produkt"
                    }
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
                    "label": {
                        "type": "plain_text",
                        "text": "Anzahl"
                    }
                }
            ]
        }
    }