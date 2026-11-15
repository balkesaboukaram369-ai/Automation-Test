"""Globale pytest-Konfiguration: Browser-Auswahl, HTML-Bericht und Screenshots.

Die Fixtures für die Tests selbst liegen in tests/conftest.py.
"""

import base64
import re
import warnings
from importlib.metadata import version

import pytest

from config.settings import BASE_URL, PASSWORD, SCREENSHOTS_DIR
from utils.report_summary import bug_id_of, build_summary_html, outcome_of

ALL_BROWSERS = ["chromium", "firefox", "webkit"]


def pytest_configure(config):
    # Ohne --browser-Angabe in allen drei Browsern testen.
    # Mit z. B. "pytest --browser firefox" läuft nur der gewählte Browser.
    if not config.option.browser:
        config.option.browser = list(ALL_BROWSERS)

    # Ohne Passwort ist kein Login möglich -> mit klarer Meldung abbrechen.
    if not PASSWORD and not config.option.collectonly:
        pytest.exit(
            "SAUCE_PASSWORD ist nicht gesetzt. Bitte .env.example nach .env kopieren "
            "und das Passwort eintragen (siehe README).",
            returncode=2,
        )

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# --- HTML-Bericht -----------------------------------------------------------

def pytest_html_report_title(report):
    report.title = "SauceDemo – Regressionstest-Bericht"


def pytest_metadata(metadata, config):
    """Tabelle "Environment" im Bericht: Was wurde wo und womit getestet (ISTQB: Testobjekt, Testumgebung)."""
    metadata.pop("Packages", None)
    metadata.pop("Plugins", None)
    metadata["Testobjekt"] = BASE_URL
    metadata["Browser"] = ", ".join(config.option.browser or ALL_BROWSERS)
    metadata["Playwright"] = version("playwright")
    metadata["pytest"] = version("pytest")

    selection = " ".join(config.args)
    if config.option.keyword:
        selection += f' -k "{config.option.keyword}"'
    if config.option.markexpr:
        selection += f' -m "{config.option.markexpr}"'
    metadata["Testauswahl"] = selection or "alle Tests"


PRIORITY_MARKERS = {"prio_hoch": "Hoch", "prio_mittel": "Mittel", "prio_niedrig": "Niedrig"}


def get_priority(item) -> str:
    """Liest die Priorität (Hoch/Mittel/Niedrig) aus den Markierungen eines Tests."""
    for marker in item.iter_markers():
        if marker.name in PRIORITY_MARKERS:
            return PRIORITY_MARKERS[marker.name]
    return ""


def pytest_collection_modifyitems(config, items):
    """Prüft nach dem Einsammeln, dass jeder Test genau eine Priorität hat (wie im Testplan)."""
    for item in items:
        if not get_priority(item):
            warnings.warn(pytest.PytestWarning(
                f"Test ohne Priorität (prio_hoch/prio_mittel/prio_niedrig): {item.nodeid}"
            ))


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Priorität</th>")
    cells.insert(3, "<th>Beschreibung</th>")
    cells.insert(4, "<th>Bekannter Fehler</th>")


def pytest_html_results_table_row(report, cells):
    priority = getattr(report, "priority", "")
    cells.insert(2, f'<td><span class="prio prio-{priority.lower()}">{priority}</span></td>')
    cells.insert(3, f"<td>{getattr(report, 'description', '')}</td>")
    cells.insert(4, f"<td>{bug_id_of(report)}</td>")


# Ergebnisse aller Tests für die Testabschluss-Übersicht: {Test-ID: {...}}
RESULTS: dict[str, dict] = {}


def pytest_runtest_logreport(report):
    """Merkt sich nach jeder Testphase das Ergebnis (funktioniert auch mit -n 4)."""
    outcome = outcome_of(report)
    if outcome is None:
        return
    # Ein Fehler im Teardown ändert ein "bestanden" nachträglich in "error"
    if report.when == "teardown" and report.nodeid in RESULTS and RESULTS[report.nodeid]["outcome"] != "passed":
        return
    RESULTS[report.nodeid] = {
        "outcome": outcome,
        "priority": getattr(report, "priority", ""),
        "bug": bug_id_of(report),
    }


def pytest_html_results_summary(prefix, summary, postfix, session):
    """Fügt oben im Bericht die Testabschluss-Übersicht ein."""
    prefix.append(build_summary_html(list(RESULTS.values())))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Wird nach jeder Testphase aufgerufen (setup / call / teardown).

    - Übernimmt die Priorität und die erste Zeile des Docstrings ("Beschreibung") in den Bericht.
    - Bei einem Fehlschlag: Screenshot speichern und in den HTML-Bericht einbetten.
    """
    outcome = yield
    report = outcome.get_result()

    report.priority = get_priority(item)

    doc = item.function.__doc__ or ""
    report.description = doc.strip().splitlines()[0] if doc.strip() else ""

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("mobile_page")
        if page is None or page.is_closed():
            return
        try:
            png = page.screenshot(full_page=True)
        except Exception:  # Screenshot ist nur eine Hilfe - nie den Testlauf abbrechen
            return

        file_name = re.sub(r"[^\w.-]", "_", item.nodeid) + ".png"
        (SCREENSHOTS_DIR / file_name).write_bytes(png)

        pytest_html = item.config.pluginmanager.getplugin("html")
        if pytest_html is not None:
            extras = getattr(report, "extras", [])
            extras.append(pytest_html.extras.png(base64.b64encode(png).decode(), "Screenshot"))
            extras.append(pytest_html.extras.url(page.url, "URL beim Fehlschlag"))
            report.extras = extras
