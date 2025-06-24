#==========================
# app/utils/slack_messages.py
#==========================

from typing import Dict, List, Tuple, Optional


def create_name_blocks(current_name: str, new_name: Optional[str] = None) -> Tuple[List[Dict], List[Dict]]:
    """Erstellt Slack-Blocks für die Namensanzeige/-änderung"""
    blocks = []
    attachments = []

    if new_name:
        # Name wurde geändert
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
        # Aktuelle Namenanzeige
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

    return blocks, attachments


def create_registration_blocks() -> List[Dict]:
    """Erstellt Slack-Blocks für die Registrierungsaufforderung"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Du bist noch nicht registriert! Bitte registriere dich zuerst mit:\n`/name <dein_name>`"
            }
        }
    ]
