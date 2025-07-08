#==========================
# app/core/order_service.py
#==========================

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Product, User
from app.utils.constants.error_types import OrderError


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def add_order(self, user_id: str, items: List[Dict[str, Any]]) -> Order:
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Order erstellen und zur Session hinzufügen
        order = Order(user_id=user.user_id, order_date=datetime.now())
        self.session.add(order)
        # Session flushen um order_id zu generieren
        self.session.flush()

        for item in items:
            product = self.session.query(Product).filter_by(
                name=item['name'],
                active=True
            ).first()
            if not product:
                raise OrderError(f"Produkt {item['name']} nicht gefunden")

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=item['quantity']
            )
            self.session.add(order_item)

        # Änderungen in der Session speichern
        self.session.flush()
        return order

    def get_user_orders(self, user_id: str) -> List[Order]:
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return []
        return self.session.query(Order).filter_by(user_id=user.user_id).all()

    def remove_items_preview(self, user_id: str, items: List[Dict[str, Any]]) -> Tuple[Order, List[Dict[str, Any]]]:
        """Erstellt eine Vorschau der Bestellung nach dem Entfernen von Produkten"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Aktuelle Wochenbestellung finden
        current_week_order = self._get_current_week_order(user.user_id)
        if not current_week_order:
            raise OrderError("Keine aktive Bestellung gefunden")

        # Überprüfen ob genügend Produkte zum Entfernen vorhanden sind
        items_to_remove = []
        for item in items:
            product = self.session.query(Product).filter(
                # Case-insensitive Vergleich des Produktnamens
                Product.name.ilike(item['name'])
            ).first()

            if not product:
                raise OrderError(f"Produkt {item['name']} nicht gefunden")

            existing_item = next(
                # Case-insensitive Vergleich bei der Suche
                (i for i in current_week_order.items if i.product.name.lower() == item['name'].lower()),
                None
            )
            if not existing_item:
                raise OrderError(f"Produkt {item['name']} ist nicht in der Bestellung vorhanden")
            if existing_item.quantity < item['quantity']:
                raise OrderError(f"Nicht genügend {item['name']} zum Entfernen vorhanden")

            items_to_remove.append({
                'item': existing_item,
                'quantity': item['quantity']
            })

        return current_week_order, items_to_remove

    # app/core/order_service.py

    def remove_items(self, user_id: str, items: List[Dict[str, Any]]) -> Order:
        """Entfernt Produkte aus der aktuellen Wochenbestellung"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Zeitraum bestimmen
        now = datetime.now()
        current_weekday = now.weekday()

        # Letzten Mittwoch 10:00 finden
        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

        # Wenn Mittwoch vor 10 Uhr, dann Vorwoche
        if current_weekday == 2 and now.hour < 10:
            period_start = period_start - timedelta(days=7)

        # Nächsten Mittwoch 09:59
        period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

        # Bestellungen im Zeitraum finden
        orders = self.session.query(Order).filter(
            Order.user_id == user.user_id,
            Order.order_date.between(period_start, period_end)
        ).all()

        if not orders:
            raise OrderError("Keine aktive Bestellung gefunden")

        # Für jedes zu entfernende Produkt
        for item in items:
            product = self.session.query(Product).filter(
                Product.name.ilike(item['name']),
                Product.active == True
            ).first()

            if not product:
                raise OrderError(f"Produkt {item['name']} nicht gefunden")

            # Alle OrderItems für dieses Produkt in den Bestellungen finden
            order_items = self.session.query(OrderItem).filter(
                OrderItem.order_id.in_([o.order_id for o in orders]),
                OrderItem.product_id == product.product_id
            ).all()

            if not order_items:
                raise OrderError(f"Produkt {item['name']} ist nicht in der Bestellung vorhanden")

            total_quantity = sum(oi.quantity for oi in order_items)
            if total_quantity < item['quantity']:
                raise OrderError(f"Nicht genügend {item['name']} zum Entfernen vorhanden")

            # Produkte entfernen/anpassen
            remaining = item['quantity']
            for order_item in order_items:
                if remaining <= 0:
                    break

                if order_item.quantity <= remaining:
                    remaining -= order_item.quantity
                    self.session.delete(order_item)
                else:
                    order_item.quantity -= remaining
                    remaining = 0

        return orders[0]  # Erste Bestellung für Bestätigung zurückgeben

    def _get_current_week_order(self, user_id: int) -> Optional[Order]:
        """Findet die aktuelle Wochenbestellung"""
        now = datetime.now()
        current_weekday = now.weekday()

        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

        if current_weekday == 2 and now.hour < 10:
            period_start = period_start - timedelta(days=7)

        period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

        return self.session.query(Order) \
            .filter(
            Order.user_id == user_id,
            Order.order_date.between(period_start, period_end)
        ) \
            .order_by(Order.order_date.desc()) \
            .first()