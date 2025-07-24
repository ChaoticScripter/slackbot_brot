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
from app.core.product_service import ProductService
from app.utils.constants.error_types import OrderError
from app.models import Order, User
from app.utils.message_blocks.messages import (
    create_order_help_blocks,
    create_order_list_blocks,
    create_daily_reminder_blocks,
    create_remove_preview_blocks,
    create_order_confirmation_blocks,
    create_product_list_blocks,
    create_product_row_block,
    create_weekly_summary_blocks
)
from datetime import datetime, timedelta, time
import json
from threading import Timer

logger = setup_logger(__name__)

# ==========================
# Hilfsfunktion zum Parsen von /order add Kommandos
# ==========================
# Diese Funktion wandelt den Text eines /order add Kommandos in eine Liste von Produkt-Dictionaries um.
# Beispiel: "add broetchen 2, vollkorn 1" -> [{name: broetchen, quantity: 2}, ...]
def _parse_order_command(text: str) -> List[Dict[str, Any]]:
    """
    Parst den Bestelltext in eine Liste von Produkten und Mengen.
    Erwartet das Format: 'add [produkt] [anzahl], ...'
    Gibt eine Liste von Dicts mit Produktnamen und Mengen zurück.
    """
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
    """
    Haupt-Handler für alle /order-Kommandos.
    Verwaltet das Routing und ruft die passenden Service-Methoden auf.
    """
    def __init__(self, slack_app=None):
        # Referenz auf die Slack-App, um Nachrichten senden zu können
        self.slack_app = slack_app

    def handle_order(self, body: Dict[str, Any], logger: logging.Logger) -> None:
        """
        Haupt-Dispatcher für den /order Command.
        Prüft, welches Subkommando aufgerufen wurde und leitet an die passende Methode weiter.
        body: Slack-Request-Body mit User- und Command-Infos
        logger: Logger-Instanz für Fehlerausgaben
        """
        try:
            command = body
            user_id = command.get('user_id')

            # Prüfe, ob der User existiert (sonst Registrierung fordern)
            with db_session() as session:
                user = session.query(User).filter_by(slack_id=user_id).first()
                if not user:
                    self._send_message(user_id, "Bitte registriere dich zuerst mit dem `/user register` Befehl.")
                    return

            # Wenn kein Sub-Command angegeben, Hilfe anzeigen
            if not command.get('text'):
                self._show_help(user_id)
                return

            command_parts = command['text'].split()
            sub_command = command_parts[0] if command_parts else None

            # Routing zu den jeweiligen Methoden je nach Sub-Command
            if sub_command == 'add':
                # Prüfen ob gespeicherte Bestellung geladen werden soll
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
            elif sub_command == 'products':
                self._handle_product_list(user_id)
            else:
                self._show_help(user_id)

        except Exception as e:
            logger.error(f"Order error: {str(e)}")
            if 'command' in locals():
                self._send_message(command['user_id'], f"Fehler: {str(e)}")

    def _handle_add_order(self, command: Dict[str, Any]) -> None:
        """
        Verarbeitet eine neue Bestellung und bestätigt sie dem User.
        """
        try:
            items = _parse_order_command(command.get('text', ''))
            user_id = command['user_id']

            with db_session() as session:
                service = OrderService(session)
                order = service.add_order(user_id, items)
                session.flush()
                session.commit()
                session.refresh(order)
                # Verwende die neue Block-Funktion für die Bestellbestätigung
                blocks = create_order_confirmation_blocks(order)
                self._send_message(user_id, blocks=blocks)

        except OrderError as e:
            self._send_message(command['user_id'], f"Bestellungsfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_add_order: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_list_orders(self, user_id: str) -> None:
        """
        Zeigt die Bestellungen der aktuellen Woche für den User an.
        Berechnet den Zeitraum von Mittwoch 10:00 bis Mittwoch 09:59 der Folgewoche.
        """
        try:
            with db_session() as session:
                now = datetime.now()
                current_weekday = now.weekday()
                days_since_wednesday = (current_weekday - 2) % 7
                last_wednesday = now - timedelta(days=days_since_wednesday)
                period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

                if current_weekday == 2 and now.hour < 10:
                    period_start = period_start - timedelta(days=7)

                period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

                user = session.query(User).filter_by(slack_id=user_id).first()
                if not user:
                    self._send_message(user_id, "Benutzer nicht gefunden")
                    return

                orders = session.query(Order) \
                    .filter(
                    Order.user_id == user.user_id,
                    Order.order_date.between(period_start, period_end)
                ) \
                    .order_by(Order.order_date.asc()) \
                    .all()

                latest_order = session.query(Order) \
                    .filter(
                    Order.user_id == user.user_id,
                    Order.order_date.between(period_start, period_end)
                ) \
                    .order_by(Order.order_date.desc()) \
                    .first()

                # Verwende die neue Block-Funktion für die Bestellübersicht
                blocks = create_order_list_blocks(orders, period_start, period_end, latest_order)
                self._send_message(user_id, blocks=blocks)

        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            self._send_message(user_id, "Fehler beim Abrufen der Bestellungen.")

    def _show_help(self, user_id: str) -> None:
        """
        Zeigt die Hilfe-Nachricht für /order an.
        """
        blocks = create_order_help_blocks()
        self._send_message(user_id, blocks=blocks)

    def _send_message(self, user_id: str, text: str = None, blocks: List = None,
                      attachments: List = None) -> None:
        """
        Sendet eine Nachricht an einen Benutzer (User oder Admin).
        Verbesserte Fallback-Logik für den Text.
        """
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
        """
        Generiert einen sinnvollen Fallback-Text für Slack-Nachrichten.
        Nutzt Header-Text, falls vorhanden, sonst generischen Text.
        """
        if attachments:
            return "Neue Bestellbestätigung"
        elif blocks:
            # Nachrichtentyp aus den Blocks ermitteln
            if blocks and blocks[0].get("text", {}).get("text"):
                # Header-Text als Fallback verwenden
                return blocks[0]["text"]["text"]

        return "Neue Nachricht vom BrotBot"

    def send_daily_reminder(self) -> None:
        """
        Sendet tägliche Erinnerungen an alle aktiven Benutzer.
        Wird vom Scheduler aufgerufen.
        """
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
        """
        Speichert eine Bestellvorlage für den User.
        """
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
        """
        Zeigt alle gespeicherten Bestellvorlagen des Users an.
        """
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
        """
        Parst den Remove-Command und normalisiert die Produktnamen.
        Erwartet das Format: 'remove [produkt] [anzahl], ...'
        Gibt eine Liste von Dicts mit Produktnamen und Mengen zurück.
        """
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
        """
        Verarbeitet das Entfernen von Produkten aus der Bestellung.
        Zeigt eine Vorschau und setzt einen Timeout für die Bestätigung.
        """
        try:
            if not command.get('text', '').startswith('remove '):
                raise OrderError("Ungültiges Format. Verwende: /order remove [produkt] [anzahl]")

            items = self._parse_remove_command(command['text'])
            user_id = command['user_id']

            with db_session() as session:
                now = datetime.now()
                current_weekday = now.weekday()
                days_since_wednesday = (current_weekday - 2) % 7
                last_wednesday = now - timedelta(days=days_since_wednesday)
                period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

                if current_weekday == 2 and now.hour < 10:
                    period_start = period_start - timedelta(days=7)

                period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

                # Aktuelle Bestellung finden
                service = OrderService(session)
                order = service.get_current_order(user_id, period_start, period_end)
                session.refresh(order)

                # Erst die aktuelle Gesamtbestellung berechnen
                preview_items = {}
                orders = session.query(Order).filter(
                    Order.user_id == order.user_id,
                    Order.order_date.between(period_start, period_end)
                ).all()

                for current_order in orders:
                    for item in current_order.items:
                        name = item.product.name
                        if name in preview_items:
                            preview_items[name] += item.quantity
                        else:
                            preview_items[name] = item.quantity

                # Dann die zu entfernenden Items abziehen
                for item in items:
                    name = item['name']
                    if name in preview_items:
                        if preview_items[name] < item['quantity']:
                            raise OrderError(f"Nicht genügend {name} zum Entfernen vorhanden")
                        preview_items[name] -= item['quantity']
                        if preview_items[name] <= 0:
                            del preview_items[name]

                # Vorschau-Blocks erstellen
                blocks = create_remove_preview_blocks(order, items, preview_items, period_start, period_end)

                # Metadaten vorbereiten
                metadata = {
                    "type": "remove_order",
                    "data": {
                        "items": items,
                        "user_id": user_id
                    }
                }

                # Nachricht mit Timer senden
                result = self.slack_app.client.chat_postMessage(
                    channel=user_id,
                    blocks=blocks,
                    text="Bestellung ändern?",
                    metadata=metadata  # Metadaten direkt als Dictionary übergeben
                )

                # Timer für das Aktualisieren der Nachricht nach 30 Sekunden
                def timeout_callback():
                    try:
                        # Buttons entfernen und Timeout-Nachricht hinzufügen
                        blocks_timeout = blocks[:-2]  # Entferne Timer-Info und Action-Block
                        blocks_timeout.append({
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "⏰ Zeitüberschreitung - Der Vorgang wurde automatisch abgebrochen. Die Bestellung bleibt unverändert."
                            }
                            ]
                        })

                        # Nachricht aktualisieren
                        self.slack_app.client.chat_update(
                            channel=result['channel'],
                            ts=result['ts'],
                            blocks=blocks_timeout,
                            text="Vorgang abgebrochen (Zeitüberschreitung)"
                        )
                    except Exception as e:
                        logger.error(f"Error handling timeout: {str(e)}")

                # Timer starten
                timer = Timer(30.0, timeout_callback)
                timer.start()

        except OrderError as e:
            logger.error(f"Remove order error: {str(e)}")
            self._send_message(command['user_id'], f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_remove_order: {str(e)}")
            self._send_message(command['user_id'], "Ein unerwarteter Fehler ist aufgetreten")

    def _handle_product_list(self, user_id: str) -> None:
        """
        Zeigt eine Liste aller aktiven Produkte an.
        """
        try:
            with db_session() as session:
                # ProductService verwenden um aktive Produkte zu holen
                service = ProductService(session)
                products = service.get_active_products()

                # Basis-Blocks erstellen
                blocks = create_product_list_blocks()

                # Für jedes Produkt einen Block hinzufügen
                for product in products:
                    blocks.append(create_product_row_block(product))

                # Nachricht senden
                self._send_message(user_id, blocks=blocks)

        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            self._send_message(user_id, "Ein Fehler ist beim Abrufen der Produkte aufgetreten")

    def send_weekly_summary(self) -> None:
        """
        Sendet die Wochenbestellung an alle berechtigten Benutzer.
        Wird vom Scheduler aufgerufen.
        """
        if not self.slack_app:
            logger.error("Slack app not initialized")
            return

        logger.info("Sending weekly order summary")
        try:
            with db_session() as session:
                service = OrderService(session)
                users, summary = service.send_weekly_summary()

                if not users or not summary:
                    logger.info("No orders to send or no users to receive summary")
                    return

                # Zeitraum für die Überschrift bestimmen
                now = datetime.now()
                days_since_wednesday = (now.weekday() - 2) % 7
                last_wednesday = now - timedelta(days=days_since_wednesday)
                period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

                # --- NEU: Namen der Besteller ermitteln ---
                # Alle User, die in der Woche bestellt haben
                user_ids_with_orders = set()
                orders = session.query(Order).filter(Order.order_date.between(period_start, period_end)).all()
                for order in orders:
                    if order.user and order.user.name:
                        user_ids_with_orders.add(order.user.name)
                user_names = sorted(user_ids_with_orders)
                # ---

                # Blocks erstellen und an alle berechtigten Benutzer senden
                blocks = create_weekly_summary_blocks(summary, period_start, period_end, user_names)

                for user in users:
                    try:
                        self.slack_app.client.chat_postMessage(
                            channel=user.slack_id,
                            text="Wochenbestellung",
                            blocks=blocks
                        )
                    except Exception as e:
                        logger.error(f"Failed to send weekly summary to user {user.slack_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send weekly summaries: {str(e)}")

# Ende OrderHandler
