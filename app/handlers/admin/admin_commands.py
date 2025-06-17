#==========================
# app/handlers/admin/admin_commands.py
#==========================

from typing import Dict, Any
import logging
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.product_service import ProductService
from app.utils.constants.error_types import ValidationError

logger = setup_logger(__name__)


class AdminHandler:
    async def handle_admin_command(self, ack: callable, respond: callable, command: Dict[str, Any]) -> None:
        await ack()

        if not await self._check_admin_permission(command['user_id']):
            await respond("Keine Admin-Berechtigung")
            return

        try:
            args = command.get('text', '').split()
            if len(args) < 2:
                await respond("Ungültiger Admin-Befehl")
                return

            sub_command = args[1]

            if sub_command == 'product_add':
                await self._handle_product_add(respond, args[2:])
            else:
                await respond("Unbekannter Admin-Befehl")

        except Exception as e:
            logger.error(f"Admin error: {str(e)}")
            await respond(f"Fehler: {str(e)}")