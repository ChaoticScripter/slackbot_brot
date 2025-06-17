#==========================
# app/core/product_service.py
#==========================

from typing import List, Optional, Type
from sqlalchemy.orm import Session
from app.models import Product
from app.utils.constants.error_types import ValidationError
from models import Product


class ProductService:
    def __init__(self, session: Session):
        self.session = session

    def add_product(self, name: str, description: Optional[str] = None) -> Product:
        if self.session.query(Product).filter_by(name=name).first():
            raise ValidationError(f"Produkt {name} existiert bereits")

        product = Product(name=name, description=description)
        self.session.add(product)
        return product

    def get_active_products(self) -> list[Type[Product]]:
        return self.session.query(Product).filter_by(active=True).all()