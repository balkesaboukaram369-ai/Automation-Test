"""Zentrale Konfiguration der Test-Suite.

Alle Werte, die sich je nach Umgebung ändern können, werden hier gesammelt.
Sensible Werte (z. B. das Passwort) kommen aus Umgebungsvariablen bzw. aus
der lokalen Datei ``.env`` und werden NICHT ins Repository eingecheckt.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Projekt-Hauptordner (eine Ebene über diesem config-Ordner)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Lädt Variablen aus .env (falls vorhanden) in os.environ
load_dotenv(PROJECT_ROOT / ".env")

# Adresse der Anwendung unter Test
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/")

# Gemeinsames Passwort aller Demo-Benutzer (kommt aus .env)
PASSWORD = os.getenv("SAUCE_PASSWORD", "")

# Annahme (mit dem Team abgestimmt): Ein Login gilt als "schnell genug",
# wenn die Produktseite spätestens nach 3 Sekunden sichtbar ist.
LOGIN_TIME_LIMIT_SECONDS = float(os.getenv("LOGIN_TIME_LIMIT_SECONDS", "3"))

# Ordner für Berichte und Screenshots
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
