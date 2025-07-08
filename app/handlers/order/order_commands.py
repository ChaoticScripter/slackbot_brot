#==========================
# app/handlers/order/order_commands.py
#==========================

from typing import Dict, Any, List
import logging
from sqlalchemy import func
from app.utils.db.database import db_session
from app.utils.logging.log_config import setup_logger
from app.core.order_service import OrderService
from app.core.saved_order_service import SavedOrderService
from app.utils.constants.error_types import OrderError
from app.models import Order, User
from app.utils.message_blocks.messages import create_order_help_blocks, create_order_list_blocks, \
    create_daily_reminder_blocks, create_remove_preview_blocks
from app.utils.message_blocks.attachments import (
    create_order_confirmation_attachments,
    create_order_list_attachments
)
from datetime import datetime, timedelta, time

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
                    self._send_message(user_id, "Bitte registriere dich zuerst mit dem `/user register` Befehl.")
                    return

            if not command.get('text'):
                self._show_help(user_id)
                return

            command_parts = command['text'].split()
            sub_command = command_parts[0] if command_parts else None

            if sub_command == 'add':
                # Prüfen ob gespeicherte Bestellung
                if len(command_parts) == 2:
                    with db_session() as session:
                        service = SavedOrderService(session)
                        saved = service.get_saved_order(user_id, command_parts[1])
                        if saved:
                            # Originalen add Befehl ausführen
                            command['text'] = f"add {saved.order_string}"

                self._handle_add_order(command)
            elif sub_command == 'save':
                self._handle_save_order(command)
            elif sub_command == 'savelist':
                self._handle_savelist(user_id)
            elif sub_command == 'list':
                self._handle_list_orders(user_id)
            elif sub_command == 'remove':
                self._handle_remove_order(command)
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
                attachments = create_order_confirmation_attachments(order)
                self._send_message(user_id, attachments=attachments)

        except OrderError as e:
            self._send_message(command['user_id'], f"Bestellungsfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_add_order: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_list_orders(self, user_id: str) -> None:
        """Zeigt die Bestellungen der aktuellen Mittwoch-Woche an"""
        try:
            with db_session() as session:
                # Aktuelle Zeit und Wochentag
                now = datetime.now()
                current_weekday = now.weekday()

                # Letzten Mittwoch 10:00 Uhr finden
                days_since_wednesday = (current_weekday - 2) % 7
                last_wednesday = now - timedelta(days=days_since_wednesday)
                period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

                # Wenn es Mittwoch vor 10 Uhr ist, nehmen wir den Mittwoch der Vorwoche
                if current_weekday == 2 and now.hour < 10:
                    period_start = period_start - timedelta(days=7)

                # Nächsten Mittwoch 09:59 Uhr
                period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

                # Bestellungen abrufen
                user = session.query(User).filter_by(slack_id=user_id).first()
                if not user:
                    self._send_message(user_id, "Benutzer nicht gefunden")
                    return

                # Bestellungen abrufen
                orders = session.query(Order) \
                    .filter(
                    Order.user_id == user.user_id,
                    Order.order_date.between(period_start, period_end)
                ) \
                    .order_by(Order.order_date.asc()) \
                    .all()

                # Letzte Bestellung für den Zeitstempel
                latest_order = session.query(Order) \
                    .filter(
                    Order.user_id == user.user_id,
                    Order.order_date.between(period_start, period_end)
                ) \
                    .order_by(Order.order_date.desc()) \
                    .first()

                # Attachments erstellen und senden
                attachments = create_order_list_attachments(orders, period_start, period_end, latest_order)
                self._send_message(user_id, attachments=attachments)

        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            self._send_message(user_id, "Fehler beim Abrufen der Bestellungen.")

    def _show_help(self, user_id: str) -> None:
        """Zeigt die Hilfe-Nachricht an"""
        blocks = create_order_help_blocks()
        self._send_message(user_id, blocks=blocks)

    def _send_message(self, user_id: str, text: str = None, blocks: List = None,
                      attachments: List = None) -> None:
        """Sendet eine Nachricht an einen Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        try:
            # Fallback-Text für verschiedene Nachrichtentypen
            fallback_text = text or self._get_fallback_text(blocks, attachments)

            self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=fallback_text,  # Immer einen Fallback-Text angeben
                blocks=blocks,
                attachments=attachments
            )
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {str(e)}")

    def _get_fallback_text(self, blocks: List = None, attachments: List = None) -> str:
        """Generiert einen sinnvollen Fallback-Text basierend auf dem Nachrichtentyp"""
        if attachments:
            return "Neue Bestellbestätigung"
        elif blocks:
            # Nachrichtentyp aus den Blocks ermitteln
            if blocks and blocks[0].get("text", {}).get("text"):
                # Header-Text als Fallback verwenden
                return blocks[0]["text"]["text"]

        return "Neue Nachricht vom BrotBot"

    def send_daily_reminder(self) -> None:
        """Sendet tägliche Erinnerungen an alle aktiven Benutzer"""
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        logger.info("Sending daily reminder")
        try:
            with db_session() as session:
                users = session.query(User).filter_by(is_away=False).all()
                blocks = create_daily_reminder_blocks()

                for user in users:
                    try:
                        self.slack_app.client.chat_postMessage(
                            channel=user.slack_id,
                            blocks=blocks
                        )
                    except Exception as e:
                        logger.error(f"Failed to send reminder to user {user.slack_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send daily reminders: {str(e)}")

    def _handle_save_order(self, command: Dict[str, Any]) -> None:
        """Speichert eine Bestellvorlage"""
        try:
            text = command.get('text', '').strip()
            if not text.startswith('save '):
                raise OrderError("Ungültiges Format. Verwende: /order save [name] [produkt] [anzahl], ...")

            parts = text[5:].split(' ', 1)
            if len(parts) != 2:
                raise OrderError("Name und Bestellung erforderlich")

            name, order = parts

            with db_session() as session:
                service = SavedOrderService(session)
                saved = service.save_order(command['user_id'], name, order)
                session.commit()

                self._send_message(
                    command['user_id'],
                    text=f"✅ Bestellung '{saved.name}' wurde gespeichert"
                )

        except Exception as e:
            logger.error(f"Save order error: {str(e)}")
            self._send_message(command['user_id'], f"Fehler: {str(e)}")

    def _handle_savelist(self, user_id: str) -> None:
        """Zeigt gespeicherte Bestellvorlagen"""
        try:
            with db_session() as session:
                service = SavedOrderService(session)
                saved_orders = service.list_saved_orders(user_id)

                if not saved_orders:
                    self._send_message(user_id, "Keine gespeicherten Bestellungen gefunden")
                    return

                # Format: "- Name: Bestellung"
                order_list = "\n".join([
                    f"- *{order.name}*: {order.order_string}"
                    for order in saved_orders
                ])

                self._send_message(
                    user_id,
                    text=f"📋 Gespeicherte Bestellungen:\n{order_list}"
                )

        except Exception as e:
            logger.error(f"List saved orders error: {str(e)}")
            self._send_message(user_id, f"Fehler: {str(e)}")

    def _parse_remove_command(self, command_text: str) -> List[Dict[str, Any]]:
        """Parst den Remove-Command und normalisiert die Produktnamen"""
        if not command_text.startswith('remove '):
            raise OrderError("Ungültiges Format. Verwende: /order remove [produkt] [anzahl], ...")

        # Entferne das "remove " am Anfang
        items_text = command_text[7:].strip()
        if not items_text:
            raise OrderError("Keine Produkte angegeben")

        items = []
        parts = items_text.split(',')

        for part in parts:
            item_parts = part.strip().split()
            if len(item_parts) < 2:
                raise OrderError(f"Ungültiges Format bei: {part}. Verwende: [produkt] [anzahl]")

            try:
                # Extrahiere Menge als letztes Element
                quantity = int(item_parts[-1])
                if quantity <= 0:
                    raise OrderError(f"Ungültige Menge für {' '.join(item_parts[:-1])}: {quantity}")

                # Produktname ist alles davor
                product_name = ' '.join(item_parts[:-1])

                items.append({
                    'name': product_name.title(),  # Normalisiere Groß-/Kleinschreibung
                    'quantity': quantity
                })
            except ValueError:
                raise OrderError(f"Ungültige Menge bei: {part}")

        return items

    def _handle_remove_order(self, command: Dict[str, Any]) -> None:
        """Verarbeitet das Entfernen von Produkten"""
        try:
            if not command.get('text', '').startswith('remove '):
                raise OrderError("Ungültiges Format. Verwende: /order remove [produkt] [anzahl]")

            items = []
            parts = command['text'][7:].split(',')  # "remove " entfernen und nach Komma splitten

            for part in parts:
                try:
                    product_parts = part.strip().split()
                    if len(product_parts) < 2:
                        raise OrderError(f"Ungültiges Format bei: {part}. Verwende: [produkt] [anzahl]")

                    quantity = int(product_parts[-1])  # Letztes Element ist die Anzahl
                    product_name = ' '.join(product_parts[:-1])  # Rest ist der Produktname

                    if quantity <= 0:
                        raise OrderError(f"Ungültige Menge für {product_name}: {quantity}")

                    items.append({
                        'name': product_name,
                        'quantity': quantity
                    })
                except ValueError:
                    raise OrderError(f"Ungültiges Format bei: {part}. Verwende: [produkt] [anzahl]")

            with db_session() as session:
                service = OrderService(session)
                order = service.remove_items(command['user_id'], items)
                session.commit()

                # Bestätigung senden
                attachments = create_order_confirmation_attachments(order)
                self._send_message(
                    command['user_id'],
                    text="✅ Produkte wurden erfolgreich aus der Bestellung entfernt",
                    attachments=attachments
                )

        except OrderError as e:
            logger.error(f"Remove order error: {str(e)}")
            self._send_message(command['user_id'], f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_remove_order: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten")