# Testplan und Testergebnisse – SauceDemo

| | |
|---|---|
| **Testobjekt** | Webshop https://www.saucedemo.com/ („Swag Labs“) |
| **Testart** | Regressionstest (funktional + ausgewählte nicht-funktionale Aspekte) |
| **Testbasis** | Keine schriftliche Spezifikation vorhanden. Erwartetes Verhalten wurde aus dem Ist-Verhalten der Anwendung (geprüft am 07.–14.11.2026), gängiger E-Commerce-Praxis und abgestimmten Annahmen abgeleitet. |
| **Werkzeuge** | Python, Playwright, pytest, pytest-html |
| **Browser** | Chromium, Firefox, WebKit (Safari-Engine) – Desktop 1280×720 |
| **Mobilgeräte (emuliert)** | iPhone 15 (WebKit), Pixel 7 (Chromium), iPad gen 7 (WebKit) |

---

## 1. Ziel und Umfang

Ziel ist eine automatisierte Regressions-Test-Suite, die alle Funktionen des Shops
prüft und nach jeder Änderung erneut ausgeführt werden kann.

**Im Umfang:** Login, Sitzung, Produktliste, Sortierung, Produktdetails, Warenkorb,
Checkout, PDF-Beleg, Menü, Footer-Links, Dynamic Catalog (Lazy Load, Spinner, Slider),
Verhalten bei fehlender/langsamer Verbindung, Doppelklick-Schutz, Antwortzeiten der
Produktliste, Eingaben mit Sonderzeichen/HTML, grundlegende Barrierefreiheit,
Demo-Benutzer mit eingebauten Fehlern, Kernabläufe auf Mobilgeräten.

**Nicht im Umfang (Out of Scope):**
- Last- und Performancetests (z. B. viele gleichzeitige Benutzer) – dafür eignen sich Werkzeuge wie JMeter oder k6
- Pixelgenaue visuelle Vergleiche (Screenshot-Vergleich) – siehe „Erweiterungsmöglichkeiten“ in der README
- Inhalte externer Webseiten (X, Facebook, LinkedIn, saucelabs.com) – geprüft wird nur die Weiterleitung
- Echtes Safari auf echten Apple-Geräten – Playwright nutzt die WebKit-Engine
- Vollständige Barrierefreiheitsprüfung nach WCAG – geprüft werden nur Grundlagen (Alternativtexte, Tastaturbedienung)
- Penetrationstests (z. B. systematische SQL-Injection, XSS, Manipulation von Cookies) – geprüft wird nur sicherheitsrelevantes Verhalten, das Teil der Funktion ist (falsche Anmeldedaten, geschützte Seiten, Logout, einfache SQL-Injection). Auffälligkeiten aus dem explorativen Testen stehen in Abschnitt 6 (B-12).

## 2. Testverfahren (nach ISTQB)

| Verfahren | Anwendung |
|---|---|
| Äquivalenzklassenbildung | Benutzername/Passwort (gültig, gesperrt, unbekannt, leer, falsche Schreibweise), Benutzertypen |
| Entscheidungstabelle | Pflichtfelder Login (2 Felder) und Checkout (3 Felder) |
| Zustandsübergänge | Warenkorb (leer → gefüllt → bestellt), Sitzung (angemeldet → abgelaufen → abgemeldet) |
| Anwendungsfallbasiert | Kompletter Kaufprozess (End-to-End) |
| Erfahrungsbasiert / Error Guessing | Großschreibung, Leerzeichen, Doppelklick, Browser-Zurück, direkte URL-Aufrufe, Offline, HTML/Skript in Eingabefeldern, ungültige Produkt-ID |
| Explorativ | Manuelle Erkundung; Fund von BUG-10 (abgeschnittene Fehlermeldung), BUG-22/23 (Seitenmenü), BUG-25 (Meldung kehrt nach F5 zurück), BUG-26 (Doppelbestellung aus zwei Tabs) und der Ausweitung von BUG-01 (Verzögerung bei jeder Anzeige der Produktliste) |

## 3. Annahmen (mangels Spezifikation)

