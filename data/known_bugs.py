"""Verzeichnis aller gefundenen Fehler (Bugs).

Jeder Test, der einen bekannten Fehler nachweist, wird mit ``known_bug("BUG-xx")``
markiert. pytest erwartet dann, dass der Test fehlschlägt (Status XFAIL).

``strict=True`` bedeutet: Wird der Fehler eines Tages behoben und der Test besteht
plötzlich, meldet pytest das als Fehlschlag (XPASS(strict)). So fällt sofort auf,
dass die Markierung entfernt werden muss – der Bericht bleibt immer aktuell.

Die ausführlichen Fehlerberichte stehen in docs/Testplan.md.
"""

import pytest

BUGS = {
    "BUG-01": "performance_glitch_user: Jedes Anzeigen der Produktliste dauert ca. 5 Sekunden (Limit: 3 Sekunden)",
    "BUG-02": "Reset App State leert den Warenkorb, setzt aber die Buttons nicht auf 'Add to cart' zurück",
    "BUG-03": "Checkout ist mit leerem Warenkorb möglich, eine leere Bestellung über 0,00 $ wird komplett abgeschlossen",
    "BUG-04": "Checkout-Schritte können per direkter URL übersprungen werden",
    "BUG-05": "Doppelklick auf 'Finish' schließt die Bestellung zweimal ab",
    "BUG-06": "Nach Bestellabschluss kann über Browser-Zurück erneut 'Finish' geklickt werden",
    "BUG-07": "Keine Offline-Erkennung: Bei fehlender Internetverbindung erscheint kein Hinweis",
    "BUG-08": "Lazy Load: 'Test.allTheThings() T-Shirt (Red) (L)' wird doppelt angezeigt",
    "BUG-09": "Lazy Load: Die Produktliste wiederholt sich endlos und endet nie",
    "BUG-10": "Lange Fehlermeldungen auf der Login-Seite werden abgeschnitten",
    "BUG-11": "Nach Ablauf der Sitzung wird nicht verständlich gemeldet, dass die Sitzung abgelaufen ist",
    "BUG-12": "problem_user: Alle Produktbilder sind falsch (Platzhalterbild)",
    "BUG-13": "problem_user: Sortierung hat keine Wirkung",
    "BUG-14": "Nicht alle Produkte lassen sich in den Warenkorb legen",
    "BUG-15": "problem_user: Klick auf ein Produkt öffnet ein anderes Produkt",
    "BUG-16": "Feld 'Last Name' im Checkout übernimmt die Eingabe nicht korrekt",
    "BUG-17": "error_user: 'Finish' schließt die Bestellung nicht ab",
    "BUG-18": "visual_user: Produktpreise sind falsch und ändern sich zufällig",
    "BUG-19": "visual_user: Das Bild des Rucksacks ist falsch",
    "BUG-20": "error_user: Sortierung bricht mit Fehlermeldung ab",
    "BUG-21": "Doppelklick auf 'Continue' im Checkout wird zweimal verarbeitet",
    "BUG-22": "Menü schließt sich nicht bei Klick außerhalb des Menüs",
    "BUG-23": "Bei geöffnetem Menü bleibt die Seite dahinter bedienbar (kein Overlay)",
    "BUG-24": "Checkout akzeptiert Pflichtfelder, die nur Leerzeichen enthalten",
    "BUG-25": "Meldung 'You can only access …' erscheint nach Neuladen (F5) wieder, auch nach Klick auf X",
    "BUG-26": "Dieselbe Bestellung kann aus einem zweiten Tab ein zweites Mal abgeschlossen werden",
}


def known_bug(bug_id: str):
    """Markierung für einen Test, der einen bekannten Fehler nachweist."""
    return pytest.mark.xfail(strict=True, reason=f"{bug_id}: {BUGS[bug_id]}")


def expect_bug_except_in(request, browser_name: str, bug_id: str, unaffected_browsers: list[str]):
    """Markiert den laufenden Test als 'bekannter Fehler' - außer in den genannten Browsern.

    Manche Fehler treten nur in bestimmten Browsern auf. Beispiel: Der Doppelklick-Fehler
    ist in Chromium und WebKit reproduzierbar, in Firefox aber nicht.
    """
    if browser_name not in unaffected_browsers:
        request.applymarker(known_bug(bug_id))


def with_bug(value, bug_id: str):
    """Ein einzelner Parameter (z. B. ein Benutzer), bei dem ein bekannter Fehler erwartet wird."""
    return pytest.param(value, marks=known_bug(bug_id), id=f"{value}-{bug_id}")
