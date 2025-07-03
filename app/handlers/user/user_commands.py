# ==========================
# app/handlers/user/user_commands.py
# ==========================

from typing import Dict, Any
import logging
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.user_service import UserService
from app.utils.message_blocks.attachments import create_name_blocks, create_registration_blocks

logger = setup_logger(__name__)


class UserHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app

    def handle_user_command(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Behandelt den /user Command (vorher /name)"""
        try:
            user_id = body.get('user_id')
            text = body.get('text', '').strip()

            with db_session() as session:
                service = UserService(session)
                user = service.get_user(user_id)

                # Benutzer muss zuerst registriert werden
                if not user and text != 'register':
                    blocks = create_registration_blocks()
                    self._send_message(user_id, blocks=blocks)
                    return

                # User Command verarbeiten
                if not text:
                    blocks = create_name_blocks(current_name=user.name if user else None)
                    self._send_message(user_id, blocks=blocks)
                    return

                parts = text.split()
                action = parts[0].lower()

                if action == 'changename' and len(parts) > 1:
                    # Namen ändern
                    new_name = ' '.join(parts[1:])
                    old_name = user.name
                    user = service.update_user_name(user_id, new_name)
                    session.commit()

                    blocks = create_name_blocks(current_name=old_name, new_name=new_name)
                    self._send_message(user_id, blocks=blocks)

                elif action == 'register' and len(parts) > 1:
                    # Neuen Benutzer registrieren
                    if user:
                        self._send_message(user_id, text="Du bist bereits registriert!")
                        return

                    name = ' '.join(parts[1:])
                    user = service.register_user(user_id, name)
                    session.commit()

                    blocks = create_name_blocks(current_name=name)
                    self._send_message(user_id, blocks=blocks)
                else:
                    # Hilfe anzeigen
                    blocks = create_name_blocks()
                    self._send_message(user_id, blocks=blocks)

        except Exception as e:
            logger.error(f"Name command error: {str(e)}")
            self._send_message(user_id, text=f"Fehler: {str(e)}")

    def _send_message(self, user_id: str, text: str = None, blocks: list = None) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            # Fallback-Text für Block-Nachrichten
            fallback_text = text or "Neue Nachricht vom BrotBot"

            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=fallback_text,
                blocks=blocks
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")