| Nr. | Annahme |
|---|---|
| A-1 | Ein Login ist „schnell genug“, wenn die Produktseite nach spätestens **3 Sekunden** sichtbar ist (Orientierung: Google Core Web Vitals ≤ 2,5 s, mit Puffer gegen instabile Tests). Dasselbe Limit gilt für jedes erneute Anzeigen der Produktliste (Sortieren, Zurück, Back Home). |
| A-2 | Benutzername und Passwort sind **exakt** zu prüfen (Groß-/Kleinschreibung, Leerzeichen). |
| A-3 | Ohne Internetverbindung muss **jede** Aktion gestoppt und ein klarer Offline-Hinweis angezeigt werden. |
| A-4 | Eine Bestellung darf nur **einmal** abgeschlossen werden (Schutz vor Doppelklick, Browser-Zurück und einem zweiten Tab). |
| A-5 | Checkout ist nur mit mindestens einem Produkt und nur in der richtigen Schrittfolge möglich. |
| A-6 | Der Produktkatalog (Lazy Load) ist endlich und enthält keine doppelten Einträge. |
| A-7 | Ein Pflichtfeld, das nur Leerzeichen enthält, gilt als leer. |
| A-8 | Das Seitenmenü verhält sich wie üblich: Klick außerhalb schließt es, die Seite dahinter ist währenddessen nicht bedienbar. |

## 4. Testfälle

Jeder Testfall ist im Code an seiner ID erkennbar (Docstring und Testname).
Legende Ergebnis: ✅ bestanden · 🐞 bekannter Fehler (XFAIL)

**Priorisierung (risikobasiert):**

| Priorität | Richtlinie |
|---|---|
| Hoch | Geld, Daten oder Sicherheit betroffen, oder Kernfunktion des Shops (Login, Warenkorb, Kauf) |
| Mittel | Funktion beeinträchtigt, der Kunde kann aber weiter einkaufen |
| Niedrig | Darstellung, Komfort, Nebenfunktionen |

Die Priorität ist im Code als Markierung hinterlegt (`@HOCH`, `@MITTEL`, `@NIEDRIG` →
`prio_hoch`, `prio_mittel`, `prio_niedrig`) und erscheint im HTML-Bericht als eigene Spalte.
So lassen sich bei wenig Zeit gezielt nur wichtige Tests ausführen, z. B. `pytest -m prio_hoch`.

### 4.1 Login – `tests/test_login.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| LOGIN-01 | Login standard_user | Produktseite „Products“ | Hoch | ✅ |
| LOGIN-02 | locked_out_user | Meldung „Sorry, this user has been locked out.“ | Hoch | ✅ |
| LOGIN-03 | Falsches Passwort | Meldung „Username and password do not match …“ | Hoch | ✅ |
| LOGIN-04 | Unbekannter Benutzer | Gleiche Meldung wie LOGIN-03 | Mittel | ✅ |
| LOGIN-05 | Beide Felder leer | „Username is required“ | Mittel | ✅ |
| LOGIN-06 | Passwort leer | „Password is required“ | Mittel | ✅ |
| LOGIN-07 | Benutzername leer | „Username is required“ | Mittel | ✅ |
| LOGIN-08 | X in der Fehlermeldung | Meldung und Fehlersymbole verschwinden | Niedrig | ✅ |
| LOGIN-09 | Login-Dauer standard_user / performance_glitch_user | ≤ 3 s | Mittel | ✅ / 🐞 BUG-01 |
| LOGIN-10 | Interne Seiten ohne Login (5 Seiten) | Login-Seite mit Hinweis | Hoch | ✅ |
| LOGIN-11 | Browser-Zurück nach Logout | Kein Zugriff auf das Konto | Hoch | ✅ |
| LOGIN-21 | Geschlossene Fehlermeldung nach F5 (Logout → Zurück → X → F5) | Meldung bleibt verschwunden | Niedrig | 🐞 BUG-25 |
| LOGIN-12 | `STANDARD_USER` | Abgelehnt | Mittel | ✅ |
| LOGIN-13 | Leerzeichen vor/nach Benutzername | Abgelehnt | Mittel | ✅ |
| LOGIN-14 | Passwortfeld | Eingabe verdeckt (type=password) | Niedrig | ✅ |
| LOGIN-15 | Login mit Enter-Taste | Produktseite | Mittel | ✅ |
| LOGIN-16 | Alle 5 aktiven Benutzer | Login möglich | Mittel | ✅ |
| LOGIN-17 | Passwort in anderer Schreibweise | Abgelehnt | Hoch | ✅ |
| LOGIN-18 | Leerzeichen vor/nach Passwort | Abgelehnt | Mittel | ✅ |
| LOGIN-19a/b/c | SQL-Injection `' OR 1=1 --` im Benutzernamen / im Passwort / in beiden Feldern | Abgelehnt | Hoch | ✅ |
| LOGIN-20 | Sehr langer Benutzername (1000 Zeichen) | Abgelehnt, Seite reagiert normal | Niedrig | ✅ |

