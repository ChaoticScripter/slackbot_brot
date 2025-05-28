# ==========================
# app/bot.py
# ==========================

from slack_bolt import App
from db.db import Session
from db.models import Order, User, Product, OrderItem
from datetime import datetime, timedelta
from sqlalchemy import func
from slack_sdk import WebClient
import os

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    process_before_response=True,  # Komma hinzugefügt
)  # Klammer auf neue Zeile


def get_slack_user_info(user_id, token):
    client = WebClient(token=token)
    try:
        result = client.users_info(user=user_id)
        return result["user"]["profile"]["display_name"] or result["user"]["real_name"]
    except Exception:
        return user_id


def get_current_order_period():
    now = datetime.now()
    # Bestimme den aktuellen Mittwoch 10:00
    current_wednesday = now
    while current_wednesday.weekday() != 2:  # 2 = Mittwoch
        current_wednesday -= timedelta(days=1)
    current_wednesday = current_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

    # Wenn es aktuell vor Mittwoch 10:00 ist, nehme die letzte Woche
    if now < current_wednesday:
        current_wednesday -= timedelta(days=7)

    # Ende der Bestellperiode ist der nächste Mittwoch 09:59
    next_wednesday = current_wednesday + timedelta(days=7)
    next_wednesday = next_wednesday.replace(hour=9, minute=59, second=59)

    return current_wednesday, next_wednesday


@app.command("/help")
def handle_help(ack, respond):
    ack()
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Brötchenbot Hilfe 🛟",
                "emoji": True
            }
        }
    ]
    attachments = [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Befehle:*\n" +
                                "`/order add <Produkt> <Menge>, <Produkt> <Menge>, ...` - Produkt zur Bestellung hinzufügen\n" +
                                "`/name` - Deinen aktuellen Namen anzeigen\n" +
                                "`/name change <Neuer Name>` - Deinen Namen ändern\n"

                        # "`/order remove <Produkt> <Menge>` - Produkt aus aktueller Bestellung entfernen\n" +
                        # "`/order list` - Aktuelle Bestellung anzeigen\n" +
                        # "`/order clear` - Bestellung zurücksetzen\n"
                    }
                }
            ]
        }
    ]
    respond(blocks=blocks, attachments=attachments)

@app.command("/name")
def handle_name(ack, respond, command):
    ack()
    user_id = command["user_id"]
    text = command.get("text", "").strip()
    session = Session()

    if text.startswith("change"):
        new_name = text[len("change"):].strip()
        if not new_name:
            respond("Bitte gib einen neuen Namen an.")
            session.close()
            return

        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            respond("Du bist nicht registriert. Bitte melde dich zuerst an.")
            session.close()
            return

        user.name = new_name
        session.commit()
        session.close()
        respond(f"Dein Name wurde auf `{new_name}` aktualisiert!")
        return

    user = session.query(User).filter_by(slack_id=user_id).first()
    if not user:
        respond("Du bist nicht registriert. Bitte melde dich zuerst an.")
        session.close()
        return

    respond(f"Dein aktueller Name ist `{user.name}`.")
    session.close()


