#==========================
# app/core/user_service.py
#==========================

from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.utils.constants.error_types import ValidationError


class UserService:
    """
    Service-Klasse für alle Geschäftslogiken rund um Benutzer.
    Kapselt alle Datenbankoperationen für User-Objekte.
    Wird von den Handlern aufgerufen, um Benutzer zu registrieren, abzufragen oder zu aktualisieren.
    """

    def __init__(self, session: Session):
        self.session = session

    def register_user(self, slack_id: str, name: str) -> User:
        """
        Registriert einen neuen Benutzer anhand der Slack-ID und des Namens.
        Gibt einen Fehler aus, wenn der User bereits existiert.
        """
        if self.session.query(User).filter_by(slack_id=slack_id).first():
            raise ValidationError("Benutzer bereits registriert")

        user = User(slack_id=slack_id, name=name)
        self.session.add(user)
        return user

    def get_user(self, slack_id: str) -> Optional[User]:
        """
        Holt einen Benutzer anhand der Slack-ID.
        Gibt None zurück, wenn der User nicht existiert.
        """
        return self.session.query(User).filter_by(slack_id=slack_id).first()

    def update_user_name(self, slack_id: str, new_name: str) -> User:
        """
        Aktualisiert den Namen eines Benutzers anhand der Slack-ID.
        Gibt einen Fehler aus, wenn der User nicht existiert.
        """
        user = self.get_user(slack_id)
        if not user:
            raise ValidationError("Benutzer nicht gefunden")

        user.name = new_name
        return user

    def get_user_name(self, slack_id: str) -> Optional[str]:
        """
        Gibt den aktuellen Namen eines Benutzers zurück (oder None).
        """
        user = self.get_user(slack_id)
        return user.name if user else None