### 4.2 Sitzung und Darstellung – `tests/test_session.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| SESS-01 | Abgelaufene Sitzung, dann Klick | Login-Seite | Hoch | ✅ |
| SESS-02 | Meldung nach Sitzungsablauf | Sagt klar „Sitzung abgelaufen“ | Niedrig | 🐞 BUG-11 |
| SESS-04 | Lebensdauer des Sitzungs-Cookies | 600 s (Ist-Verhalten) | Niedrig | ✅ |
| SESS-05 | Logout | Sitzungs-Cookie gelöscht | Hoch | ✅ |
| UI-01a/b/c | Lange Fehlermeldungen: „You can only access …“, „Username and password do not match …“, „locked out“ | Vollständig sichtbar | Niedrig | a/b: 🐞 BUG-10 · c: Firefox 🐞 BUG-10, Chromium/WebKit ✅ |

### 4.3 Produktliste und Sortierung – `tests/test_inventory.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| INV-01 | Produktdaten | 6 Produkte, Name/Preis/Beschreibung korrekt | Hoch | ✅ |
| INV-02 | Produktbilder | Jedes Produkt hat sein Bild | Mittel | ✅ |
| INV-03 | Standard-Sortierung | Name (A to Z); geprüft wird die Regel „alphabetisch“, nicht eine feste Namensliste | Mittel | ✅ |
| INV-04/05 | Sortierung Name A–Z / Z–A | Korrekte Reihenfolge (Regel, nicht feste Liste – bleibt bei neuen Produkten gültig) | Mittel | ✅ |
| INV-06/07 | Sortierung Preis auf-/absteigend | Preise korrekt geordnet | Mittel | ✅ |
| INV-08 | Add to cart | Button „Remove“, Zähler 1 | Hoch | ✅ |
| INV-09 | Mehrere Produkte | Zähler stimmt | Mittel | ✅ |
| INV-10 | Remove auf Produktseite | Zähler sinkt / verschwindet | Mittel | ✅ |
| INV-11 | Sortieren mit gefülltem Warenkorb | Warenkorb unverändert | Niedrig | ✅ |

### 4.4 Produktdetails – `tests/test_product_details.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| PD-01 | Details aller 6 Produkte | Gleiche Daten wie Liste | Hoch | ✅ |
| PD-02 | Öffnen über Bild | Detailseite | Niedrig | ✅ |
| PD-03 | Add to cart auf Detailseite | Zähler 1, Button „Remove“ | Hoch | ✅ |
| PD-04 | Remove auf Detailseite | Zähler verschwindet | Mittel | ✅ |
| PD-05 | Back to products | Produktliste | Mittel | ✅ |
| PD-06 | Zustand Detailseite ↔ Liste | „Remove“ auch in der Liste | Mittel | ✅ |
| PD-07 | Ungültige Produkt-ID in der URL (99, -1, abc) | „ITEM NOT FOUND“, Zurück möglich | Niedrig | ✅ |

### 4.5 Warenkorb – `tests/test_cart.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| CART-01 | Leerer Warenkorb | Keine Produkte, kein Zähler | Mittel | ✅ |
| CART-02 | Inhalt | Produkte, Preise, Menge 1 | Hoch | ✅ |
| CART-03 | Remove im Warenkorb | Produkt und Zähler aktualisiert | Hoch | ✅ |
| CART-04 | Continue Shopping | Produktseite, Warenkorb erhalten | Mittel | ✅ |
| CART-05 | Neu laden | Warenkorb erhalten | Mittel | ✅ |
| CART-06 | Logout + Login | Warenkorb erhalten | Mittel | ✅ |
| CART-07 | Checkout-Button | Seite „Your Information“ | Hoch | ✅ |
| CART-08 | Zwei Tabs | Produkt aus Tab 1 erscheint nach Neuladen in Tab 2 | Niedrig | ✅ |