@app.command("/order")
def handle_order(ack, respond, command):
    ack()
    text = command.get("text").strip()
    user_id = command["user_id"]
    session = Session()

    if text.startswith("add"):
        period_start, period_end = get_current_order_period()
        additions = text[4:].split(",")
        summary = []

        # Verbesserte Benutzeranlage mit Slack-Namen
        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            slack_name = get_slack_user_info(user_id, os.getenv("SLACK_BOT_TOKEN"))
            user = User(slack_id=user_id, name=slack_name)
            session.add(user)
            session.commit()

        # Existierende Wochenbestellung finden oder neue anlegen
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

        # Produkte zur Bestellung hinzufügen
        for item in additions:
            try:
                kind, amount = item.strip().split()
                product = session.query(Product).filter_by(name=kind, active=True).first()
                if not product:
                    respond(f"Fehler: Produkt `{kind}` nicht gefunden")
                    session.rollback()
                    return

                # Update oder Insert von OrderItem
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
            except Exception as e:
                respond(f"Fehler beim Parsen: `{item.strip()}` — {e}")
                session.rollback()
                return

        session.commit()

        # Aggregierte Abfrage für die aktuelle Wochenbestellung
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

        # Formatiere die Bestellung
        order_summary = "\n".join([f"• {total}x {name}" for name, total in order_items])

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🥨 Hey {user.name}, deine Bestellung wurde aktualisiert!",
                    "emoji": True
                }
            }
        ]

        attachments = [
            {
                "color": "#f2c744",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Hinzugefügt:*\n" + "\n".join(summary)
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Deine aktuelle Bestellung:*\n" +
                                    "\n".join([f"• {total}x {name}" for name, total in order_items])
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Bestellzeitraum: {period_start.strftime('%d.%m.%Y %H:%M')} - {period_end.strftime('%d.%m.%Y %H:%M')}"
                            }
                        ]
                    }
                ]
            }
        ]

        respond(blocks=blocks, attachments=attachments)

    if text.startswith("remove"):
        period_start, period_end = get_current_order_period()
        removals = text[7:].strip().split(",")
        summary = []
        not_found = []

        # Benutzer prüfen
        user = session.query(User).filter_by(slack_id=user_id).first()
        if not user:
            respond("Du bist nicht registriert. Bitte melde dich zuerst an.")
            session.close()
            return

        # Aktuelle Wochenbestellung finden
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
            respond("Du hast aktuell keine Bestellung für diese Woche.")
            session.close()
            return

        # Prüfe, was entfernt werden soll
        items_to_remove = []
        for item in removals:
            if not item.strip():
                continue

            try:
                kind, amount = item.strip().split()
                amount = int(amount)

                # Produkt in DB suchen
                product = session.query(Product).filter_by(name=kind, active=True).first()
                if not product:
                    not_found.append(f"Produkt `{kind}` nicht gefunden")
                    continue

                # OrderItem prüfen
                order_item = (
                    session.query(OrderItem)
                    .filter_by(order_id=current_order.order_id, product_id=product.product_id)
                    .first()
                )

                if not order_item:
                    not_found.append(f"`{kind}` ist nicht in deiner Bestellung")
                    continue

                if order_item.quantity < amount:
                    not_found.append(f"Du hast nur {order_item.quantity}x `{kind}` bestellt (nicht {amount}x)")
                    continue

                items_to_remove.append((order_item, amount, kind))
                summary.append(f"• {amount}x {kind}")

            except ValueError:
                not_found.append(f"Ungültiges Format: `{item.strip()}`")
                continue

        # Aktuelle Bestellung abfragen
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

        # Nachricht formatieren
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🥨 Bestellung aktualisieren",
                    "emoji": True
                }
            }
        ]

        attachments = [
            {
                "color": "#e01e5a" if not_found else "#f2c744",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Zu entfernende Produkte:*\n" + (
                                "\n".join(summary) if summary else "Keine gültigen Produkte ausgewählt.")
                        }
                    }
                ]
            }
        ]

        # Fehlermeldungen anzeigen wenn vorhanden
        if not_found:
            attachments[0]["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Fehler:*\n" + "\n".join(not_found)
                }
            })

        # Aktuelle Bestellung anzeigen
        attachments[0]["blocks"].extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Deine aktuelle Bestellung:*\n" + "\n".join(
                        [f"• {total}x {name}" for name, total in order_items])
                }
            }
        ])

        # Buttons nur anzeigen wenn gültige Produkte zum Entfernen existieren
        if items_to_remove:
            attachments[0]["blocks"].extend([
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Entfernen bestätigen"},
                            "style": "primary",
                            "action_id": "confirm_remove",
                            "value": f"{current_order.order_id}|" + "|".join(
                                [f"{oi.orderItem_id}:{qty}" for oi, qty, _ in items_to_remove])
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Abbrechen"},
                            "style": "danger",
                            "action_id": "cancel_remove"
                        }
                    ]
                }
            ])

        respond(blocks=blocks, attachments=attachments)
        return

    if text.startswith("list"):
        respond("Der Befehl `/order list` ist noch nicht implementiert.")

    if text.startswith("clear"):
        respond("Der Befehl `/order clear` ist noch nicht implementiert.")


@app.action("confirm_remove")
def handle_confirm_remove(ack, body, respond):
    ack()
    session = Session()

    try:
        # Parse die Button-Value
        order_id, *items = body["actions"][0]["value"].split("|")
        order_id = int(order_id)

        # Hole die Order
        order = session.query(Order).get(order_id)
        if not order:
            respond("Fehler: Bestellung nicht gefunden.")
            session.close()
            return

        summary = []
        # Verarbeite jedes zu entfernende Item
        for item_data in items:
            orderitem_id, qty = map(int, item_data.split(":"))
            order_item = session.query(OrderItem).get(orderitem_id)

            if not order_item:
                continue

            product_name = order_item.product.name
            if order_item.quantity <= qty:
                session.delete(order_item)
                summary.append(f"• {order_item.quantity}x {product_name} (komplett entfernt)")
            else:
                order_item.quantity -= qty
                summary.append(f"• {qty}x {product_name}")

        session.commit()

        # Aktualisierte Bestellung abfragen
        period_start, period_end = get_current_order_period()
        current_items = (
            session.query(Product.name, func.sum(OrderItem.quantity).label('total'))
            .join(OrderItem)
            .join(Order)
            .filter(
                Order.order_id == order_id,
                Order.order_date >= period_start,
                Order.order_date < period_end
            )
            .group_by(Product.name)
            .all()
        )

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🥨 Bestellung aktualisiert",
                    "emoji": True
                }
            }
        ]

        attachments = [
            {
                "color": "#36a64f",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Entfernte Produkte:*\n" + "\n".join(summary)
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Deine aktuelle Bestellung:*\n" +
                                    ("\n".join([f"• {total}x {name}" for name, total in current_items])
                                     if current_items else "Keine Produkte bestellt")
                        }
                    }
                ]
            }
        ]

        respond(blocks=blocks, attachments=attachments)

    except Exception as e:
        respond("Es ist ein Fehler aufgetreten: " + str(e))
        session.rollback()
    finally:
        session.close()


@app.action("cancel_remove")
def handle_cancel_remove(ack, respond):
    ack()
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "❌ Entfernen abgebrochen"
            }
        }
    ]
    respond(blocks=blocks)
    session.close()