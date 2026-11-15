"""Tests gegen doppelte Ausführung (z. B. doppelte Bestellung / Doppelzahlung).

Die Demo-Seite hat kein echtes Bezahlsystem. Wir können daher nicht prüfen, ob
Geld doppelt abgebucht wird. Wir prüfen aber die Anzeichen im Browser:
Wie oft wird eine Aktion tatsächlich ausgeführt?

Messmethode: ``history.length`` zählt die Einträge im Browser-Verlauf.
Jede ausgeführte Weiterleitung erzeugt einen neuen Eintrag.

Ergebnis der Prüfung (07.11.2026): Der Doppelklick wird in Chromium und WebKit
zweimal verarbeitet, in Firefox nur einmal.
"""

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from data.known_bugs import expect_bug_except_in, known_bug
from data.test_data import CUSTOMER, PRODUCT_NAMES
from pages import CartPage, CheckoutCompletePage, CheckoutInfoPage, CheckoutOverviewPage, InventoryPage
from utils.flows import go_to_overview
from utils.priority import HOCH, NIEDRIG

CLICKS = [pytest.param(1, id="Einfachklick"), pytest.param(2, id="Doppelklick")]


def history_length(page) -> int:
    return page.evaluate("history.length")


@pytest.mark.parametrize("clicks", CLICKS)
@HOCH
def test_dbl_01_finish_is_processed_only_once(inventory_page: InventoryPage, clicks, request, browser_name):
    """DBL-01: Auch bei Doppelklick auf 'Finish' wird die Bestellung nur EINMAL abgeschlossen."""
    if clicks == 2:
        expect_bug_except_in(request, browser_name, "BUG-05", unaffected_browsers=["firefox"])
    overview = go_to_overview(inventory_page.page, [PRODUCT_NAMES[0]])
    before = history_length(inventory_page.page)

    overview.finish_button.click(click_count=clicks)
    expect(CheckoutCompletePage(inventory_page.page).complete_header).to_be_visible()
    inventory_page.page.wait_for_timeout(500)  # kurz warten, falls ein zweiter Abschluss folgt

    assert history_length(inventory_page.page) - before == 1, "Bestellung wurde mehrfach abgeschlossen"

  
@known_bug("BUG-06")
@HOCH
def test_dbl_02_no_second_order_via_back_button(inventory_page: InventoryPage):
    """DBL-02: Nach Bestellabschluss führt Browser-Zurück nicht zu einem erneut klickbaren 'Finish'."""
    overview = go_to_overview(inventory_page.page, [PRODUCT_NAMES[0]])
    overview.finish()
    expect(CheckoutCompletePage(inventory_page.page).complete_header).to_be_visible()

    inventory_page.page.go_back()
    expect(inventory_page.title).to_be_visible()  # warten, bis die vorherige Seite angezeigt wird

    expect(CheckoutOverviewPage(inventory_page.page).finish_button).to_be_hidden(timeout=3_000)


@pytest.mark.parametrize("clicks", CLICKS)
@NIEDRIG
def test_dbl_03_continue_is_processed_only_once(inventory_page: InventoryPage, clicks, request, browser_name):
    """DBL-03: Auch bei Doppelklick auf 'Continue' wird Schritt 1 nur einmal verlassen."""
    if clicks == 2:
        expect_bug_except_in(request, browser_name, "BUG-21", unaffected_browsers=["firefox"])
    inventory_page.add_to_cart(PRODUCT_NAMES[0])
    inventory_page.header.open_cart()
    CartPage(inventory_page.page).checkout()
    info = CheckoutInfoPage(inventory_page.page)
    info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])
    before = history_length(inventory_page.page)

    info.continue_button.click(click_count=clicks)
    expect(inventory_page.page).to_have_url(BASE_URL + "checkout-step-two.html")
    inventory_page.page.wait_for_timeout(500)

    assert history_length(inventory_page.page) - before == 1, "Schritt wurde mehrfach verarbeitet"


@known_bug("BUG-26")
@HOCH
def test_dbl_04_no_second_order_from_second_tab(inventory_page: InventoryPage):
    """DBL-04: Dieselbe Bestellung lässt sich aus einem zweiten Tab nicht ein zweites Mal abschließen.

    Ablauf: Beide Tabs zeigen die Übersicht. Tab 1 schließt ab, danach klickt Tab 2
    (ohne Neuladen) ebenfalls auf 'Finish'. Geprüft am 14.11.2026 in Chromium, Firefox
    und WebKit: Tab 2 zeigt erneut 'Thank you for your order!', obwohl der Warenkorb
    nach der ersten Bestellung leer ist.
    """
    tab1 = inventory_page.page
    go_to_overview(tab1, [PRODUCT_NAMES[0], PRODUCT_NAMES[1]])
    tab2 = tab1.context.new_page()
    tab2.goto(BASE_URL + "checkout-step-two.html")
    expect(CheckoutOverviewPage(tab2).finish_button).to_be_visible()

    CheckoutOverviewPage(tab1).finish()
    expect(CheckoutCompletePage(tab1).complete_header).to_be_visible()
    CheckoutOverviewPage(tab2).finish()
    # Kurz warten: Ein "unsichtbar"-Check wäre sonst wahr, bevor Tab 2 reagiert hat
    tab2.wait_for_timeout(1_000)

    expect(CheckoutCompletePage(tab2).complete_header).to_be_hidden()