### 4.6 Checkout – `tests/test_checkout.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| CO-01 | Kompletter Kauf (E2E) | „Thank you for your order!“ | Hoch | ✅ |
| CO-02–05 | Pflichtfelder (Entscheidungstabelle) | Meldung zum fehlenden Feld | Hoch | ✅ |
| CO-06 | Cancel in Schritt 1 | Warenkorb | Mittel | ✅ |
| CO-07 | Übersicht | Produkte, Zahlungs- und Versandinfo | Mittel | ✅ |
| CO-08 | Item total | Summe der Preise | Hoch | ✅ |
| CO-09 | Steuer | 8 %, kaufmännisch gerundet (Steuersatz aus dem Verhalten der Seite abgeleitet, siehe B-15) | Hoch | ✅ |
| CO-10 | Total | Zwischensumme + Steuer | Hoch | ✅ |
| CO-11 | Cancel in Übersicht | Produktseite, Warenkorb erhalten | Mittel | ✅ |
| CO-12 | Nach Finish | Warenkorb leer | Hoch | ✅ |
| CO-13 | Back Home | Produktseite, nichts im Warenkorb | Mittel | ✅ |
| CO-15 | Checkout mit leerem Warenkorb | Button deaktiviert/ausgeblendet | Mittel | 🐞 BUG-03 |
| CO-16a/b | Übersicht / Bestätigung per URL | Nicht erreichbar | Mittel | 🐞 BUG-04 |
| CO-17 | Pflichtfelder nur mit Leerzeichen | Abgelehnt mit Fehlermeldung | Mittel | 🐞 BUG-24 |
| CO-18 | HTML/JavaScript in den Feldern | Wird nicht ausgeführt (Schutz vor XSS) | Hoch | ✅ |

### 4.7 PDF-Beleg – `tests/test_order_pdf.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| PDF-01 | Download | Gültige PDF-Datei `swag-labs-order-….pdf` | Mittel | ✅ |
| PDF-02 | Kundendaten | Name und PLZ enthalten | Mittel | ✅ |
| PDF-03 | Produkte | Alle Produkte mit Preis | Hoch | ✅ |
| PDF-04 | Beträge | Stimmen mit Übersicht überein | Hoch | ✅ |
| PDF-05 | Datum | Heutiges Datum | Niedrig | ✅ |

### 4.8 Menü – `tests/test_menu.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| MENU-01 | Menü öffnen | 5 Einträge | Mittel | ✅ |
| MENU-02 | Menü schließen | Menü ausgeblendet | Niedrig | ✅ |
| MENU-03 | All Items (vom Warenkorb) | Produktseite | Mittel | ✅ |
| MENU-04 | About | saucelabs.com | Niedrig | ✅ |
| MENU-05 | Logout | Login-Seite | Hoch | ✅ |
| MENU-06 | Reset App State | Warenkorb leer | Mittel | ✅ |
| MENU-07 | Reset App State | Buttons wieder „Add to cart“ | Mittel | 🐞 BUG-02 |
| MENU-08 | Dynamic Catalog (3 Einträge) | Jeweilige Seite öffnet sich | Niedrig | ✅ |
| MENU-09 | Klick außerhalb des Menüs | Menü schließt sich | Niedrig | 🐞 BUG-22 |
| MENU-10 | Escape-Taste | Menü schließt sich | Niedrig | ✅ |
| MENU-11 | Klick auf die Seite bei offenem Menü | Keine Aktion (Seite gesperrt) | Mittel | 🐞 BUG-23 |

### 4.9 Footer-Links – `tests/test_external_links.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| LINK-01–03 | X, Facebook, LinkedIn | Neuer Tab mit richtiger Domain | Niedrig | ✅ |
| LINK-04 | Copyright | Aktuelles Jahr | Niedrig | ✅ |

