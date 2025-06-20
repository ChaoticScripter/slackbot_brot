#==========================
# app/handlers/admin/admin_commands.py
#==========================

from typing import Dict, Any, List
import logging
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.core.product_service import ProductService
from app.models import User

logger = setup_logger(__name__)

class AdminHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app

    def handle_admin(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Behandelt Admin-Kommandos"""
        try:
            user_id = body.get('user_id')
            command = body.get('text', '').strip()

            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id, is_admin=True).first()
                if not user:
                    self._send_message(user_id, "❌ Keine Admin-Berechtigung")
                    return

                if not command:
                    self._show_admin_help(user_id)
                    return

                parts = command.split()
                action = parts[0]

                if action == 'product':
                    self._handle_product_command(session, user_id, parts[1:])
                else:
                    self._show_admin_help(user_id)

        except Exception as e:
            logger.error(f"Admin error: {str(e)}")
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _handle_product_command(self, session, user_id: str, args: List[str]) -> None:
        """Verarbeitet Produkt-bezogene Admin-Kommandos"""
        if not args:
            self._send_message(user_id, "❌ Ungültiges Produktkommando")
            return

        service = ProductService(session)
        action = args[0]

        try:
            if action == 'add' and len(args) >= 2:
                product = service.add_product(args[1])
                self._send_message(user_id, f"✅ Produkt '{product.name}' wurde hinzugefügt")
            elif action == 'list':
                products = service.get_active_products()
                self._send_product_list(user_id, products)
            else:
                self._show_admin_help(user_id)
        except Exception as e:
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _send_message(self, user_id: str, text: str = None, blocks: List = None) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=text if text else "Neue Admin-Nachricht",
                blocks=blocks
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")

    def _send_product_list(self, user_id: str, products: List) -> None:
        """Sendet eine formatierte Produktliste"""
        if not products:
            self._send_message(user_id, "Keine aktiven Produkte vorhanden")
            return

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Aktive Produkte:*"
                }
            }
        ]

        product_list = []
        for product in products:
            product_list.append(f"• {product.name}")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(product_list)
            }
        })

        self._send_message(user_id, blocks=blocks)

    def _show_admin_help(self, user_id: str) -> None:
        """Zeigt Admin-Hilfenachricht"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Admin Befehle:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `/admin product add [name]` - Neues Produkt hinzufügen\n"
                           "• `/admin product list` - Alle Produkte anzeigen\n"
                           "• `/admin help` - Diese Hilfe anzeigen"
                }
            }
        ]
        self._send_message(user_id, blocks=blocks)