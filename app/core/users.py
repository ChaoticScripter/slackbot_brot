from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.utils.constants.exceptions import ValidationError


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def register_user(self, slack_id: str, name: str) -> User:
        if self.session.query(User).filter_by(slack_id=slack_id).first():
            raise ValidationError("Benutzer bereits registriert")

        user = User(slack_id=slack_id, name=name)
        self.session.add(user)
        return user

    def get_user(self, slack_id: str) -> Optional[User]:
        """Benutzer anhand der Slack ID abrufen"""
        return self.session.query(User).filter_by(slack_id=slack_id).first()

    def update_user_name(self, slack_id: str, new_name: str) -> User:
        """Aktualisiert den Namen eines Benutzers"""
        user = self.get_user(slack_id)
        if not user:
            raise ValidationError("Benutzer nicht gefunden")

        user.name = new_name
        return user