### 4.10 Dynamic Catalog – `tests/test_dynamic_catalog.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| LAZY-01 | Erste Ansicht | 8 Produkte + 4 Platzhalter | Niedrig | ✅ |
| LAZY-02 | Scrollen | Weitere Produkte werden geladen | Mittel | ✅ |
| LAZY-03 | Doppelte Einträge | Keine | Niedrig | 🐞 BUG-08 |
| LAZY-04 | Ende der Liste | Liste endet | Niedrig | 🐞 BUG-09 |
| SPIN-01 | Ladezustand | Spinner sichtbar | Niedrig | ✅ |
| SPIN-02 | Nach dem Laden | 6 Produkte mit korrektem Preis | Niedrig | ✅ |
| SLD-01 | Punkte-Navigation | Passendes Produkt | Niedrig | ✅ |
| SLD-02 | Automatischer Wechsel | Produkt wechselt | Niedrig | ✅ |

### 4.11 Netzwerk – `tests/test_network.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| OFF-01 | Login offline | Offline-Hinweis | Hoch | 🐞 BUG-07 |
| OFF-02 | Sortieren offline | Offline-Hinweis | Niedrig | 🐞 BUG-07 |
| OFF-03 | Add to cart offline | Offline-Hinweis | Mittel | 🐞 BUG-07 |
| OFF-04 | Produktdetails offline | Offline-Hinweis | Niedrig | 🐞 BUG-07 |
| OFF-05 | Finish offline | Keine Bestellung, Offline-Hinweis | Hoch | 🐞 BUG-07 |
| OFF-06 | PDF offline | Offline-Hinweis | Mittel | 🐞 BUG-07 |
| OFF-07 | Verbindung kommt zurück | Seite funktioniert, Warenkorb erhalten | Hoch | ✅ |
| OFF-08 | Logout offline | Offline-Hinweis | Niedrig | 🐞 BUG-07 |
| SLOW-01–05 | Bilder laden sehr langsam | Login, Liste, Details, Kauf, Lazy Load bleiben bedienbar | Mittel | ✅ |

### 4.12 Doppelklick-Schutz – `tests/test_double_submit.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| DBL-01 | Doppelklick auf Finish | Bestellung nur einmal | Hoch | Chromium/WebKit 🐞 BUG-05 · Firefox ✅ |
| DBL-02 | Browser-Zurück nach Bestellung | Kein erneutes Finish möglich | Hoch | 🐞 BUG-06 |
| DBL-03 | Doppelklick auf Continue | Nur einmal verarbeitet | Niedrig | Chromium/WebKit 🐞 BUG-21 · Firefox ✅ |
| DBL-04 | Dieselbe Bestellung aus zwei Tabs | Zweiter Tab kann nicht erneut abschließen | Hoch | 🐞 BUG-26 |

### 4.13 Spezielle Demo-Benutzer – `tests/test_special_users.py`
`standard_user` dient jeweils als Referenz und besteht alle Tests.

| ID | Testfall | Fehler bei | Prio |
|---|---|---|---|
| SU-01 | Produktbilder | problem_user (BUG-12), visual_user (BUG-19) | Mittel |
| SU-02 | Sortierung Z–A | problem_user (BUG-13), error_user (BUG-20) | Mittel |
| SU-03 | Alle 6 Produkte in den Warenkorb | problem_user, error_user (BUG-14) | Mittel |
| SU-04 | Richtige Detailseite | problem_user (BUG-15) | Mittel |
| SU-05 | Checkout-Felder übernehmen Eingabe | problem_user, error_user (BUG-16) | Mittel |
| SU-06 | Finish schließt Bestellung ab | error_user (BUG-17) | Mittel |
| SU-07 | Korrekte Preise | visual_user (BUG-18) | Mittel |

### 4.14 Mobilgeräte – `tests/test_mobile.py`
Je Test auf iPhone 15, Pixel 7 und iPad:

| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| MOB-01 | Login und Layout | Alle Produkte, kein horizontales Scrollen | Hoch | ✅ |
| MOB-02 | Menü und Logout | Login-Seite | Mittel | ✅ |
| MOB-03 | Kompletter Kauf | Bestellbestätigung | Hoch | ✅ |

### 4.15 Antwortzeiten der Produktliste – `tests/test_performance.py`
Jeweils mit standard_user (Referenz) und performance_glitch_user, Limit 3 Sekunden (Annahme A-1):

| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| PERF-01 | Sortieren | Liste ≤ 3 s neu aufgebaut | Mittel | standard ✅ · glitch 🐞 BUG-01 (ca. 5,2 s) |
| PERF-02 | Zurück von der Detailseite | Liste ≤ 3 s sichtbar | Mittel | standard ✅ · glitch 🐞 BUG-01 (ca. 5,4 s) |
| PERF-03 | „Back Home“ nach der Bestellung | Liste ≤ 3 s sichtbar | Mittel | standard ✅ · glitch 🐞 BUG-01 (ca. 5,4 s) |

