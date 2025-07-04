#==========================
# app/core/saved_order_service.py
#==========================

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SavedOrder, User
from app.utils.constants.error_types import OrderError


class SavedOrderService:
    def __init__(self, session: Session):
        self.session = session

    def save_order(self, user_id: str, name: str, order_string: str) -> SavedOrder:
        """Speichert eine Bestellvorlage"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            raise OrderError("Benutzer nicht gefunden")

        # Prüfen ob Name bereits existiert
        existing = self.session.query(SavedOrder).filter_by(
            user_id=user.user_id,
            name=name
        ).first()

        if existing:
            raise OrderError(f"Eine Bestellung mit dem Namen '{name}' existiert bereits")

        saved_order = SavedOrder(
            user_id=user.user_id,
            name=name,
            order_string=order_string
        )
        self.session.add(saved_order)
        return saved_order

    def get_saved_order(self, user_id: str, name: str) -> Optional[SavedOrder]:
        """Lädt eine gespeicherte Bestellvorlage"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return None

        return self.session.query(SavedOrder).filter_by(
            user_id=user.user_id,
            name=name
        ).first()

    def list_saved_orders(self, user_id: str) -> List[SavedOrder]:
        """Listet alle gespeicherten Bestellvorlagen eines Users"""
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return []

        return self.session.query(SavedOrder).filter_by(
            user_id=user.user_id
        ).all()