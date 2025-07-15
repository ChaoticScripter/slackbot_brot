#==========================
# app/core/saved_order_service.py
#==========================

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SavedOrder, User
from app.utils.constants.error_types import OrderError


class SavedOrderService:
    """
    Service-Klasse für das Speichern und Laden von Bestellvorlagen ("gespeicherte Bestellungen").
    Kapselt alle Datenbankoperationen für SavedOrder-Objekte.
    Wird von den Handlern aufgerufen, um Vorlagen zu speichern, zu laden oder aufzulisten.
    """
    def __init__(self, session: Session):
        # SQLAlchemy-Session für alle DB-Operationen
        self.session = session

    def save_order(self, user_id: str, name: str, order_string: str) -> SavedOrder:
        """
        Speichert eine neue Bestellvorlage für einen User.
        - user_id: Slack-ID des Users
        - name: Name der Vorlage (eindeutig pro User)
        - order_string: String-Repräsentation der Bestellung (z.B. 'brot 2, kuchen 1')
        Ablauf:
        1. User anhand Slack-ID suchen
        2. Prüfen, ob bereits eine Vorlage mit diesem Namen existiert
        3. Neue SavedOrder anlegen und speichern
        4. Gibt das SavedOrder-Objekt zurück
        """
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
        """
        Lädt eine gespeicherte Bestellvorlage eines Users anhand des Namens.
        - user_id: Slack-ID
        - name: Name der Vorlage
        - Rückgabe: SavedOrder-Objekt oder None
        Ablauf:
        1. User anhand Slack-ID suchen
        2. SavedOrder anhand user_id und name suchen
        3. Gibt das SavedOrder-Objekt zurück (oder None)
        """
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return None

        return self.session.query(SavedOrder).filter_by(
            user_id=user.user_id,
            name=name
        ).first()

    def list_saved_orders(self, user_id: str) -> List[SavedOrder]:
        """
        Gibt alle gespeicherten Bestellvorlagen eines Users zurück.
        - user_id: Slack-ID
        - Rückgabe: Liste von SavedOrder-Objekten
        """
        user = self.session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            return []
        return self.session.query(SavedOrder).filter_by(user_id=user.user_id).all()
