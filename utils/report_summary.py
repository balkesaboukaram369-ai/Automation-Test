"""Testabschluss-Übersicht für den HTML-Bericht (angelehnt an den ISTQB-Testabschlussbericht).

Die Hooks in conftest.py sammeln während des Testlaufs die Ergebnisse.
Diese Datei macht daraus am Ende den HTML-Block oben im Bericht:
Kennzahlen, Bewertung der Endekriterien, Ergebnis nach Priorität und offene bekannte Fehler.
"""

import re
from collections import Counter
from html import escape

from data.known_bugs import BUGS

PRIORITIES = ["Hoch", "Mittel", "Niedrig"]


def outcome_of(report) -> str | None:
    """Übersetzt eine pytest-Testphase in ein Ergebnis (passed, failed, xfailed, ...).

    Gibt None zurück, wenn die Phase nichts am Ergebnis ändert (z. B. ein erfolgreiches Setup).
    """
    known_bug = hasattr(report, "wasxfail")
    if report.when == "call":
        if report.passed:
            return "xpassed" if known_bug else "passed"
        if report.skipped:
            return "xfailed" if known_bug else "skipped"
        return "failed"
    # Setup oder Teardown
    if report.failed:
        return "error"  # Problem im Testablauf, nicht unbedingt in der Webseite
    if report.skipped:
        return "xfailed" if known_bug else "skipped"
    return None


def bug_id_of(report) -> str:
    """Liest die Fehler-ID (z. B. BUG-01) aus dem Grund eines bekannten Fehlers."""
    match = re.search(r"BUG-\d+", getattr(report, "wasxfail", "") or "")
    return match.group(0) if match else ""


def _release_decision(results: list[dict]) -> tuple[str, str, str]:
    """Bewertet die Endekriterien aus dem Testplan (Abschnitt 7) -> (CSS-Klasse, Titel, Text)."""
    problems = [r for r in results if r["outcome"] in ("failed", "error", "xpassed")]
    high = [r for r in problems if r["priority"] == "Hoch"]

    if high:
        return ("rot", "Endekriterien nicht erfüllt: Freigabe nicht empfohlen",
                f"{len(high)} Test(s) mit Priorität Hoch sind fehlgeschlagen. Bitte zuerst analysieren.")
    if problems:
        return ("orange", "Endekriterien nicht erfüllt: Freigabe nur nach Prüfung",
                f"{len(problems)} Test(s) mit Priorität Mittel/Niedrig sind fehlgeschlagen.")
    open_bugs = len({r["bug"] for r in results if r["outcome"] == "xfailed" and r["bug"]})
    return ("gruen", "Endekriterien erfüllt: keine neuen Fehler",
            f"Alle Tests verhalten sich wie erwartet. {open_bugs} bekannte(r) Fehler sind weiterhin offen "
            "und müssen bei der Freigabeentscheidung berücksichtigt werden.")


def build_summary_html(results: list[dict]) -> str:
    """Baut den HTML-Block „Testabschluss-Übersicht“ aus den gesammelten Ergebnissen."""
    if not results:
        return ""

    count = Counter(r["outcome"] for r in results)
    total = len(results)
    executed = total - count["skipped"]
    pass_rate = round(100 * count["passed"] / executed) if executed else 0

    # 1) Kennzahlen als Kacheln
    tiles = [
        ("Ausgeführt", executed, ""),
        ("Bestanden", count["passed"], "gruen"),
        ("Fehlgeschlagen", count["failed"] + count["error"] + count["xpassed"], "rot"),
        ("Bekannte Fehler (XFAIL)", count["xfailed"], "orange"),
        ("Übersprungen", count["skipped"], ""),
        ("Bestanden-Quote", f"{pass_rate} %", ""),
    ]
    tiles_html = "".join(
        f'<div class="kachel {css}"><div class="zahl">{value}</div><div>{label}</div></div>'
        for label, value, css in tiles
    )

    # 2) Bewertung der Endekriterien
    css, title, text = _release_decision(results)
    decision_html = f'<div class="bewertung {css}"><strong>{title}</strong><br>{text}</div>'

    # 3) Ergebnis nach Priorität
    rows = ""
    for prio in PRIORITIES:
        group = [r for r in results if r["priority"] == prio]
        if not group:
            continue
        c = Counter(r["outcome"] for r in group)
        failed = c["failed"] + c["error"] + c["xpassed"]
        rows += (f'<tr><td><span class="prio prio-{prio.lower()}">{prio}</span></td><td>{len(group)}</td>'
                 f'<td>{c["passed"]}</td><td class="{"rot" if failed else ""}">{failed}</td>'
                 f'<td>{c["xfailed"]}</td></tr>')
    prio_html = ("<h3>Ergebnis nach Priorität</h3><table class='uebersicht'>"
                 "<tr><th>Priorität</th><th>Tests</th><th>Bestanden</th><th>Fehlgeschlagen</th>"
                 f"<th>Bekannte Fehler</th></tr>{rows}</table>")

    # 4) Offene bekannte Fehler, die in diesem Lauf aufgetreten sind
    bug_counts = Counter(r["bug"] for r in results if r["outcome"] == "xfailed" and r["bug"])
    if bug_counts:
        bug_rows = "".join(
            f"<tr><td>{bug}</td><td>{escape(BUGS.get(bug, ''))}</td><td>{n}</td></tr>"
            for bug, n in sorted(bug_counts.items(), key=lambda item: int(item[0].split("-")[1]))
        )
        bugs_html = ("<h3>Offene bekannte Fehler</h3><table class='uebersicht'>"
                     "<tr><th>ID</th><th>Beschreibung</th><th>Betroffene Tests</th></tr>"
                     f"{bug_rows}</table>")
    else:
        bugs_html = ""

    note = ("<p class='hinweis'>Restrisiken, Beobachtungen und offene Fragen an den Kunden: "
            "siehe <code>docs/Testplan.md</code>, Abschnitt 5 bis 7.</p>")

    return (f'<div class="testabschluss"><h2>Testabschluss-Übersicht</h2>'
            f'<div class="kacheln">{tiles_html}</div>{decision_html}{prio_html}{bugs_html}{note}</div>')
