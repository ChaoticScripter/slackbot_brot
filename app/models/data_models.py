#==========================
# app/models/data_models.py
#==========================

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Basisklasse für alle Datenbankmodelle
Base = declarative_base()

class User(Base):
    """
    Datenbankmodell für Benutzer.
    Jeder User ist eindeutig über die Slack-ID identifizierbar.
    Attribute:
        - user_id: Primärschlüssel, interne ID
        - slack_id: Eindeutige Slack-Benutzer-ID
        - name: Anzeigename des Users
        - is_away: Abwesenheitsstatus (z.B. Urlaub/Homeoffice)
        - is_admin: Adminrechte
        - gets_orders: Erhält Wochenbestellungen
    Beziehungen:
        - orders: Alle Bestellungen des Users
        - reminders: Alle Erinnerungen des Users
        - saved_orders: Alle gespeicherten Bestellvorlagen
    """
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    slack_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    is_away = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    gets_orders = Column(Boolean, default=False, nullable=False)
    orders = relationship("Order", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    saved_orders = relationship("SavedOrder", back_populates="user")

class Product(Base):
    """
    Datenbankmodell für Produkte.
    Attribute:
        - product_id: Primärschlüssel
        - name: Produktname (z.B. Brötchen)
        - description: Optionale Beschreibung
        - active: Ist das Produkt bestellbar?
    Beziehungen:
        - order_items: Alle Bestellpositionen mit diesem Produkt
    """
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    """
    Datenbankmodell für Bestellungen.
    Jede Bestellung gehört zu genau einem User.
    Attribute:
        - order_id: Primärschlüssel
        - user_id: Fremdschlüssel zu User
        - order_date: Zeitpunkt der Bestellung
        - notes: Optionale Notiz
    Beziehungen:
        - user: Der zugehörige User
        - items: Alle Bestellpositionen (OrderItems)
    """
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String(255), nullable=True)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """
    Datenbankmodell für einzelne Bestellpositionen (Produkt + Menge).
    Jede OrderItem gehört zu einer Bestellung und einem Produkt.
    Attribute:
        - orderItem_id: Primärschlüssel
        - order_id: Fremdschlüssel zu Order
        - product_id: Fremdschlüssel zu Product
        - quantity: Bestellte Menge
    Beziehungen:
        - order: Zugehörige Bestellung
        - product: Zugehöriges Produkt
    """
    __tablename__ = "orderItem"
    orderItem_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="RESTRICT"))
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Reminder(Base):
    """
    Datenbankmodell für Erinnerungen (z.B. tägliche/wöchentliche Reminder).
    Attribute:
        - reminder_id: Primärschlüssel
        - user_id: Fremdschlüssel zu User
        - reminder_name: Name der Erinnerung
        - reminder_type: Typ (z.B. daily, weekly)
        - weekdays: Wochentage als String (optional)
        - reminder_time: Uhrzeit der Erinnerung
        - created_at: Erstellungszeitpunkt
        - updated_at: Letzte Änderung
        - is_active: Ist die Erinnerung aktiv?
    Beziehungen:
        - user: Der zugehörige User
    """
    __tablename__ = "reminders"
    reminder_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    reminder_name = Column(String(100), nullable=False)
    reminder_type = Column(String(50), nullable=False)
    weekdays = Column(String(50), nullable=True)
    reminder_time = Column(Time, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="reminders")

class SavedOrder(Base):
    """
    Datenbankmodell für gespeicherte Bestellvorlagen.
    Ermöglicht das Speichern und Wiederverwenden von Bestellungen.
    Attribute:
        - savedOrder_id: Primärschlüssel
        - user_id: Fremdschlüssel zu User
        - name: Name der Vorlage
        - order_string: String-Repräsentation der Bestellung
        - created_at: Erstellungszeitpunkt
        - updated_at: Letzte Änderung
    Beziehungen:
        - user: Der zugehörige User
    """
    __tablename__ = "savedOrders"
    savedOrder_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    order_string = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="saved_orders")