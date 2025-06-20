#==========================
# app/handlers/order/order_commands.py
#==========================

from typing import Dict, Any, List
import logging
from datetime import datetime
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.order_service import OrderService
from app.utils.constants.error_types import OrderError
from app.models import Order, User

logger = setup_logger(__name__)


def _parse_order_command(text: str) -> List[Dict[str, Any]]:
    """Parst den Bestelltext in eine Liste von Produkten und Mengen"""
    if not text.startswith('add '):
        raise OrderError("Ungültiges Bestellformat. Verwende: /order add [produkt] [anzahl]")

    items = []
    parts = text[4:].split(',')

    for part in parts:
        try:
            name, quantity = part.strip().split()
            quantity = int(quantity)
            if quantity <= 0:
                raise OrderError(f"Ungültige Menge für {name}: {quantity}")
            items.append({
                'name': name.lower(),
                'quantity': quantity
            })
        except ValueError:
            raise OrderError(f"Ungültiges Format bei: {part}. Verwende: [produkt] [anzahl]")

    return items


def _create_order_list_blocks(orders: List[Order]) -> List[Dict[str, Any]]:
    """Erstellt die Slack-Blocks für die Bestellungsübersicht"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "📋 *Deine Bestellung für diese Woche:*"
            }
        },
        {
            "type": "divider"
        }
    ]

    # Produkte nach Name gruppieren
    all_items = {}
    for order in orders:
        for item in order.items:
            product_name = item.product.name
            if product_name in all_items:
                all_items[product_name] += item.quantity
            else:
                all_items[product_name] = item.quantity

    # Sortierte Bestellübersicht erstellen
    if all_items:
        order_details = []
        for product_name, quantity in sorted(all_items.items()):
            order_details.append(f"• {product_name}: {quantity}x")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(order_details)
            }
        })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "❌ Keine aktiven Bestellungen vorhanden."
            }
        })

    return blocks


def _create_order_confirmation_blocks(order: Order) -> List[Dict[str, Any]]:
    """Erstellt die Slack-Blocks für die Bestellbestätigung"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "✅ *Bestellung erfolgreich aufgegeben!*"
            }
        },
        {
            "type": "divider"
        }
    ]

    order_details = []
    for item in order.items:
        order_details.append(f"• {item.product.name}: {item.quantity}x")

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Bestelldetails:*\n" + "\n".join(order_details)
        }
    })

    return blocks


class OrderHandler:
    def __init__(self, slack_app=None):
        self.slack_app = slack_app

    def handle_order(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """Synchrone Hauptfunktion für den /order Command"""
        try:
            command = body
            user_id = command.get('user_id')

            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id).first()
                if not user:
                    self._send_message(user_id, "Bitte registriere dich zuerst mit dem `/name` Befehl.")
                    return

            if not command.get('text'):
                self._show_help(user_id)
                return

            command_parts = command['text'].split()
            sub_command = command_parts[0] if command_parts else None

            if sub_command == 'add':
                self._handle_add_order(command)
            elif sub_command == 'list':
                self._handle_list_orders(user_id)
            else:
                self._show_help(user_id)

        except Exception as e:
            logger.error(f"Order error: {str(e)}")
            if 'command' in locals():
                self._send_message(command['user_id'], f"Fehler: {str(e)}")

    def _handle_add_order(self, command: Dict[str, Any]) -> None:
        """Verarbeitet eine neue Bestellung"""
        try:
            items = _parse_order_command(command.get('text', ''))
            user_id = command['user_id']

            with db_session() as session:
                service = OrderService(session)
                order = service.add_order(user_id, items)
                session.flush()
                session.commit()
                session.refresh(order)
                blocks = _create_order_confirmation_blocks(order)
                self._send_message(user_id, blocks=blocks)

        except OrderError as e:
            self._send_message(command['user_id'], f"Bestellungsfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_add_order: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_list_orders(self, user_id: str) -> None:
        """Zeigt die aktuellen Bestellungen des Benutzers an"""
        try:
            with db_session() as session:
                service = OrderService(session)
                orders = service.get_user_orders(user_id)
                blocks = _create_order_list_blocks(orders)
                self._send_message(user_id, blocks=blocks)

        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            self._send_message(user_id, "Fehler beim Abrufen der Bestellungen.")

    def _show_help(self, user_id: str) -> None:
        """Zeigt die Hilfe-Nachricht an"""
        help_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Verfügbare Befehle:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "• `/order add [produkt] [anzahl]` - Neue Bestellung aufgeben\n"
                        "• `/order list` - Deine Bestellungen anzeigen\n"
                        "• `/order help` - Diese Hilfe anzeigen"
                    )
                }
            }
        ]
        self._send_message(user_id, blocks=help_blocks)

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
        """Sendet tägliche Erinnerungen an alle aktiven Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        logger.info("Sending daily reminder")
        try:
            with db_session() as session:
                users = session.query(User).filter_by(is_away=False).all()

                reminder_blocks = [
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
                            "text": "Nutze `/order add [produkt] [anzahl]` um zu bestellen."
                        }
                    }
                ]

                for user in users:
                    try:
                        self.slack_app.client.chat_postMessage(
                            channel=user.slack_id,
                            blocks=reminder_blocks
                        )
                    except Exception as e:
                        logger.error(f"Failed to send reminder to user {user.slack_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send daily reminders: {str(e)}")