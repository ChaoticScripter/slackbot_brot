from typing import Dict, Any, Optional
from app.utils.db.session import db_session
from app.utils.logging.logger import setup_logger
from app.core.users import UserService
from app.utils.constants.exceptions import ValidationError, DatabaseError
from app.utils.formatting import create_name_blocks, create_registration_blocks

logger = setup_logger(__name__)


class UserHandler:
    async def handle_name_command(self, ack: callable, respond: callable, command: Dict[str, Any]) -> None:
        """Behandelt den /name Command"""
        await ack()
        user_id = command["user_id"]
        text = command.get("text", "").strip()

        try:
            with db_session() as session:
                service = UserService(session)
                user = service.get_user(user_id)

                if not user:
                    blocks = create_registration_blocks()
                    await respond(blocks=blocks)
                    return

                if text.startswith("change"):
                    await self._handle_name_change(respond, user, text[6:].strip(), service)
                    return

                blocks, attachments = create_name_blocks(current_name=user.name)
                await respond(blocks=blocks, attachments=attachments)

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            await respond(str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            await respond("Ein Datenbankfehler ist aufgetreten.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await respond("Ein unerwarteter Fehler ist aufgetreten.")

    async def handle_registration(self, ack: callable, body: Dict[str, Any], respond: callable) -> None:
        """Behandelt die Benutzerregistrierung"""
        await ack()

        try:
            user_id = body["user"]["id"]
            name = body.get("text", "").strip()

            if not name:
                await respond("Bitte gib einen Namen ein.")
                return

            with db_session() as session:
                service = UserService(session)
                user = service.register_user(user_id, name)

                blocks, attachments = create_name_blocks(current_name=user.name)
                await respond(blocks=blocks, attachments=attachments)

        except ValidationError as e:
            logger.warning(f"Registration error: {str(e)}")
            await respond(str(e))
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            await respond("Fehler bei der Registrierung.")

    async def _handle_name_change(self, respond: callable, user: Any, new_name: str,
                                  service: UserService) -> None:
        """Behandelt die Namensänderung"""
        if not new_name:
            await respond("Bitte gib einen neuen Namen an.")
            return

        old_name = user.name
        user = service.update_user_name(user.slack_id, new_name)

        blocks, attachments = create_name_blocks(current_name=old_name, new_name=new_name)
        await respond(blocks=blocks, attachments=attachments)