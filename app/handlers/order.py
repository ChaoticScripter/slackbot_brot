#==========================
# app/handlers/order.py
#==========================

from db.db import Session
from db.models import Order, User, Product, OrderItem
from app.utils.slack import get_current_order_period, get_slack_user_info
from app.utils.formatting import create_order_blocks
from app.utils.user_validation import check_user_registration
from sqlalchemy import func
from datetime import datetime
import os


def handle_order_add(ack, respond, command):
    ack()
    user_id = command["user_id"]

    # Überprüfe Registrierung
    user = check_user_registration(user_id, respond)
    if not user:
        return

    text = command.get("text").strip()
    session = Session()

    try:
        period_start, period_end = get_current_order_period()
        additions = text[4:].split(",")
        summary = []

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

        for item in additions:
            kind, amount = item.strip().split()
            product = session.query(Product).filter_by(name=kind, active=True).first()
            if not product:
                respond(f"Fehler: Produkt `{kind}` nicht gefunden")
                return

            existing_item = (
                session.query(OrderItem)
                .filter_by(order_id=current_order.order_id, product_id=product.product_id)
                .first()
            )

            if existing_item:
                existing_item.quantity += int(amount)
            else:
                order_item = OrderItem(
                    order_id=current_order.order_id,
                    product_id=product.product_id,
                    quantity=int(amount)
                )
                session.add(order_item)
            summary.append(f"• {amount}x {kind}")

        session.commit()

        order_items = (
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

        blocks, attachments = create_order_blocks(user.name, summary, order_items, period_start, period_end)
        respond(blocks=blocks, attachments=attachments)

    finally:
        session.close()