#==========================
# db/models.py
#==========================
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    slack_id = Column(String, unique=True, nullable=False)  # Slack User ID
    name = Column(String, nullable=False)
    is_on_vacation = Column(Boolean, default=False)
    is_home_office = Column(Boolean, default=False)
    home_office_until = Column(DateTime, nullable=True)

    orders = relationship("Order", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item = Column(String, nullable=False)   # e.g. "normal", "kürbis"
    quantity = Column(Integer, nullable=False)
    confirmed = Column(Boolean, default=False)

    user = relationship("User", back_populates="orders")


class SavedOrder(Base):
    __tablename__ = "saved_orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)  # z. B. "großhunger"
    items = Column(String, nullable=False)  # CSV: "normal 2, kürbis 1"

    __table_args__ = (UniqueConstraint("user_id", "name"),)


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # "day" oder "wd"
    weekdays = Column(String, nullable=True)  # "mo,di,mi"
    times = Column(String)  # "08:00,12:00"

    user = relationship("User", back_populates="reminders")