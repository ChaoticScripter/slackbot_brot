#==========================
# app/core/product_service.py
#==========================

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Product
from app.utils.constants.error_types import ValidationError


class ProductService:
    """
    Service-Klasse für alle Geschäftslogiken rund um Produkte.
    Kapselt alle Datenbankoperationen für Produkt-Objekte.
    Wird von den Handlern aufgerufen, um Produkte zu verwalten oder abzufragen.
    """

    def __init__(self, session: Session):
        self.session = session

    def add_product(self, name: str, description: Optional[str] = None) -> Product:
        """
        Fügt ein neues Produkt hinzu. Gibt einen Fehler aus, wenn das Produkt bereits existiert.
        :param name: Produktname
        :param description: Optionale Beschreibung
        :return: Das hinzugefügte Produkt-Objekt
        """
        if self.session.query(Product).filter_by(name=name).first():
            raise ValidationError(f"Produkt {name} existiert bereits")

        product = Product(name=name, description=description)
        self.session.add(product)
        return product

    def get_active_products(self) -> List[Product]:
        """
        Gibt alle aktiven Produkte zurück.
        :return: Liste der aktiven Produkt-Objekte
        """
        return self.session.query(Product).filter_by(active=True).all()