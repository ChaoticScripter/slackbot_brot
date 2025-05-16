[//]: # (==========================)
[//]: # (README.md)
[//]: # (==========================)

# BrotBot 🥐

Ein Slack-Bot zur Verwaltung von Brötchenbestellungen für Teams. Ermöglicht die einfache Verwaltung von 
Brötchenbestellungen via Slack-Commands.

## Features

- Bestellungen via `/order` Command
- Erinnerungen für regelmäßige Bestellungen
- Urlaubs- und Home-Office-Verwaltung
- Speichern von Standardbestellungen

## Installation

1. Repository klonen:
```bash
git clone git@github.com:ChaoticScripter/brotbot.git
cd brotbot
```

Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

Konfiguration einrichten:
```bash
cp .env.example .env
# .env mit eigenen Werten befüllen
```
Konfiguration
Die `.env` Datei benötigt folgende Werte:
- `SLACK_BOT_TOKEN`: Bot Token aus Slack
- `SLACK_SIGNING_SECRET`: Signing Secret aus Slack
- `DATABASE_URL`: MySQL Verbindungs-URL
# Datenbank einrichten
```bash
# MySQL-Datenbank erstellen
mysql -u root -p
CREATE DATABASE brotbot;
```
```bash
# Datenbankmigrationen durchführen
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

```bash
# Beispiel-Daten einfügen
flask shell
from app import db
from app.models import User, Order
db.create_all()
user = User(name="Max Mustermann", slack_id="U12345678")
order = Order(user_id=user.id, date="2023-10-01", type="normal", amount=2)
db.session.add(user)
db.session.add(order)
db.session.commit()
```
```bash
# Flask-Server starten
flask run
```
## Verwendung
Bot starten:
```bash
python main.py
```
Bot zu Slack hinzufügen:
1. Gehe zu deiner Slack App und wähle "OAuth & Permissions" aus.
2. Füge die benötigten Scopes hinzu:
   - `commands`
   - `chat:write`
   - `users:read`

3. Installiere die App in deinem Workspace.
4. Füge den Bot zu deinem gewünschten Channel hinzu.
5. Teste den Bot mit dem `/order` Command.

## Befehle
### `/order`
Bestellt Brötchen für den aktuellen Tag. Beispiel:
```
/order add normal 2, vollkorn 1    # Neue Bestellung
/order list                        # Zeige Bestellung
```
## Entwicklung
- Python 3.8+
- Flask als Web-Framework
- SQLAlchemy als ORM
- Slack Bolt für Slack-Integration
## Sicherheitshinweise
- Niemals .env ins Repository pushen
- Produktiv-Tokens regelmäßig rotieren
- Datenbank-Backup einrichten