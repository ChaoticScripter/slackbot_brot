# GIT Branches

|        Branches (feature)         | Priorität |  Abhängigkeit  |            Beschreibung            |          Status          |
|:---------------------------------:|:---------:|:--------------:|:----------------------------------:|:------------------------:|
|  feature_order_function_flat_1.0  | Sehr Hoch |     Keine      | Grundlegende Bestellfunktionalität |     Erste Priorität      |
|    feature_order_save_flat_1.0    |  Mittel   | order_function |        Bestellung speichern        |    Nach Hauptfunktion    |
|  feature_order_reminder_flat_1.0  |   Hoch    | order_function |   Erinnerungen für Bestellungen    | Parallel zu Liste/Senden |
| feature_orderListAndSend_flat_1.0 |   Hoch    | order_function |      Bestellliste und Versand      |   Parallel zu Reminder   |
|   feature_order_remove_flat_1.0   |  Mittel   | order_function |        Bestellung entfernen        |   Nach Basisfunktionen   |
| feature_order_nameChange_flat_1.0 |  Niedrig  | order_function |            Name ändern             |         Optional         |
|       feature_away_flat_1.0       |  Niedrig  |     Keine      |         Abwesenheitsstatus         |         Optional         |
|     feature_vacation_flat_1.0     |  Niedrig  |      away      |            Urlaubsmodus            |         Optional         |
|       feature_home_flat_1.0       |  Niedrig  |      away      |         Home-Office-Modus          |         Optional         |
## Grundlegende Bot-Funktionen
  - [ ] **feature_order_function_flat_1.0** Grundlegende Bestellfunktionalität
      - [ ] Help Befehl implementieren
      - [ ] Einpflegen von Produkten in die Datenbank
        - [ ] Anzeigen der Produktauswahl `/order selection`
        - [ ] Anzeigen der aktuellen Bestellung, wenn vorhanden (ansonsten Anleitung + Auswahl der Produkte)
      - [ ] Bestellen von Produkten `/order add`
        - [ ] Bestellung bestätigen oder abbrechen nach ausgabe `/order add accept` , `/order add cancel`
        - [ ] Fehler bei falschen Produktnamen
      - [ ] Bestellhistorie
        - [ ] Bestellungen aus der Vergangenheit auflisten
      - [ ] Bestellung an einen User um eine bestimmte Uhrzeit senden
        - [ ] Als Slack-Bot-Nachricht an User X in Form einer Tabelle
        - [ ] Als Slack-Bot-Nachricht an Channel Y in Form einer Tabelle
    - [ ] Admin-Funktionalität
      - [ ] Admin-Befehle `/order admin`
        - [ ] Produkte in der Datenbank hinzufügen
        - [ ] Produkte in der Datenbank löschen
        - [ ] Produkte in der Datenbank ändern
        - [ ] Produkte in der Datenbank aktivieren/deaktivieren
      - [ ] Aktuelle Bestellungen anzeigen `/order admin list`
      - [ ] Installieren und implementieren von prettytable als "Tabelle" für Slack
        [Prettytables](https://pypi.org/project/prettytable/)

### Erweiterte Bestellungs-Funktionen, um bestehende Bestellungen zu ändern/löschen
- [ ] **feature_order_remove_flat_1.0**
    - [ ] Grundlegende Änderungsfunktionalität
      - [ ] Produkte aus aktueller Bestellung löschen `/order remove`
        - [ ] Löschen der Produkte aus der Bestellung bestätigen oder abbrechen nach ausgabe `/order remove accept` , `/order remove cancel`
      - [ ] Alle Produkte aus aktueller Bestellung löschen `/order remove all`
### Erweiterte Grundfunktionalität für eine individuell eingestellte Benachrichtigung
- [ ] **feature_order_reminder_flat_1.0**
    - [ ] Anzeigen der aktuellen Erinnerungen, wenn vorhanden (ansonsten Anleitung) `/order reminder`
      - [ ] Allgemeine TÄGLICHE Erinnerung hinzufügen `/order reminder day` 
        - [ ] Grundlegende Funktionalität für tägliche Erinnerungen einpflegen
      - [ ] Allgemeine WÖCHENTLICHE Erinnerung hinzufügen `/order reminder wday`
        - [ ] Grundlegende Funktionalität für wöchentliche Erinnerungen einpflegen
    - [ ] Stoppen aller Erinnerungen `/order reminder stop [Date (DD.MM.YYYY)]`
    - [ ] Stoppen einer bestimmten Erinnerung `/order reminder stop [ID/Name]`
    - [ ] Löschen aller Erinnerungen `/order reminder delete all`
      - [ ] Bestätigung der Löschung aller Erinnerungen `/order reminder delete accept` , `/order reminder delete cancel`
    - [ ] Löschen einer bestimmten Erinnerung `/order reminder delete [ID/Name]`
      - [ ] Bestätigung der Löschung einer bestimmten Erinnerung `/order reminder delete accept` , `/order reminder delete cancel`
### Erweiterte Funktion zum Ändern des in der Tabelle angezeigten Namens (lower priority)
- [ ] **feature_order_name_change_flat_1.0**
### Erweiterte Funktionalität für das individuelle Speichern von Bestellungstemplates
- [ ] **feature_order_save_flat_1.0**
### Erweiterte Funktion zur Statusänderung der Anwesenheit
- [ ] **feature_away_flat_1.0**
    - [ ] feature_vacation_flat_1.0
    - [ ] feature_home_office_flat_1.0
### Erweiterte Funktionalität für die Anzeige der Bestellhistorie
- [ ] **feature_order_ListAndSend_flat_1.0**
### Erweiterte Funktionalitäten
- [ ] **feature_order_undo_flat_1.0**
    - [ ] `/order undo` letztes ausgeführtes Kommando zurücksetzten
