# ==========================
# app/handlers/user/user_commands.py
# ==========================

from typing import Dict, Any
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.user_service import UserService
from app.utils.constants.error_types import ValidationError, DatabaseError
from app.utils.message_blocks.messages import create_name_blocks, create_registration_blocks

logger = setup_logger(__name__)


class UserHandler:
    def handle_name_command(self, body: Dict[str, Any], logger) -> None:
        """Behandelt den /name Command"""
        user_id = body["user_id"]
        text = body.get("text", "").strip()

        try:
            with db_session() as session:
                service = UserService(session)
                user = service.get_user(user_id)

                if not user:
                    blocks = create_registration_blocks()
                    self._send_message(user_id, blocks=blocks)
                    return

                if text.startswith("change"):
                    self._handle_name_change(user, text[6:].strip(), service)
                    return

                blocks = create_name_blocks(current_name=user.name)
                self._send_message(user_id, blocks=blocks)

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            self._send_message(user_id, str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            self._send_message(user_id, "Ein Datenbankfehler ist aufgetreten.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self._send_message(user_id, "Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_name_change(self, user: Any, new_name: str, service: UserService) -> None:
        """Behandelt die Namensänderung"""
        if not new_name:
            self._send_message(user.slack_id, "Bitte gib einen neuen Namen an.")
            return

        old_name = user.name
        user = service.update_user_name(user.slack_id, new_name)
        blocks = create_name_blocks(current_name=old_name, new_name=new_name)
        self._send_message(user.slack_id, blocks=blocks)

    def _send_message(self, user_id: str, text: str = None, blocks: list = None) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        # Hier Implementierung für das Senden der Nachricht
        pass