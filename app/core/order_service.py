#==========================
# app/core/order_service.py
#==========================

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Product, User
from app.utils.constants.error_types import OrderError


class OrderService:
    """
    Service-Klasse für alle Geschäftslogiken rund um Bestellungen.
    Kapselt alle Datenbankoperationen für Orders, OrderItems und deren Auswertung.
    Wird von den Handlern aufgerufen, um Bestellungen zu erstellen, zu ändern oder auszuwerten.
    """
    def __init__(self, session: Session):
        # SQLAlchemy-Session für alle DB-Operationen
        self.session = session

    def add_order(self, user_id: str, items: List[Dict[str, Any]]) -> Order:
        """
        Legt eine neue Bestellung für einen User an und fügt die bestellten Produkte hinzu.
        - user_id: Slack-ID des Users
        - items: Liste von Dicts mit Produktnamen und Mengen
        Ablauf:
        1. User anhand Slack-ID suchen
        2. Neue Order anlegen
        3. Für jedes Produkt ein OrderItem anlegen
        4. Order und Items in DB speichern
        5. Gibt das Order-Objekt zurück
        """
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
        """
        Gibt alle Bestellungen eines Users zurück.
        - user_id: Slack-ID
        - Rückgabe: Liste von Order-Objekten
        """
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return []
        return self.session.query(Order).filter_by(user_id=user.user_id).all()

    def remove_items_preview(self, user_id: str, items: List[Dict[str, Any]]) -> Tuple[Order, List[Dict[str, Any]], Dict[str, int]]:
        """
        Erstellt eine Vorschau der Bestellung nach dem Entfernen von Produkten.
        - user_id: Slack-ID
        - items: Liste der zu entfernenden Produkte
        - Rückgabe: (Order, entfernte Items, verbleibende Produkte)
        Ablauf:
        1. User und aktuelle Woche bestimmen
        2. Alle Bestellungen des Users in dieser Woche holen
        3. Produkte aufsummieren
        4. Entfernte Produkte simulieren (ohne DB-Änderung)
        5. Fehler, falls zu viel entfernt werden soll
        """
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Zeitraum bestimmen (aktuelle Bestellwoche)
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

    def remove_items(self, user_id: str, items: List[Dict[str, Any]]) -> Order:
        """
        Entfernt Produkte aus der aktuellen Wochenbestellung (persistiert in der DB).
        - user_id: Slack-ID
        - items: Liste der zu entfernenden Produkte
        Ablauf:
        1. User und aktuelle Woche bestimmen
        2. Alle Bestellungen des Users in dieser Woche holen
        3. Für jedes Produkt die OrderItems suchen und Mengen anpassen/löschen
        4. Änderungen werden in der DB gespeichert
        5. Gibt die erste Order zurück (zur Bestätigung)
        """
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")
        # Zeitraum bestimmen (aktuelle Bestellwoche)
        now = datetime.now()
        current_weekday = now.weekday()
        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)
        if current_weekday == 2 and now.hour < 10:
            period_start = period_start - timedelta(days=7)
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
        """
        Findet die aktuelle Wochenbestellung eines Users (hilfreich für interne Zwecke).
        - user_id: interne User-ID
        - Rückgabe: Order-Objekt oder None
        """
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
        """
        Holt die aktuelle Bestellung eines Benutzers für den angegebenen Zeitraum.
        - user_slack_id: Slack-ID
        - period_start, period_end: Zeitraum der Woche
        - Rückgabe: Order-Objekt
        Ablauf:
        1. User anhand Slack-ID suchen
        2. Order im Zeitraum suchen (neueste zuerst)
        3. Fehler, falls keine Order gefunden
        4. Order-Objekt zurückgeben
        """
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
        """
        Holt alle Bestellungen der aktuellen Woche und fasst sie nach Produkt zusammen.
        - Rückgabe: Liste von Dicts mit Produktname und Gesamtmenge
        Ablauf:
        1. Zeitraum der aktuellen Woche bestimmen (Mi 10:00 bis Mi 09:59)
        2. Alle Orders im Zeitraum holen
        3. Produkte und Mengen aufsummieren
        4. Rückgabe als Liste von Dicts
        """
        now = datetime.now()
        current_weekday = now.weekday()
        days_since_wednesday = (current_weekday - 2) % 7
        last_wednesday = now - timedelta(days=days_since_wednesday)
        period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)
        if current_weekday == 2 and now.hour < 10:  # Wenn Mittwoch vor 10 Uhr
            period_start = period_start - timedelta(days=7)
        period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

        # Hole alle Bestellungen mit User-Informationen

        orders = (
            self.session.query(Order)
            .filter(Order.order_date.between(period_start, period_end))
            .distinct()
            .all()
        )

        # Bestellungen nach Produkten und Usern zusammenfassen

        product_totals = {}
        user_orders = {}  # Dict für User-spezifische Bestellungen

        for order in orders:
            user_name = order.user.name or "Unbekannt"

            for item in order.items:
                name = item.product.name
                # Produkt-Totale
                if name in product_totals:
                    product_totals[name] += item.quantity
                else:
                    product_totals[name] = item.quantity

                # User-spezifische Bestellungen
                if name not in user_orders:
                    user_orders[name] = []
                if user_name not in [u['name'] for u in user_orders[name]]:
                    user_orders[name].append({
                        'name': user_name,
                        'quantity': item.quantity
                    })
                else:
                    # Addiere zur bestehenden Menge des Users
                    for user_order in user_orders[name]:
                        if user_order['name'] == user_name:
                            user_order['quantity'] += item.quantity
                            
        return [{
            'name': name,
            'quantity': quantity,
            'users': sorted(user_orders[name], key=lambda x: x['name'])  # Sortiere User alphabetisch
        } for name, quantity in sorted(product_totals.items())]

    def send_weekly_summary(self) -> None:
        """
        Sammelt alle User mit gets_orders=True und gibt sie zusammen mit der Wochenzusammenfassung zurück.
        Wird vom Handler genutzt, um die Wochenbestellung zu verschicken.
        - Rückgabe: (Liste der User, Wochenzusammenfassung)
        """
        users = self.session.query(User).filter_by(gets_orders=True).all()
        if not users:
            return
        summary = self.get_weekly_summary()
        return users, summary
