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

    def remove_items_preview(self, user_id: str, items: List[Dict[str, Any]]) -> Tuple[Order, List[Dict[str, Any]], Dict[str, int]]:
        """Erstellt eine Vorschau der Bestellung nach dem Entfernen von Produkten"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Zeitraum bestimmen
        now = datetime.now()
        current_weekday = now.weekday()
        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

        if current_weekday == 2 and now.hour < 10:
            period_start = period_start - timedelta(days=7)

        period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

        # Alle Bestellungen im Zeitraum finden
        orders = self.session.query(Order).filter(
            Order.user_id == user.user_id,
            Order.order_date.between(period_start, period_end)
        ).all()

        if not orders:
            raise OrderError("Keine aktive Bestellung gefunden")

        # Alle Produkte über den gesamten Zeitraum summieren
        current_items = {}
        for order in orders:
            for item in order.items:
                name = item.product.name
                if name in current_items:
                    current_items[name] += item.quantity
                else:
                    current_items[name] = item.quantity

        # Vorschau der verbleibenden Produkte berechnen
        preview_items = current_items.copy()

        # Überprüfen ob genügend Produkte zum Entfernen vorhanden sind und Vorschau berechnen
        invalid_items = []
        for item in items:
            name = item['name']
            if name not in preview_items:
                invalid_items.append((name, 0, item['quantity']))
            elif preview_items[name] < item['quantity']:
                invalid_items.append((name, preview_items[name], item['quantity']))
            else:
                preview_items[name] -= item['quantity']
                if preview_items[name] <= 0:
                    del preview_items[name]

        if invalid_items:
            error_msg = "\n".join([
                f"Nicht genügend {name} zum Entfernen vorhanden (Vorhanden: {current}, Angefordert: {requested})"
                for name, current, requested in invalid_items
            ])
            raise OrderError(error_msg)

        return orders[0], items, preview_items

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

    def get_current_order(self, user_slack_id: str, period_start: datetime, period_end: datetime) -> Order:
        """Holt die aktuelle Bestellung eines Benutzers für den angegebenen Zeitraum"""
        user = self.session.query(User).filter_by(slack_id=user_slack_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        order = (
            self.session.query(Order)
            .filter(
                Order.user_id == user.user_id,
                Order.order_date.between(period_start, period_end)
            )
            .order_by(Order.order_date.desc())
            .first()
        )

        if not order:
            raise OrderError("Keine aktive Bestellung gefunden")

        # Stelle sicher, dass die Items geladen werden
        self.session.refresh(order)
        return order

    def get_weekly_summary(self) -> List[Dict]:
        """Holt alle Bestellungen der aktuellen Woche und fasst sie zusammen"""
        now = datetime.now()
        current_weekday = now.weekday()
        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

        if current_weekday == 2 and now.hour < 10:  # Wenn Mittwoch vor 10 Uhr
            period_start = period_start - timedelta(days=7)

        period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

        # Nur eindeutige Bestellungen im Zeitraum holen
        orders = (
            self.session.query(Order)
            .filter(Order.order_date.between(period_start, period_end))
            .distinct()
            .all()
        )

        # Bestellungen nach Produkten zusammenfassen
        product_totals = {}
        for order in orders:
            for item in order.items:
                name = item.product.name
                if name in product_totals:
                    product_totals[name] += item.quantity
                else:
                    product_totals[name] = item.quantity

        return [{
            'name': name,
            'quantity': quantity
        } for name, quantity in sorted(product_totals.items())]

    def send_weekly_summary(self) -> None:
        """Sendet die Wochenbestellung an alle Benutzer mit gets_orders=True"""
        # Benutzer mit gets_orders=True finden
        users = self.session.query(User).filter_by(gets_orders=True).all()
        if not users:
            return

        # Wochenbestellung zusammenfassen
        summary = self.get_weekly_summary()

        return users, summary