### 4.16 Barrierefreiheit (Grundlagen) – `tests/test_accessibility.py`
| ID | Testfall | Erwartetes Ergebnis | Prio | Ergebnis |
|---|---|---|---|---|
| A11Y-01 | Alternativtexte der Produktbilder | Produktname als `alt`-Text | Niedrig | ✅ |
| A11Y-02 | Login nur mit Tastatur | Tab, Eingabe, Enter → Produktseite | Mittel | ✅ |
| A11Y-03 | Menü per Tastatur | Fokus + Enter öffnet das Menü | Niedrig | ✅ |

---

## 5. Fehlerberichte

Schweregrad: **Hoch** = Geld/Daten/Sicherheit betroffen · **Mittel** = Funktion beeinträchtigt · **Niedrig** = Darstellung/Komfort

| ID | Titel | Schritte | Erwartet | Tatsächlich | Schwere |
|---|---|---|---|---|---|
| BUG-01 | Langsame Produktliste | Als performance_glitch_user: Login, Sortieren, Zurück von Detailseite, Back Home | ≤ 3 s | Jedes Anzeigen der Produktliste dauert ca. 5 s; alle anderen Aktionen sind normal schnell | Mittel |
| BUG-02 | Reset setzt Buttons nicht zurück | Produkt hinzufügen → Menü → Reset App State | Buttons „Add to cart“ | Button bleibt „Remove“, Warenkorb aber leer | Mittel |
| BUG-03 | Checkout mit leerem Warenkorb | Leeren Warenkorb öffnen → Checkout | Button deaktiviert/ausgeblendet | Weiterleitung zu „Your Information“; die Bestellung lässt sich komplett abschließen (Übersicht ohne Produkte, „Total: $0.00“, danach „Thank you for your order!“). Gleiches Verhalten, wenn alle Produkte vorher entfernt wurden | Mittel |
| BUG-04 | Checkout-Schritte überspringbar | Eingeloggt `/checkout-step-two.html` bzw. `/checkout-complete.html` aufrufen | Kein Zugriff | Übersicht bzw. „Thank you for your order!“ wird angezeigt | Mittel |
| BUG-05 | Doppelte Bestellung per Doppelklick | Übersicht → Doppelklick auf Finish | Einmal verarbeitet, Button danach deaktiviert | Zweimal verarbeitet (Chromium, WebKit) | Hoch |
| BUG-06 | Erneute Bestellung über Zurück | Bestellung abschließen → Browser-Zurück → Finish | Weiterleitung zur Produktseite | Übersicht mit aktivem Finish | Hoch |
| BUG-07 | Keine Offline-Erkennung | Seite öffnen → Verbindung trennen → beliebige Aktion | Offline-Hinweis, Aktion gestoppt | Alles läuft weiter, Bestellung wird „abgeschlossen“, PDF-Download schlägt still fehl | Hoch |
| BUG-08 | Doppelter Katalogeintrag | Dynamic Catalog → Lazy Load → scrollen | Jeder Eintrag einmal | „Test.allTheThings() T-Shirt (Red) (L)“ doppelt | Niedrig |
| BUG-09 | Endlose Produktliste | Lazy Load → weiter scrollen | Liste endet | Liste wiederholt sich endlos | Niedrig |
| BUG-10 | Abgeschnittene Fehlermeldung | Ohne Login `/inventory.html` aufrufen (1920×1080) | Text vollständig | Erste und letzte Zeile abgeschnitten (53 px Text, 45 px sichtbar). Ebenso „Username and password do not match …“; in Firefox zusätzlich „locked out“ (geprüft am 14.11.2026) | Niedrig |
| BUG-11 | Unklare Meldung bei Sitzungsablauf | Login → 10 Minuten warten → Klick | „Sitzung abgelaufen“ | „You can only access … when you are logged in.“ | Niedrig |
| BUG-12–20 | Absichtliche Fehler der Demo-Benutzer | siehe 4.13 | – | – | Mittel |
| BUG-21 | Doppelte Verarbeitung „Continue“ | Schritt 1 ausfüllen → Doppelklick auf Continue | Einmal verarbeitet | Zweimal verarbeitet (Chromium, WebKit) | Niedrig |
| BUG-22 | Menü schließt nicht bei Klick daneben | Menü öffnen → auf die Seite daneben klicken | Menü schließt sich | Menü bleibt offen (nur X oder Escape schließen es) | Niedrig |
| BUG-23 | Seite hinter dem Menü bedienbar | Menü öffnen → „Add to cart“ eines sichtbaren Produkts klicken | Keine Aktion, Seite abgedunkelt/gesperrt | Produkt wird in den Warenkorb gelegt; kein Overlay, Inhalte wirken abgeschnitten | Mittel |
| BUG-24 | Leerzeichen als Pflichtfeld-Eingabe | Checkout Schritt 1: alle Felder nur mit Leerzeichen → Continue | Fehlermeldung „… is required“ | Weiterleitung zur Übersicht | Mittel |
| BUG-25 | Fehlermeldung kehrt nach Neuladen zurück | Logout → Browser-Zurück → Meldung mit X schließen → F5 | Meldung bleibt verschwunden (wie bei „falsches Passwort“) | „You can only access '/inventory.html' …“ erscheint wieder; die Seite speichert sie in `history.state` (Chromium, Firefox, WebKit) | Niedrig |
| BUG-26 | Doppelte Bestellung aus zwei Tabs | Übersicht in zwei Tabs öffnen → Tab 1: Finish → Tab 2 (ohne Neuladen): Finish | Zweite Bestellung wird abgelehnt (Lösungsvorschlag: eindeutige Bestell-ID im Backend, jede Bestellung nur einmal verarbeiten = Idempotenz) | Tab 2 zeigt erneut „Thank you for your order!“, obwohl der Warenkorb leer ist (Chromium, Firefox, WebKit) | Hoch |

