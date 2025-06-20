#==========================
# app/handlers/order/order_commands.py
#==========================

from typing import Dict, Any, List
import logging
from difflib import get_close_matches
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.core.order_service import OrderService
from app.models import User, Product, Order
from app.utils.constants.error_types import OrderError
from datetime import datetime, timedelta

logger = setup_logger(__name__)


class OrderHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app
        self.valid_commands = {
            'add': 'Neue Bestellung aufgeben. Syntax: /order add [produkt] [anzahl] (, [produkt] [anzahl], ...)',
            'list': 'Aktuelle Bestellungen anzeigen. Syntax: /order list',
            'help': 'Zeigt diese Hilfe an. Syntax: /order help'
        }

    def handle_order(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Behandelt Order-Kommandos"""
        try:
            user_id = body.get('user_id')
            command = body.get('text', '').strip()

            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id).first()
                if not user:
                    self._send_message(user_id, "❌ Bitte registriere dich zuerst mit dem `/name` Befehl.")
                    return

                if not command:
                    self._show_order_help(user_id)
                    return

                parts = command.split()
                action = parts[0].lower()

                if action not in self.valid_commands:
                    suggestions = get_close_matches(action, self.valid_commands.keys(), n=1)
                    if suggestions:
                        self._send_message(user_id, f"❌ Ungültiger Befehl. Meintest du `/order {suggestions[0]}`?")
                    else:
                        self._show_order_help(user_id)
                    return

                if action == 'add':
                    self._handle_add_order(session, user_id, ' '.join(parts[1:]))
                elif action == 'list':
                    self._handle_list_orders(session, user_id)
                elif action == 'help':
                    self._show_order_help(user_id)

        except Exception as e:
            logger.error(f"Order error: {str(e)}")
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _handle_add_order(self, session: Any, user_id: str, order_text: str) -> None:
        """Verarbeitet neue Bestellungen"""
        try:
            if not order_text:
                self._send_message(user_id, f"❌ Syntax: {self.valid_commands['add']}")
                return

            service = OrderService(session)
            items = self._parse_order_text(order_text)

            # Produktnamen validieren
            available_products = {p.name.lower(): p.name for p in session.query(Product).filter_by(active=True).all()}
            for item in items:
                product_name = item['name'].lower()
                if product_name not in available_products:
                    similar = get_close_matches(product_name, available_products.keys(), n=1)
                    if similar:
                        self._send_message(user_id,
                                           f"❌ Produkt nicht gefunden. Meintest du '{available_products[similar[0]]}'?")
                    else:
                        self._send_message(user_id, f"❌ Produkt '{item['name']}' nicht verfügbar")
                    return

            order = service.add_order(user_id, items)
            self._send_order_confirmation(user_id, order)

        except OrderError as e:
            self._send_message(user_id, f"❌ Bestellfehler: {str(e)}")
        except Exception as e:
            self._send_message(user_id, f"❌ Fehler: {str(e)}")

    def _handle_list_orders(self, session: Any, user_id: str) -> None:
        """Zeigt die aktuellen Bestellungen an"""
        try:
            service = OrderService(session)
            orders = service.get_user_orders(user_id)
            self._send_order_list(user_id, orders)
        except Exception as e:
            self._send_message(user_id, f"❌ Fehler beim Abrufen der Bestellungen: {str(e)}")

    def _parse_order_text(self, text: str) -> List[Dict[str, Any]]:
        """Parst den Bestelltext in eine Liste von Produkten und Mengen"""
        items = []
        parts = text.split(',')

        for part in parts:
            try:
                product_parts = part.strip().split()
                if len(product_parts) < 2:
                    raise OrderError(f"Ungültiges Format bei: {part}")

                name = ' '.join(product_parts[:-1])
                quantity = int(product_parts[-1])

                if quantity <= 0:
                    raise OrderError(f"❌ Ungültige Menge für {name}: {quantity}")

                items.append({
                    'name': name,
                    'quantity': quantity
                })
            except ValueError:
                raise OrderError(f"❌ Ungültiges Format bei: {part}. Verwende: [produkt] [anzahl]")

        return items

    def _send_order_confirmation(self, user_id: str, order: Order) -> None:
        """Sendet eine Bestellbestätigung"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ *Bestellung erfolgreich aufgegeben!*"
                }
            }
        ]

        order_items = []
        for item in order.items:
            order_items.append(f"• {item.product.name}: {item.quantity}x")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bestelldetails:*\n" + "\n".join(order_items)
            }
        })

        self._send_message(user_id, blocks=blocks)

    def _send_order_list(self, user_id: str, orders: List[Order]) -> None:
        """Sendet eine zusammengefasste Liste aller Bestellungen"""
        if not orders:
            self._send_message(user_id, "❌ Keine aktiven Bestellungen vorhanden")
            return

        # Nächsten Mittwoch ermitteln
        now = datetime.now()
        next_wednesday = now
        while next_wednesday.weekday() != 2:  # 2 = Mittwoch
            next_wednesday += timedelta(days=1)
        next_wednesday = next_wednesday.replace(hour=9, minute=59, second=59)

        # Wenn aktueller Tag Mittwoch nach 10:00 Uhr, dann nächste Woche
        if now.weekday() == 2 and now.hour >= 10:
            next_wednesday += timedelta(days=7)

        # Bestellungen zusammenfassen
        order_summary = {}
        for order in orders:
            # Alle Bestellungen werden unter dem nächsten Mittwoch gruppiert
            if order_summary == {}:
                order_summary[next_wednesday] = {}

            # Produkte zusammenfassen
            for item in order.items:
                product_name = item.product.name
                if product_name in order_summary[next_wednesday]:
                    order_summary[next_wednesday][product_name] += item.quantity
                else:
                    order_summary[next_wednesday][product_name] = item.quantity

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📋 *Deine Bestellungen:*"
                }
            }
        ]

        # Zusammengefasste Bestellungen ausgeben
        for date, products in order_summary.items():
            order_items = []
            for product_name, quantity in products.items():
                order_items.append(f"• {product_name}: {quantity}x")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Bestellung für das Frühstück am {date.strftime('%d.%m.%Y')}:*\n" + "\n".join(order_items)
                }
            })

        self._send_message(user_id, blocks=blocks)

    def _show_order_help(self, user_id: str) -> None:
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

    def send_daily_reminder(self) -> None:
        """Sendet tägliche Erinnerungen"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            with db_session() as session:
                users = session.query(User).filter_by(is_away=False).all()

                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "🔔 *Tägliche Erinnerung*\nVergiss nicht, deine Bestellung aufzugeben!"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Nutze `{self.valid_commands['add']}`"
                        }
                    }
                ]

                for user in users:
                    try:
                        self._send_message(user.slack_id, blocks=blocks)
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {user.slack_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send daily reminders: {str(e)}")