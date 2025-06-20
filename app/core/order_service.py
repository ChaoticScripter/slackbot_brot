#==========================
# app/core/order_service.py
#==========================

from datetime import datetime
from typing import List, Dict, Any, Optional
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