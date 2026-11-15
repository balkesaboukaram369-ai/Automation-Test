"""Antwortzeiten der Produktliste (nicht-funktionaler Test).

Messung am 08.11.2026: Beim performance_glitch_user dauert JEDES Anzeigen der
Produktliste ca. 5 Sekunden - nicht nur der Login (siehe LOGIN-09), sondern auch
Sortieren, Zurück von der Detailseite und 'Back Home' nach der Bestellung.
Alle anderen Aktionen (Warenkorb, Checkout ...) sind normal schnell.

Zeitlimit: dieselbe Annahme wie beim Login (3 Sekunden, siehe config/settings.py).
standard_user dient als Referenz und muss das Limit immer einhalten.
"""

import time

import pytest
from playwright.sync_api import expect

from config.settings import LOGIN_TIME_LIMIT_SECONDS as LIMIT
from data.known_bugs import known_bug
from data.test_data import PRODUCT_NAMES, Users
from pages import CheckoutCompletePage, ProductPage
from utils.flows import go_to_overview, login_as
from utils.priority import MITTEL

USERS = [
    pytest.param(Users.STANDARD, id=Users.STANDARD),
    pytest.param(Users.PERFORMANCE_GLITCH, id="performance_glitch_user-BUG-01", marks=known_bug("BUG-01")),
]

pytestmark = MITTEL  # alle Tests dieser Datei haben die Priorität Mittel


def measure(action, wait_until_done) -> float:
    """Führt eine Aktion aus und misst die Zeit, bis `wait_until_done` erfüllt ist."""
    start = time.perf_counter()
    action()
    wait_until_done()
    return time.perf_counter() - start


@pytest.mark.parametrize("username", USERS)
def test_perf_01_sorting_within_limit(page, username):
    """PERF-01: Nach dem Sortieren ist die Produktliste innerhalb des Zeitlimits neu aufgebaut."""
    inventory = login_as(page, username)
    expected_first = sorted(PRODUCT_NAMES, reverse=True)[0]

    duration = measure(
        lambda: inventory.sort_by("za"),
        # fertig, sobald das erste Produkt das richtige ist
        lambda: expect(inventory.item_names.first).to_have_text(expected_first, timeout=15_000),
    )

    assert duration <= LIMIT, f"Sortieren dauerte {duration:.2f} s (Limit: {LIMIT} s)"


@pytest.mark.parametrize("username", USERS)
def test_perf_02_back_to_products_within_limit(page, username):
    """PERF-02: 'Back to products' zeigt die Produktliste innerhalb des Zeitlimits an."""
    inventory = login_as(page, username)
    inventory.open_product(PRODUCT_NAMES[0])
    details = ProductPage(page)

    duration = measure(
        details.back_button.click,
        lambda: expect(inventory.inventory_list).to_be_visible(timeout=15_000),
    )

    assert duration <= LIMIT, f"Zurück zur Liste dauerte {duration:.2f} s (Limit: {LIMIT} s)"


@pytest.mark.parametrize("username", USERS)
def test_perf_03_back_home_after_order_within_limit(page, username):
    """PERF-03: 'Back Home' nach der Bestellung zeigt die Produktliste innerhalb des Zeitlimits an."""
    inventory = login_as(page, username)
    overview = go_to_overview(page, [PRODUCT_NAMES[0]])
    overview.finish()
    complete = CheckoutCompletePage(page)
    expect(complete.complete_header).to_be_visible()

    duration = measure(
        complete.back_home_button.click,
        lambda: expect(inventory.inventory_list).to_be_visible(timeout=15_000),
    )

    assert duration <= LIMIT, f"Back Home dauerte {duration:.2f} s (Limit: {LIMIT} s)"
