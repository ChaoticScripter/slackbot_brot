#==========================
# app/handlers/order.py
#==========================

from db.db import Session
from db.models import Order, User, Product, OrderItem
from app.utils.slack import get_current_order_period
from app.utils.formatting import create_order_blocks
from app.utils.user_validation import check_user_registration
from app.utils.constants import ERROR_MESSAGES, COMMANDS, DB_CONSTRAINTS
from sqlalchemy import func
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


def handle_order_add(ack: callable, respond: callable, command: Dict[str, Any]) -> None:
    """Behandelt das Hinzufügen von Produkten zur Bestellung"""
    ack()
    user_id: str = command["user_id"]
    session = Session()

    try:
        # Überprüfe Registrierung
        user = check_user_registration(user_id, respond)
        if not user:
            respond(ERROR_MESSAGES["REGISTRATION_REQUIRED"])
            return

        text = command.get("text", "").strip()
        if not text.startswith(COMMANDS["ORDER_ADD"]):
            respond(ERROR_MESSAGES["ORDER_INVALID_FORMAT"])
            return

        period_start, period_end = get_current_order_period()
        current_order = get_or_create_order(user, period_start, period_end, session)

        # Verarbeite Bestellung
        try:
            additions = text[4:].split(",")
            summary = process_order_items(additions, current_order, session)
            if not summary:
                return

            session.commit()

            # Hole aktuelle Bestellübersicht
            order_items = get_current_order_items(user, period_start, period_end, session)
            blocks, attachments = create_order_blocks(user.name, summary, order_items, period_start, period_end)
            respond(blocks=blocks, attachments=attachments)

        except ValueError:
            respond(ERROR_MESSAGES["ORDER_INVALID_FORMAT"])
        except Exception as e:
            respond(ERROR_MESSAGES["ORDER_GENERAL_ERROR"])
            raise

    finally:
        session.close()


def get_or_create_order(user: User, period_start: datetime, period_end: datetime,
                        session: Session) -> Order:
    """Holt existierende oder erstellt neue Bestellung"""
    current_order = (
        session.query(Order)
        .filter(
            Order.user_id == user.user_id,
            Order.order_date >= period_start,
            Order.order_date < period_end
        )
        .first()
    )

    if not current_order:
        current_order = Order(user_id=user.user_id, order_date=datetime.now())
        session.add(current_order)
        session.commit()

    return current_order


def process_order_items(additions: List[str], current_order: Order,
                        session: Session) -> Optional[List[str]]:
    """Verarbeitet die Bestellpositionen"""
    summary: List[str] = []

    for item in additions:
        try:
            kind, amount = item.strip().split()
            amount = int(amount)

            if not DB_CONSTRAINTS["MIN_QUANTITY"] <= amount <= DB_CONSTRAINTS["MAX_QUANTITY"]:
                raise ValueError(ERROR_MESSAGES["ORDER_INVALID_QUANTITY"].format(product=kind))

            product = session.query(Product).filter_by(name=kind, active=True).first()
            if not product:
                raise ValueError(ERROR_MESSAGES["ORDER_PRODUCT_NOT_FOUND"].format(product=kind))

            update_order_item(current_order, product, amount, session)
            summary.append(f"• {amount}x {kind}")

        except ValueError as e:
            session.rollback()
            raise ValueError(str(e))

    return summary


def update_order_item(order: Order, product: Product, quantity: int,
                      session: Session) -> None:
    """Aktualisiert oder erstellt Bestellposition"""
    existing_item = (
        session.query(OrderItem)
        .filter_by(order_id=order.order_id, product_id=product.product_id)
        .first()
    )

    if existing_item:
        existing_item.quantity += quantity
    else:
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity
        )
        session.add(order_item)


def get_current_order_items(user: User, period_start: datetime, period_end: datetime,
                            session: Session) -> List[Tuple[str, int]]:
    """Holt aktuelle Bestellpositionen"""
    return (
        session.query(Product.name, func.sum(OrderItem.quantity).label('total'))
        .join(OrderItem)
        .join(Order)
        .filter(
            Order.user_id == user.user_id,
            Order.order_date >= period_start,
            Order.order_date < period_end
        )
        .group_by(Product.name)
        .all()
    )