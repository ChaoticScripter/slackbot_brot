#==========================
# app/core/order_service.py
#==========================

from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import Order, OrderItem, Product, User
from app.utils.constants.error_types import OrderError


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def add_order(self, user_id: str, items: List[Dict[str, Any]]) -> Order:
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        current_time = datetime.now()
        if not self._is_within_order_period(current_time):
            raise OrderError("Bestellungen sind nur von Mittwoch 10:00 bis nächsten Mittwoch 09:59 möglich")

        order = Order(user_id=user.user_id, order_date=current_time)
        self.session.add(order)
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

        self.session.flush()
        return order

    def get_user_orders(self, user_id: str) -> List[Order]:
        """Holt alle Bestellungen eines Users im aktuellen Bestellzeitraum"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return []

        current_period = self._get_current_order_period()
        return self.session.query(Order).filter(
            and_(
                Order.user_id == user.user_id,
                Order.order_date >= current_period['start'],
                Order.order_date <= current_period['end']
            )
        ).order_by(Order.order_date.asc()).all()

    def _get_current_order_period(self) -> Dict[str, datetime]:
        """Berechnet den aktuellen Bestellzeitraum"""
        now = datetime.now()

        # Letzten Mittwoch 10:00 Uhr finden
        last_wednesday = now
        while last_wednesday.weekday() != 2:  # 2 = Mittwoch
            last_wednesday -= timedelta(days=1)

        start_time = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

        # Wenn aktueller Tag Mittwoch und Zeit < 10:00 Uhr, dann nimm Mittwoch der Vorwoche
        if now.weekday() == 2 and now.hour < 10:
            start_time -= timedelta(days=7)

        # Ende ist immer 7 Tage später um 9:59:59 Uhr
        end_time = start_time + timedelta(days=7)
        end_time = end_time.replace(hour=9, minute=59, second=59)

        return {
            'start': start_time,
            'end': end_time
        }

    def _is_within_order_period(self, check_time: datetime) -> bool:
        """Prüft ob ein Zeitpunkt innerhalb des Bestellzeitraums liegt"""
        period = self._get_current_order_period()
        return period['start'] <= check_time <= period['end']