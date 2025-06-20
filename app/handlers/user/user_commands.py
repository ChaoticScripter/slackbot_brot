#==========================
# app/handlers/user/user_commands.py
#==========================

from typing import Dict, Any, List
import logging
from difflib import get_close_matches
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.user_service import UserService
from app.utils.constants.error_types import ValidationError
from app.models import User
from app.utils.slack_messages import create_name_blocks, create_registration_blocks

logger = setup_logger(__name__)

class UserHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app
        self.valid_commands = {
            'register': 'Registriere dich als Benutzer. Syntax: /name [dein_name]',
            'change': 'Ändere deinen Namen. Syntax: /name change [neuer_name]',
            'show': 'Zeige deinen aktuellen Namen. Syntax: /name show'
        }

    def handle_name_command(self, ack: Any, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Behandelt Name-Kommandos"""
        try:
            user_id = body.get('user_id')
            command = body.get('text', '').strip()

            with db_session() as session:
                service = UserService(session)
                user = service.get_user(user_id)

                if not command:
                    if user:
                        blocks, _ = create_name_blocks(user.name)
                        self._send_message(user_id, blocks=blocks)
                    else:
                        self._send_message(user_id, blocks=create_registration_blocks())
                    return

                parts = command.split()
                action = parts[0].lower()

                if not user and action != 'register':
                    self._send_message(user_id, blocks=create_registration_blocks())
                    return

                if action == 'register':
                    if len(parts) < 2:
                        self._send_message(user_id, f"❌ Syntax: {self.valid_commands['register']}")
                        return
                    name = ' '.join(parts[1:])
                    service.register_user(user_id, name)
                    blocks, _ = create_name_blocks(name, name)
                    self._send_message(user_id, blocks=blocks)

                elif action == 'change':
                    if len(parts) < 2:
                        self._send_message(user_id, f"❌ Syntax: {self.valid_commands['change']}")
                        return
                    new_name = ' '.join(parts[1:])
                    service.update_user_name(user_id, new_name)
                    blocks, _ = create_name_blocks(user.name, new_name)
                    self._send_message(user_id, blocks=blocks)

                elif action == 'show':
                    blocks, _ = create_name_blocks(user.name)
                    self._send_message(user_id, blocks=blocks)

                else:
                    suggestions = get_close_matches(action, self.valid_commands.keys(), n=1)
                    if suggestions:
                        self._send_message(user_id, f"❌ Ungültiger Befehl. Meintest du `/name {suggestions[0]}`?")
                    else:
                        self._show_name_help(user_id)

        except ValidationError as e:
            self._send_message(user_id, f"❌ Validierungsfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Name command error: {str(e)}")
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _show_name_help(self, user_id: str) -> None:
        """Zeigt die Hilfe-Nachricht an"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Verfügbare Befehle:*"
                }
            }
        ]

        for command, description in self.valid_commands.items():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• `{description}`"
                }
            })

        self._send_message(user_id, blocks=blocks)

    def _send_message(self, user_id: str, text: str = None, blocks: List = None) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=text if text else "Neue Nachricht",
                blocks=blocks
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")