**Hinweis zu BUG-03, 04, 06, 07, 09, 22, 23, 24, 26:** Es gibt keine schriftliche Anforderung. Die
Erwartung beruht auf den Annahmen in Abschnitt 3 und sollte mit dem Kunden bestätigt werden.

## 6. Beobachtungen und offene Fragen an den Kunden

| Nr. | Beobachtung |
|---|---|
| B-1 | **Login-Prüfung im Browser:** Der Login funktioniert auch ohne Internetverbindung. Benutzername und Passwort werden also im Browser (JavaScript) geprüft, nicht auf einem Server. Für eine Demo akzeptabel, in einem echten Shop ein Sicherheitsrisiko. |
| B-2 | **Feste Sitzungsdauer:** Die Sitzung endet 10 Minuten nach dem Login, auch wenn der Kunde aktiv ist (keine Verlängerung bei Aktivität). Kunden könnten mitten im Einkauf abgemeldet werden. Gewünscht? |
| B-3 | **Uhrzeit im PDF:** Dateiname und Belegtext zeigen unterschiedliche Uhrzeiten (z. B. 12-45 im Dateinamen, 1:45 PM im Beleg) – vermutlich UTC gegenüber Ortszeit. |
| B-4 | **Reihenfolge der Größen** im Lazy-Load-Katalog ist uneinheitlich (z. B. Bolt T-Shirt: XS, M, L, XL, XXL, S). |
| B-5 | **Trim von Leerzeichen:** Ein Leerzeichen vor dem Benutzernamen (z. B. durch Kopieren) führt zur Ablehnung. Ein automatisches Entfernen könnte die Bedienung verbessern. |
| B-6 | **Barrierefreiheit Slider:** Der Slider wechselt alle 2 Sekunden automatisch und hält weder bei Mausberührung noch bei Fokus an. Es gibt keine Pause-Schaltfläche (vgl. WCAG 2.2.2 „Pausieren, Beenden, Ausblenden“). |
| B-7 | **Sortierung wird zurückgesetzt:** Nach dem Öffnen eines Produkts und „Back to products“ (ebenso nach Warenkorb → „Continue Shopping“ oder Neuladen) steht die Sortierung wieder auf „Name (A to Z)“. Der Kunde muss erneut sortieren. Gewünscht? |
| B-8 | **Menge nicht änderbar:** Im Warenkorb ist die Menge immer 1 und kann nicht geändert werden. Ein Produkt mehrfach zu kaufen ist nicht möglich. |
| B-9 | **Checkout-Daten gehen verloren:** Von der Übersicht mit Browser-Zurück zu Schritt 1 sind Vorname, Nachname und PLZ wieder leer. |
| B-10 | **Keine Formatprüfung:** Die PLZ akzeptiert Buchstaben (z. B. „ABCDE“), Namen und PLZ haben keine Längenbegrenzung (300 Zeichen werden akzeptiert). Ohne Anforderung zum Format nicht als Fehler gewertet. |
| B-12 | **Anmeldung per manipuliertem Cookie (Sicherheit):** Ohne Login genügt es, im Browser den Cookie `session-username=standard_user` zu setzen – danach ist der Shop mit allen Produkten erreichbar (geprüft am 11.11.2026). Der Login wird damit vollständig umgangen. Mit `locked_out_user` oder einem unbekannten Namen wird der Zugriff verweigert. Zusätzlich ist der Cookie weder `HttpOnly` noch `Secure`. Für eine Demo ohne Server erklärbar (siehe B-1), in einem echten Shop eine kritische Schwachstelle. Nicht automatisiert, da Penetrationstests außerhalb des Umfangs liegen. |
| B-13 | **Benutzername nur aus Leerzeichen:** Die Login-Seite meldet „Username and password do not match …“ statt „Username is required“. Leerzeichen gelten also nicht als leer (vgl. BUG-24 im Checkout). |
| B-14 | **Sitzungsende bleibt unbemerkt:** Nach Ablauf der Sitzung (10 Minuten) funktionieren Aktionen innerhalb der Seite (Add to cart, Sortieren) ohne Hinweis weiter. Erst beim Seitenwechsel landet der Kunde auf der Login-Seite (geprüft am 14.11.2026 mit echter Wartezeit von 10,5 Minuten). Folge aus B-2 und BUG-11. |
| B-15 | **Steuersatz nicht spezifiziert:** Die 8 % Steuer (CO-09) sind aus dem Verhalten der Seite abgeleitet (39,98 $ → 3,20 $). Ist die Seite von Anfang an falsch, bemerkt der Test das nicht. Bitte den gültigen Steuersatz bestätigen. |
| B-11 | **Text bei unbekanntem Produkt:** Die Seite „ITEM NOT FOUND“ zeigt den Text „your call could not be completed as dialled …“ (Telefon-Ansage) – für einen Webshop unpassend. |

