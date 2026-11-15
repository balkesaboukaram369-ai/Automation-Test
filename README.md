# SauceDemo – Regressionstest-Suite mit Python & Playwright

Automatisierte Regressionstests für den Webshop **https://www.saucedemo.com/** („Swag Labs“).
Die Suite prüft alle Funktionen des Shops in **Chromium, Firefox und WebKit (Safari-Engine)**
sowie die Kernabläufe auf **emulierten Mobilgeräten** und erzeugt nach jedem Lauf einen **HTML-Bericht**.

> Testplan, Testfälle, Annahmen und Fehlerberichte: **[docs/Testplan.md](docs/Testplan.md)**

---

## Inhalt

1. [Was wird getestet?](#1-was-wird-getestet)
2. [Voraussetzungen](#2-voraussetzungen)
3. [Installation](#3-installation)
4. [Tests ausführen](#4-tests-ausführen)
5. [HTML-Bericht](#5-html-bericht)
6. [Projektstruktur](#6-projektstruktur)
7. [Aufbau und Konzepte](#7-aufbau-und-konzepte)
8. [Bekannte Fehler (XFAIL)](#8-bekannte-fehler-xfail)
9. [Fehleranalyse](#9-fehleranalyse)
10. [Grenzen und Erweiterungsmöglichkeiten](#10-grenzen-und-erweiterungsmöglichkeiten)

---

## 1. Was wird getestet?

| Bereich                   | Datei                     | Beispiele                                                                                     |
| ------------------------- | ------------------------- | --------------------------------------------------------------------------------------------- |
| Login                     | `test_login.py`           | gültige/ungültige Daten, Pflichtfelder, Groß-/Kleinschreibung, Login-Dauer, geschützte Seiten |
| Sitzung & Darstellung     | `test_session.py`         | Ablauf der Sitzung, Logout löscht Cookie, abgeschnittene Fehlermeldungen                      |
| Produktliste & Sortierung | `test_inventory.py`       | Produktdaten, Bilder, 4 Sortierungen, Warenkorb-Zähler                                        |
| Produktdetails            | `test_product_details.py` | Daten aller 6 Produkte, Hinzufügen/Entfernen, Zurück                                          |
| Warenkorb                 | `test_cart.py`            | Inhalt, Entfernen, Neu laden, Logout/Login                                                    |
| Checkout                  | `test_checkout.py`        | Kompletter Kauf, Pflichtfelder, Summe/Steuer/Total, Abbrechen                                 |
| PDF-Beleg                 | `test_order_pdf.py`       | Download und Inhalt des Belegs                                                                |
| Menü                      | `test_menu.py`            | Alle Einträge inkl. Reset App State und Dynamic Catalog                                       |
| Footer-Links              | `test_external_links.py`  | X, Facebook, LinkedIn öffnen die richtige Seite                                               |
| Dynamic Catalog           | `test_dynamic_catalog.py` | Lazy Load, Spinner, Slider                                                                    |
| Netzwerk                  | `test_network.py`         | Verhalten ohne Internet und bei langsamer Verbindung                                          |
| Doppelklick-Schutz        | `test_double_submit.py`   | Doppelte Bestellung durch Doppelklick / Browser-Zurück / zweiten Tab                          |
| Demo-Benutzer mit Fehlern | `test_special_users.py`   | problem_user, error_user, visual_user                                                         |
| Mobilgeräte               | `test_mobile.py`          | iPhone 15, Pixel 7, iPad                                                                      |
| Antwortzeiten             | `test_performance.py`     | Sortieren, Zurück zur Liste, Back Home (Zeitlimit 3 s)                                        |
| Barrierefreiheit          | `test_accessibility.py`   | Alternativtexte, Bedienung nur mit Tastatur                                                   |

Insgesamt **543 Testläufe**: 178 Testläufe je Desktop-Browser (× 3 Browser) plus 9 Testläufe
auf Mobilgeräten (3 Tests × 3 Geräte). Parametrisierte Tests (z. B. alle Sortierungen) zählen
dabei als mehrere Testläufe.

Jeder Test hat eine **Priorität** aus dem Testplan (Hoch / Mittel / Niedrig), siehe Abschnitt 7.

## 2. Voraussetzungen

- **Python 3.10 oder neuer** – Download: https://www.python.org/downloads/
  (unter Windows bei der Installation „Add python.exe to PATH“ anhaken)
- **Git** – https://git-scm.com/
- Internetverbindung (die Tests laufen gegen die Live-Webseite)

Prüfen, ob alles installiert ist:

```bash
python --version
git --version
```

## 3. Installation

```bash
# 1. Repository klonen und in den Ordner wechseln
git clone https://github.com/<BENUTZERNAME>/<REPOSITORY>.git
cd <REPOSITORY>

# 2. Virtuelle Umgebung anlegen (eigener, sauberer Python-Bereich nur für dieses Projekt)
python -m venv .venv

# 3. Virtuelle Umgebung aktivieren
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    macOS / Linux:
source .venv/bin/activate

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# 5. Browser für Playwright herunterladen (Chromium, Firefox, WebKit)
playwright install
```

> Falls PowerShell das Aktivieren blockiert: einmalig
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ausführen.

### Zugangsdaten konfigurieren

Das Passwort wird **nicht** im Repository gespeichert. Es wird aus einer lokalen Datei `.env` gelesen:

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

Dann in `.env` das Passwort eintragen. Es steht öffentlich auf der Login-Seite von saucedemo.com
unter „Password for all users“:

```
SAUCE_PASSWORD=secret_sauce
```

Optionale Einstellungen in `.env`:

| Variable                   | Bedeutung                    | Standard                     |
| -------------------------- | ---------------------------- | ---------------------------- |
| `BASE_URL`                 | Adresse des Shops            | `https://www.saucedemo.com/` |
| `LOGIN_TIME_LIMIT_SECONDS` | Zeitlimit für den Login-Test | `3`                          |

## 4. Tests ausführen

Alle Befehle im Projektordner und mit aktivierter virtueller Umgebung ausführen.

| Ziel                                         | Befehl                                           |
| -------------------------------------------- | ------------------------------------------------ |
| **Alle Tests** (3 Browser + Mobilgeräte)     | `pytest`                                         |
| Alle Tests **parallel** (deutlich schneller) | `pytest -n 4`                                    |
| Nur ein Browser                              | `pytest --browser firefox`                       |
| Nur eine Datei                               | `pytest tests/test_login.py`                     |
| Nur ein Test                                 | `pytest tests/test_login.py -k login_01`         |
| Nur die wichtigsten Kernfunktionen           | `pytest -m smoke`                                |
| Nur Tests mit Priorität Hoch                 | `pytest -m prio_hoch`                            |
| Priorität Hoch und Mittel                    | `pytest -m "prio_hoch or prio_mittel"`           |
| Nur Mobilgeräte                              | `pytest -m mobile`                               |
| Ohne externe Webseiten                       | `pytest -m "not external"`                       |
| Browser sichtbar mitlaufen lassen            | `pytest --headed --browser chromium -k login_01` |
| Sichtbar und verlangsamt (0,5 s pro Schritt) | `pytest --headed --slowmo 500 --browser chromium -k login_01` |
| Im installierten Google Chrome statt Chromium | `pytest --browser chromium --browser-channel chrome` |
| Ausführliche Ausgabe                         | `pytest -v`                                      |

> Standardmäßig laufen die Browser **unsichtbar** (headless) – das ist schneller und auch auf
> Servern ohne Bildschirm möglich. `--headed` zeigt das Browserfenster an.
> „Chromium“ ist der Open-Source-Browser, auf dem Google Chrome und Microsoft Edge aufbauen;
> Playwright bringt ihn mit. Mit `--browser-channel chrome` wird das installierte Google Chrome verwendet.

Dauer: ca. 6–13 Minuten parallel mit 4 Prozessen (`-n 4`), je nach Rechner und
Internetverbindung; ohne Parallelisierung entsprechend länger. Zu viele parallele Prozesse
überlasten Rechner und Webseite und führen zu Zeitüberschreitungen.

> **Hinweis:** Da die Tests gegen die öffentliche Live-Seite laufen, kann vereinzelt eine
> Zeitüberschreitung (`TimeoutError` bei `Page.goto`) durch eine langsame Verbindung auftreten.
> Einen solchen Test einzeln wiederholen (siehe Abschnitt 9), bevor ein Fehler gemeldet wird.

### Ergebnis in der Konsole lesen

| Zeichen | Status | Bedeutung                                                            |
| ------- | ------ | -------------------------------------------------------------------- |
| `.`     | PASSED | Test bestanden                                                       |
| `x`     | XFAIL  | Bekannter Fehler wurde wie erwartet nachgewiesen (siehe Abschnitt 8) |
| `F`     | FAILED | **Neuer Fehler** oder Regression – muss untersucht werden            |
| `E`     | ERROR  | Problem in der Testvorbereitung (z. B. Seite nicht erreichbar)       |

## 5. HTML-Bericht

Nach jedem Lauf wird automatisch **`reports/report.html`** erzeugt (eine einzige Datei,
alle Screenshots sind eingebettet).

Öffnen:

```bash
# Windows
start reports\report.html
# macOS
open reports/report.html
# Linux
xdg-open reports/report.html
```

Der Bericht ist an den Testabschlussbericht nach ISTQB angelehnt und enthält:

- **Environment:** Testobjekt (URL), Browser, Testauswahl, Python-, pytest- und Playwright-Version
- **Testabschluss-Übersicht:**
  - Kennzahlen (ausgeführt, bestanden, fehlgeschlagen, bekannte Fehler, Bestanden-Quote)
  - **Bewertung der Endekriterien** aus dem Testplan (Abschnitt 7) mit Freigabeempfehlung
  - Ergebnis **nach Priorität**
  - Liste der **offenen bekannten Fehler** (BUG-ID, Beschreibung, Anzahl betroffener Tests)
- **Ergebnistabelle:** pro Test die **Priorität** (farbig), eine **Beschreibung mit Testfall-ID**
  (z. B. „LOGIN-01: …“) und bei XFAIL die **Bug-ID**
- bei Fehlschlag die Fehlerausgabe, einen **Screenshot** und die URL zum Zeitpunkt des Fehlers

Bestandene Tests und bekannte Fehler sind zugeklappt (Klick auf die Zeile öffnet die Details),
neue Fehlschläge sind sofort aufgeklappt.
Restrisiken, Beobachtungen und offene Fragen stehen in [docs/Testplan.md](docs/Testplan.md).

## 6. Projektstruktur

```
├── config/
│   ├── settings.py          # Konfiguration (URL, Passwort aus .env, Zeitlimit)
│   └── report.css           # Aussehen des HTML-Berichts
├── data/
│   ├── test_data.py         # Testdaten: Benutzer, Produkte, Fehlermeldungen, Seitentitel
│   └── known_bugs.py        # Verzeichnis aller gefundenen Fehler (BUG-01 …)
├── pages/                   # Page Objects – eine Klasse pro Seite
│   ├── base_page.py         # gemeinsame Basis aller Seiten
│   ├── header.py            # Menü, Warenkorb-Symbol, Footer (auf allen Seiten)
│   ├── login_page.py
│   ├── inventory_page.py    # Produktliste
│   ├── product_page.py      # Produktdetails
│   ├── cart_page.py
│   ├── checkout_page.py     # die drei Checkout-Schritte
│   └── dynamic_catalog_page.py
├── utils/
│   ├── flows.py             # wiederkehrende Abläufe (Login, Produkte bis zur Übersicht)
│   ├── priority.py          # Kurznamen für die Prioritäten (@HOCH, @MITTEL, @NIEDRIG)
│   └── report_summary.py    # Testabschluss-Übersicht oben im HTML-Bericht
├── tests/
│   ├── conftest.py          # Fixtures (Vorbereitungen) für die Tests
│   └── test_*.py            # die Testfälle
├── docs/
│   └── Testplan.md          # Testplan, Testfälle, Fehlerberichte
├── conftest.py              # Browser-Auswahl, HTML-Bericht, Screenshots
├── pytest.ini               # pytest-Einstellungen
├── requirements.txt         # benötigte Python-Pakete (feste Versionen)
├── .env.example             # Vorlage für die Zugangsdaten
└── .gitignore               # Dateien, die nicht ins Repository gehören
```

## 7. Aufbau und Konzepte

### Page Object Model (POM)

Jede Seite des Shops ist eine Python-Klasse in `pages/`. Sie kennt die **Elemente**
(Locator) und **Aktionen** der Seite. Die Tests beschreiben nur noch _was_ passiert:

```python
login_page.login("standard_user", PASSWORD)
expect(inventory.title).to_have_text(PageTitles.INVENTORY)
```

Ändert sich ein Button auf der Webseite, wird er an **einer** Stelle im Page Object angepasst –
nicht in jedem Test.

### Locator

Elemente werden bevorzugt über das Attribut `data-test` gefunden, das SauceDemo extra für
Tests bereitstellt (`page.get_by_test_id("login-button")`). Es ändert sich nicht, wenn sich
Design oder Text ändern – das macht die Tests stabil.

### Fixtures

Fixtures sind Vorbereitungen, die pytest automatisch vor einem Test ausführt
(`tests/conftest.py`). Beispiel: `inventory_page` meldet `standard_user` an und öffnet die Produktseite.
Jeder Test bekommt einen **neuen Browser-Kontext** – die Tests sind dadurch unabhängig
voneinander und können in beliebiger Reihenfolge und parallel laufen.

### Assertions mit automatischem Warten

`expect(...)` von Playwright wartet automatisch (bis zu 10 Sekunden), bis die Bedingung
erfüllt ist. Feste Wartezeiten (`sleep`) werden vermieden.

### Parametrisierung

Ein Test kann mit mehreren Datensätzen laufen (`@pytest.mark.parametrize`). So wird z. B.
die komplette Entscheidungstabelle der Pflichtfelder mit einer einzigen Testfunktion geprüft.

### Prioritäten und Markierungen

Jeder Test trägt die Priorität aus dem Testplan als Markierung (`@HOCH`, `@MITTEL`, `@NIEDRIG`).
Sie steht im HTML-Bericht in der Spalte „Priorität“ und dient zur Auswahl, wenn wenig Zeit ist:

| Markierung | Anzahl Testläufe | Bedeutung |
|---|---|---|
| `prio_hoch` | 150 | Geld, Daten, Sicherheit, Kernfunktionen |
| `prio_mittel` | 270 | Funktion beeinträchtigt |
| `prio_niedrig` | 123 | Darstellung, Komfort |
| `smoke` | 18 | schnellster Überblick: Login, Produkte, Warenkorb, Kauf, Logout |

Die Priorität bestimmt nicht die Reihenfolge – die Tests sind unabhängig und laufen parallel.
Fehlt bei einem neuen Test die Priorität, gibt pytest eine Warnung aus.

### Zeitsteuerung

Der Slider wechselt per Timer automatisch. Mit `page.clock.install()` und `pause_at()` hält
der Test die Uhr des Browsers an – so ist das Ergebnis zuverlässig und nicht vom Zufall abhängig.

## 8. Bekannte Fehler (XFAIL)

Gefundene Fehler sind in `data/known_bugs.py` erfasst (BUG-01 bis BUG-26) und die
betroffenen Tests mit `known_bug("BUG-xx")` markiert:

- Der Test läuft trotzdem und **weist den Fehler nach** → Status **XFAIL** (erwarteter Fehlschlag).
- `strict=True`: Wird ein Fehler behoben, schlägt der Test als **XPASS(strict)** fehl. So fällt
  sofort auf, dass die Markierung entfernt werden muss.
- Tests werden **nicht übersprungen**, um einen grünen Bericht zu erhalten.

Die Fehlerberichte (Schritte, erwartet, tatsächlich, Schweregrad) stehen in
[docs/Testplan.md](docs/Testplan.md#5-fehlerberichte).

## 9. Fehleranalyse

Wenn ein Test fehlschlägt:

1. **HTML-Bericht** öffnen → Screenshot und URL beim Fehlschlag ansehen.
2. **Playwright-Trace** öffnen (Schritt für Schritt mit DOM, Netzwerk und Konsole).
   Er wird nur bei Fehlschlägen unter `reports/traces/` gespeichert:
   ```bash
   playwright show-trace reports/traces/<ordner-des-tests>/trace.zip
   ```
3. Test einzeln und sichtbar wiederholen:
   ```bash
   pytest tests/test_cart.py -k cart_02 --headed --browser chromium
   ```

## 10. Grenzen und Erweiterungsmöglichkeiten

**Grenzen**

- WebKit entspricht der Safari-Engine, ist aber nicht das echte Safari auf Apple-Geräten.
- Mobilgeräte werden emuliert (Bildschirm, Touch, User-Agent), nicht auf echten Geräten getestet.
- Die Demo hat kein echtes Bezahlsystem – Doppelzahlungen werden über Anzeichen im Browser erkannt.
- Die Tests laufen gegen die öffentliche Live-Seite; Änderungen dort können Tests beeinflussen.

**Erweiterungsmöglichkeiten**

- Visueller Screenshot-Vergleich (`expect(page).to_have_screenshot()`)
- Automatischer Lauf bei jedem Push mit GitHub Actions (CI)
- Barrierefreiheits-Prüfung (z. B. mit axe-core)
- Lasttests mit k6 oder JMeter
