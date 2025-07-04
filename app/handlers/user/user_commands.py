#==========================
# app/handlers/user/user_commands.py
#==========================

from typing import Dict, Any
import logging
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.user_service import UserService
from app.utils.constants.error_types import ValidationError

logger = setup_logger(__name__)

class UserHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app

    def handle_user_command(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Hauptfunktion für den /user Command"""
        try:
            command = body
            user_id = command.get('user_id')

            if not command.get('text'):
                self._show_help(user_id)
                return

            command_parts = command['text'].split()
            sub_command = command_parts[0] if command_parts else None

            if sub_command == 'register':
                self._handle_registration(command)
            elif sub_command == 'name':
                self._handle_name_change(command)
            else:
                self._show_help(user_id)

        except Exception as e:
            logger.error(f"User command error: {str(e)}")
            if 'command' in locals():
                self._send_message(command['user_id'], f"Fehler: {str(e)}")

    def _handle_registration(self, command: Dict[str, Any]) -> None:
        """Verarbeitet die Benutzerregistrierung"""
        try:
            parts = command['text'].split()
            if len(parts) < 2:
                raise ValidationError("Bitte gib einen Namen an. Beispiel: /user register Max")

            user_id = command['user_id']
            name = ' '.join(parts[1:])  # Erlaubt Namen mit Leerzeichen

            with db_session() as session:
                service = UserService(session)
                user = service.register_user(user_id, name)
                session.commit()

                self._send_message(
                    user_id,
                    f"✅ Erfolgreich registriert als: {user.name}"
                )

        except ValidationError as e:
            self._send_message(command['user_id'], f"❌ Registrierungsfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten")

    def _handle_name_change(self, command: Dict[str, Any]) -> None:
        """Verarbeitet Namensänderungen"""
        try:
            parts = command['text'].split()
            if len(parts) < 2:
                raise ValidationError("Bitte gib einen neuen Namen an")

            user_id = command['user_id']
            new_name = ' '.join(parts[1:])

            with db_session() as session:
                service = UserService(session)
                user = service.update_user_name(user_id, new_name)
                session.commit()

                self._send_message(
                    user_id,
                    f"✅ Name geändert zu: {user.name}"
                )

        except ValidationError as e:
            self._send_message(command['user_id'], f"❌ Fehler: {str(e)}")
        except Exception as e:
            logger.error(f"Name change error: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten")

    def _show_help(self, user_id: str) -> None:
        """Zeigt die Hilfe-Nachricht an"""
        help_text = (
            "*Verfügbare Befehle:*\n"
            "• `/user register [name]` Registriere dich als neuer Benutzer\n"
            "• `/user name [neuer name]` Ändere deinen Namen\n"
        )
        self._send_message(user_id, help_text)

    def _send_message(self, user_id: str, text: str) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")