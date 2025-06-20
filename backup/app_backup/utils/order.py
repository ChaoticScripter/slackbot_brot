#==========================
# app/utils/order.py
#==========================

from db.db import Session
from db.models import Order, OrderItem, Product
from datetime import datetime
from sqlalchemy import func
from typing import List, Tuple, Optional

def get_user_order(user_id: int, period_start: datetime, period_end: datetime) -> Optional[Order]:
    """Aktuelle Bestellung eines Users im Bestellzeitraum abrufen"""
    session = Session()
    try:
        return (
            session.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.order_date >= period_start,
                Order.order_date < period_end
            )
            .first()
        )
    finally:
        session.close()

def get_order_summary(order_id: int) -> List[Tuple[str, int]]:
    """Zusammenfassung der Bestellpositionen"""
    session = Session()
    try:
        return (
            session.query(Product.name, func.sum(OrderItem.quantity).label('total'))
            .join(OrderItem)
            .filter(OrderItem.order_id == order_id)
            .group_by(Product.name)
            .all()
        )
    finally:
        session.close()

def validate_products(product_list: List[Tuple[str, int]]) -> List[str]:
    """Prüft ob alle Produkte existieren und aktiv sind"""
    session = Session()
    errors = []
    try:
        for product_name, _ in product_list:
            product = session.query(Product).filter_by(name=product_name, active=True).first()
            if not product:
                errors.append(f"Produkt `{product_name}` nicht gefunden oder inaktiv")
        return errors
    finally:
        session.close()

def parse_order_items(order_text: str) -> List[Tuple[str, int]]:
    """Parst Bestelltext in Liste von (Produkt, Menge)"""
    items = []
    for item in order_text.split(","):
        try:
            kind, amount = item.strip().split()
            items.append((kind, int(amount)))
        except ValueError:
            continue
    return items

def update_order_items(order_id: int, items: List[Tuple[str, int]]) -> None:
    """Aktualisiert die Bestellpositionen"""
    session = Session()
    try:
        for product_name, quantity in items:
            product = session.query(Product).filter_by(name=product_name, active=True).first()
            if not product:
                continue

            existing_item = (
                session.query(OrderItem)
                .filter_by(order_id=order_id, product_id=product.product_id)
                .first()
            )

            if existing_item:
                existing_item.quantity += quantity
            else:
                new_item = OrderItem(
                    order_id=order_id,
                    product_id=product.product_id,
                    quantity=quantity
                )
                session.add(new_item)
        session.commit()
    finally:
        session.close()