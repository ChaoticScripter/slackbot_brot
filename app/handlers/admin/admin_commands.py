#==========================
# app/handlers/admin/admin_commands.py
#==========================

from typing import Dict, Any, List
import logging
from difflib import get_close_matches
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.core.product_service import ProductService
from app.models import User, Product
from app.utils.constants.error_types import ValidationError

logger = setup_logger(__name__)

class AdminHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app
        self.valid_commands = {
            'product': {
                'add': 'Fügt ein neues Produkt hinzu. Syntax: /admin product add [name] [beschreibung]',
                'list': 'Zeigt alle aktiven Produkte an. Syntax: /admin product list',
                'delete': 'Löscht ein Produkt. Syntax: /admin product delete [name]',
                'update': 'Aktualisiert ein Produkt. Syntax: /admin product update [name] [neue_beschreibung]'
            }
        }

    def handle_admin(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Behandelt Admin-Kommandos"""
        try:
            user_id = body.get('user_id')
            command = body.get('text', '').strip()

            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id, is_admin=True).first()
                if not user:
                    self._send_message(user_id, "❌ Du hast keine Admin-Berechtigung.")
                    return

                if not command:
                    self._show_admin_help(user_id)
                    return

                parts = command.split()
                action = parts[0].lower()

                if action not in self.valid_commands:
                    suggestions = get_close_matches(action, self.valid_commands.keys(), n=1)
                    if suggestions:
                        self._send_message(user_id, f"❌ Ungültiger Befehl. Meintest du `/admin {suggestions[0]}`?")
                    else:
                        self._show_admin_help(user_id)
                    return

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
            self._send_message(user_id, self.valid_commands['product']['add'])
            return

        service = ProductService(session)
        action = args[0].lower()

        try:
            if action == 'add':
                if len(args) < 3:
                    self._send_message(user_id,
                        "❌ Syntax: `/admin product add [name] [beschreibung]`\n"
                        "Beispiel: `/admin product add Roggenbrot Leckeres Roggenbrot aus der Backstube`")
                    return

                name = args[1]
                description = ' '.join(args[2:])

                # Ähnliche Produkte finden
                existing_products = session.query(Product).all()
                similar_products = get_close_matches(name, [p.name for p in existing_products], n=1)
                if similar_products:
                    self._send_message(user_id,
                        f"⚠️ Warnung: Es gibt bereits ein ähnliches Produkt: '{similar_products[0]}'\n"
                        f"Bitte wähle einen eindeutigen Namen oder aktualisiere das bestehende Produkt.")
                    return

                product = service.add_product(name, description)
                self._send_message(user_id,
                    f"✅ Produkt hinzugefügt:\n"
                    f"• Name: {product.name}\n"
                    f"• Beschreibung: {product.description}")

            elif action == 'list':
                products = service.get_active_products()
                self._send_product_list(user_id, products)

            elif action == 'delete':
                if len(args) < 2:
                    self._send_message(user_id, "❌ Syntax: `/admin product delete [name]`")
                    return
                product_name = args[1]
                product = session.query(Product).filter_by(name=product_name).first()
                if not product:
                    similar = get_close_matches(product_name,
                                             [p.name for p in service.get_active_products()],
                                             n=1)
                    if similar:
                        self._send_message(user_id,
                            f"❌ Produkt nicht gefunden. Meintest du '{similar[0]}'?")
                    else:
                        self._send_message(user_id, f"❌ Produkt '{product_name}' nicht gefunden")
                    return
                product.active = False
                self._send_message(user_id, f"✅ Produkt '{product.name}' wurde deaktiviert")

            elif action == 'update':
                if len(args) < 3:
                    self._send_message(user_id, "❌ Syntax: `/admin product update [name] [neue_beschreibung]`")
                    return
                product_name = args[1]
                new_description = ' '.join(args[2:])
                product = session.query(Product).filter_by(name=product_name).first()
                if not product:
                    similar = get_close_matches(product_name,
                                             [p.name for p in service.get_active_products()],
                                             n=1)
                    if similar:
                        self._send_message(user_id,
                            f"❌ Produkt nicht gefunden. Meintest du '{similar[0]}'?")
                    else:
                        self._send_message(user_id, f"❌ Produkt '{product_name}' nicht gefunden")
                    return
                product.description = new_description
                self._send_message(user_id,
                    f"✅ Produkt aktualisiert:\n"
                    f"• Name: {product.name}\n"
                    f"• Neue Beschreibung: {product.description}")

            else:
                closest = get_close_matches(action, self.valid_commands['product'].keys(), n=1)
                if closest:
                    self._send_message(user_id, f"❌ Ungültiger Befehl. Meintest du `/admin product {closest[0]}`?")
                else:
                    self._show_admin_help(user_id)

        except ValidationError as e:
            self._send_message(user_id, f"❌ Validierungsfehler: {str(e)}")
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

        for product in products:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• *{product.name}*\n  {product.description or 'Keine Beschreibung'}"
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
            }
        ]

        for command, subcommands in self.valid_commands.items():
            command_text = []
            for subcommand, description in subcommands.items():
                command_text.append(f"• `{description}`")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(command_text)
                }
            })

        self._send_message(user_id, blocks=blocks)