"""Kurze Namen für die Prioritäts-Markierungen aus dem Testplan.

Statt ``@pytest.mark.prio_hoch`` schreiben wir einfach ``@HOCH`` über einen Test.
Die Priorität steht danach im HTML-Bericht (Spalte "Priorität") und kann zur
Auswahl genutzt werden, z. B. ``pytest -m prio_hoch``.

Richtlinie (siehe docs/Testplan.md):
- HOCH:    Geld, Daten oder Sicherheit betroffen, oder Kernfunktion des Shops
- MITTEL:  Funktion beeinträchtigt, Kunde kann aber weiter einkaufen
- NIEDRIG: Darstellung, Komfort, Nebenfunktionen
"""

import pytest

HOCH = pytest.mark.prio_hoch
MITTEL = pytest.mark.prio_mittel
NIEDRIG = pytest.mark.prio_niedrig