## 7. Endekriterien und Testbericht

Die Endekriterien werden nach jedem Lauf automatisch im HTML-Bericht bewertet
(Abschnitt „Testabschluss-Übersicht“, Code: `utils/report_summary.py`).

| Ergebnis des Laufs | Bewertung im Bericht |
|---|---|
| Kein Test fehlgeschlagen; nur bekannte Fehler (XFAIL) | 🟢 Endekriterien erfüllt: keine neuen Fehler. Die offenen bekannten Fehler werden aufgelistet und müssen bei der Freigabe berücksichtigt werden. |
| Fehlschlag nur bei Priorität Mittel oder Niedrig | 🟠 Endekriterien nicht erfüllt: Freigabe nur nach Prüfung |
| Mindestens ein Fehlschlag mit Priorität Hoch | 🔴 Endekriterien nicht erfüllt: Freigabe nicht empfohlen |

Als Fehlschlag zählen auch Fehler im Testablauf (Setup/Teardown) und ein bekannter Fehler,
der plötzlich nicht mehr auftritt (XPASS). In diesem Fall wurde der Fehler vermutlich behoben
und der Test muss angepasst werden.

**Aufteilung des Testberichts (nach ISTQB):**

| Inhalt des Testabschlussberichts | Wo zu finden |
|---|---|
| Testobjekt, Testumgebung, Testauswahl | HTML-Bericht, Tabelle „Environment“ |
| Kennzahlen (ausgeführt, bestanden, fehlgeschlagen) | HTML-Bericht, Testabschluss-Übersicht |
| Bewertung und Freigabeempfehlung | HTML-Bericht, Testabschluss-Übersicht |
| Offene Fehler | HTML-Bericht und Abschnitt 5 |
| Restrisiken, offene Fragen | Abschnitt 6 |
| Nicht getestete Bereiche | Abschnitt 1 (außerhalb des Umfangs) |
