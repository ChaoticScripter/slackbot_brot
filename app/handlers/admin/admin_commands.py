#==========================
# app/handlers/admin/admin_commands.py
#==========================

from typing import Dict, Any, List
import logging
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.core.product_service import ProductService
from app.models import User
from app.utils.message_blocks.messages import create_admin_help_blocks, create_product_list_blocks

logger = setup_logger(__name__)

class AdminHandler:
    """
    Handler für alle Admin-Kommandos, z.B. Produktverwaltung.
    Wird über den /admin Slack-Befehl aufgerufen.
    Kapselt die gesamte Logik für Admin-Befehle und prüft Adminrechte.
    """
    def __init__(self, slack_app=None):
        # Referenz auf die Slack-App, um Nachrichten senden zu können
        self.slack_app = slack_app

    def handle_admin(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """
        Haupt-Dispatcher für Admin-Kommandos. Prüft Adminrechte und leitet an die passende Funktion weiter.
        body: Slack-Request-Body mit User- und Command-Infos
        logger: Logger-Instanz für Fehlerausgaben
        Ablauf:
        1. Holt die Slack-User-ID und das eingegebene Kommando
        2. Prüft, ob der User Adminrechte hat
        3. Leitet an die passende Subfunktion weiter (z.B. Produktverwaltung)
        4. Zeigt Hilfe, wenn kein oder ein ungültiges Kommando eingegeben wurde
        """
        try:
            user_id = body.get('user_id')
            command = body.get('text', '').strip()

            # Datenbank-Session öffnen und Adminrechte prüfen
            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id, is_admin=True).first()
                if not user:
                    self._send_message(user_id, "❌ Keine Admin-Berechtigung")
                    return

                # Wenn kein Sub-Command angegeben, Hilfe anzeigen
                if not command:
                    self._show_admin_help(user_id)
                    return

                parts = command.split()
                action = parts[0]

                # Produkt-Kommandos weiterleiten
                if action == 'product':
                    self._handle_product_command(session, user_id, parts[1:])
                else:
                    self._show_admin_help(user_id)

        except Exception as e:
            logger.error(f"Admin error: {str(e)}")
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _handle_product_command(self, session, user_id: str, args: List[str]) -> None:
        """
        Verarbeitet Produkt-bezogene Admin-Kommandos wie Hinzufügen und Listen von Produkten.
        session: Aktive DB-Session
        user_id: Slack-ID des Admins
        args: Argumente nach 'product' (z.B. ['add', 'Brötchen'])
        Ablauf:
        1. Prüft, ob ein Subkommando (add/list) angegeben ist
        2. Leitet an die jeweilige Produktfunktion weiter
        3. Zeigt Hilfe bei ungültigen Kommandos
        """
        if not args:
            self._send_message(user_id, "❌ Ungültiges Produktkommando")
            return

        service = ProductService(session)
        action = args[0]

        try:
            # Produkt hinzufügen: /admin product add [name] [beschreibung]
            # Beschreibung ist optional, kann aber mitgegeben werden
            if action == 'add' and len(args) >= 2:
                name = args[1]
                description = args[2] if len(args) > 2 else None
                product = service.add_product(name, description)
                self._send_message(user_id, f"✅ Produkt '{product.name}' wurde hinzugefügt")
            # Produktliste anzeigen: /admin product list
            elif action == 'list':
                products = service.get_active_products()
                self._send_product_list(user_id, products)
            else:
                self._show_admin_help(user_id)
        except Exception as e:
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _send_message(self, user_id: str, text: str = None, blocks: List = None) -> None:
        """
        Sendet eine Nachricht an einen Benutzer (Admin).
        user_id: Slack-ID
        text: Fallback-Text
        blocks: Slack-Blocks für formatierte Nachrichten
        Verbesserte Fallback-Logik und Fehlerausgabe.
        """
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            # Fallback-Text: Nutze Text, sonst generischen Hinweis
            fallback_text = text if text else "Neue Admin-Nachricht"
            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=fallback_text,
                blocks=blocks
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")

    def _send_product_list(self, user_id: str, products: List) -> None:
        """
        Sendet eine formatierte Produktliste an den Admin.
        Nutzt die Message-Block-Funktion für die Produktübersicht.
        """
        blocks = create_product_list_blocks(products)
        self._send_message(user_id, blocks=blocks)

    def _show_admin_help(self, user_id: str) -> None:
        """
        Zeigt die Admin-Hilfenachricht an.
        Nutzt die Message-Block-Funktion für die Admin-Hilfe.
        """
        blocks = create_admin_help_blocks()
        self._send_message(user_id, blocks=blocks)