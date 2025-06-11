# app/handlers/order/handlers.py
from typing import Dict, Any, List  # List hinzugefügt
import logging
from app.utils.db.session import db_session
from app.utils.logging.logger import setup_logger
from app.core.orders import OrderService
from app.utils.constants.exceptions import OrderError
from app.models import Order  # Order Model für Type Hints importiert
from app.bot import app as slack_app

logger = setup_logger(__name__)


class OrderHandler:
    async def send_daily_reminder(self) -> None:
        """Sendet die tägliche Erinnerung für Brötchenbestellungen"""
        logger.info("Sending daily reminder")

        try:
            with db_session() as session:
                # Aktive Benutzer abrufen, die nicht abwesend sind
                users = session.query(User).filter_by(is_away=False).all()

                for user in users:
                    try:
                        await slack_app.client.chat_postMessage(
                            channel=user.slack_id,
                            blocks=[
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "🥐 Zeit für die tägliche Brötchenbestellung!"
                                    }
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "Bestelle mit:\n`/order add normal 2, vollkorn 1`"
                                    }
                                }
                            ]
                        )
                    except Exception as e:
                        logger.error(f"Failed to send reminder to user {user.slack_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send daily reminders: {str(e)}")

    async def handle_order_add(self, ack: callable, respond: callable, command: Dict[str, Any]) -> None:
        await ack()

        try:
            items = self._parse_order_command(command.get('text', ''))

            with db_session() as session:
                service = OrderService(session)
                order = service.add_order(command['user_id'], items)

                await respond(
                    blocks=self._create_order_confirmation_blocks(order)
                )

        except OrderError as e:
            logger.warning(f"Order error: {str(e)}")
            await respond(f"Fehler bei der Bestellung: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await respond("Ein unerwarteter Fehler ist aufgetreten.")

    def _parse_order_command(self, text: str) -> List[Dict[str, Any]]:
        if not text.startswith('add '):
            raise OrderError("Ungültiges Bestellformat")

        items = []
        parts = text[4:].split(',')

        for part in parts:
            try:
                name, quantity = part.strip().split()
                items.append({
                    'name': name,
                    'quantity': int(quantity)
                })
            except ValueError:
                raise OrderError(f"Ungültiges Format: {part}")

        return items

    def _create_order_confirmation_blocks(self, order: Order) -> List[Dict[str, Any]]:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ Bestellung erfolgreich aufgegeben!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Bestellnummer:* {order.order_id}"
                }
            }
        ]