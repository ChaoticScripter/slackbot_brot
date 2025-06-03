[//]: # (==========================)
[//]: # (README.md)
[//]: # (==========================)

# BrotBot 🥐

Ein Slack-Bot zur Verwaltung von Brötchenbestellungen für Teams. Ermöglicht die einfache Verwaltung von 
Brötchenbestellungen via Slack-Commands.

## Features

* Bestellungen via `/order` Command
* Erinnerungen für regelmäßige Bestellungen
* Urlaubs- und Home-Office-Verwaltung
* Speichern von Standardbestellungen

## Entwicklung
* Python 3.8+
* Flask als Web-Framework
* SQLAlchemy als ORM
* Slack Bolt für Slack-Integration

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
# Flask-Server starten
flask run
```
## Verwendung
Bot zu Slack hinzufügen:
1. Gehe zu deiner Slack App und wähle "OAuth & Permissions" aus.
2. Füge die benötigten Scopes hinzu:
   - `commands`
   - `chat:write`
   - `users:read`

3. Installiere die App in deinem Workspace.
4. Füge den Bot zu deinem gewünschten Channel hinzu.
5. Teste den Bot mit dem `/order` Command.

Bot starten:
```bash
python main.py      # Im Projektverzeichnis
```

## Befehle
### `/order`
Bestellt Brötchen für den aktuellen Tag. Beispiel:
```
/order add normal 2, vollkorn 1    # Neue Bestellung
/order list                        # Zeige Bestellung
```

## Datenbank-Schema

### Tabelle: `users`
|  Spalte  |      Typ      |   Constraints    |      Beschreibung      |
|:--------:|:-------------:|:----------------:|:----------------------:|
| user_id  |    INTEGER    |   Primary Key    | Eindeutige Benutzer-ID |
| slack_id |  VARCHAR(50)  | NOT NULL, UNIQUE | Slack-Benutzerkennung  |
|   name   | NVARCHAR(100) |       NULL       |   Name des Benutzers   |
| is_away  |    BOOLEAN    |  DEFAULT FALSE   | Status der Abwesenheit |

### Tabelle: `orders`
|   Spalte   |      Typ      | Constraints |         Beschreibung          |
|:----------:|:-------------:|:-----------:|:-----------------------------:|
|  order_id  |    INTEGER    | Primary Key |     Eindeutige Bestell-ID     |
|  user_id   |    INTEGER    | Foreign Key | Referenz zum Benutzer `users` |
| order_date |   TIMESTAMP   |  NOT NULL   |     Datum der Bestellung      |
|   notes    | NVARCHAR(255) |    NULL     |      Zusätzliche Notizen      |

### Tabelle: `products`
|   Spalte    |      Typ      | Constraints  |     Beschreibung      |
|:-----------:|:-------------:|:------------:|:---------------------:|
| product_id  |    INTEGER    | Primary Key  | Eindeutige Produkt-ID |
|    name     | NVARCHAR(100) |   NOT NULL   |  Name des Produktes   |
| description | NVARCHAR(255) |     NULL     |  Produktbeschreibung  |
|   active    |    BOOLEAN    | DEFAULT TRUE |   Ist Produkt aktiv   |

### Tabelle: `reminders`
|    Spalte     |      Typ      | Constraints  |         Beschreibung          |
|:-------------:|:-------------:|:------------:|:-----------------------------:|
|  reminder_id  |    INTEGER    | Primary Key  |   Eindeutige Erinnerungs-ID   |
|    user_id    |    INTEGER    | Foreign Key  | Referenz zum Benutzer `users` |
| reminder_name | NVARCHAR(100) |   NOT NULL   |      Name der Erinnerung      |
| reminder_type |  VARCHAR(50)  |   NOT NULL   |      Typ der Erinnerung       |
|   weekdays    |  VARCHAR(50)  |     NULL     |   Wochentag der Erinnerung    |
| reminder_time |     TIME      |     NULL     |    Uhrzeit der Erinnerung     |
|  created_at   |   TIMESTAMP   |   NOT NULL   |     Erstellungszeitpunkt      |
|  updated_at   |   TIMESTAMP   |     NULL     |  Letzter Änderungszeitpunkt   |
|   is_active   |    BOOLEAN    | DEFAULT TRUE |     Status der Erinnerung     |

### Tabelle: `orderItem`
|    Spalte    |   Typ   | Constraints |           Beschreibung           |
|:------------:|:-------:|:-----------:|:--------------------------------:|
| orderItem_id | INTEGER | Primary Key |   Eindeutige Bestellprodukt-ID   |
|   order_id   | INTEGER | Foreign Key | Referenz zur Bestellung `orders` |
|  product_id  | INTEGER | Foreign Key | Referenz zum Produkt `products`  |
|   quantity   | INTEGER |  NOT NULL   |              Menge               |

### Tabelle: `savedOrders`
|    Spalte     |      Typ      | Constraints |              Beschreibung              |
|:-------------:|:-------------:|:-----------:|:--------------------------------------:|
| savedOrder_id |    INTEGER    | Primary Key |      Eindeutige Bestellprodukt-ID      |
|    user_id    |    INTEGER    | Foreign Key |     Referenz zum Benutzer `users`      |
|     name      | NVARCHAR(100) |  NOT NULL   |   Name der gespeicherten Bestellung    |
| order_string  |     TEXT      |  NOT NULL   | JSON oder String-Format der Bestellung |
|  created_at   |   TIMESTAMP   |  NOT NULL   |          Erstellungszeitpunkt          |
|  updated_at   |   TIMESTAMP   |    NULL     |       Letzter Änderungszeitpunkt       |

## MySQL-Statement zum Erstellen der Datenbank
```MySQL
-- Erstellen der Datenbank
CREATE DATABASE IF NOT EXISTS brotbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Datenbank auswählen
USE brotbot;

-- Tabelle: users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    slack_id VARCHAR(50) NOT NULL UNIQUE,
    name NVARCHAR(100) NULL,
    is_away BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

-- Tabelle: products
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255) NULL,
    active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- Tabelle: orders
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date TIMESTAMP NOT NULL,
    notes NVARCHAR(255) NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabelle: reminders
CREATE TABLE reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reminder_name NVARCHAR(100) NOT NULL,
    reminder_type VARCHAR(50) NOT NULL,
    weekdays VARCHAR(50) NULL,
    reminder_time TIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabelle: orderItem
CREATE TABLE orderItem (
    orderItem_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tabelle: savedOrders
CREATE TABLE savedOrders (
    savedOrder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    order_string TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Indices erstellen
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_orderitem_order ON orderItem(order_id);
CREATE INDEX idx_orderitem_prod ON orderItem(product_id);
CREATE INDEX idx_savedorders_user ON savedOrders(user_id);
```# test
# test
