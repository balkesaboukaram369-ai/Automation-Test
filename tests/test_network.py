"""Tests bei fehlender oder langsamer Internetverbindung.

Offline (OFF):
    Die Webseite wird zuerst normal (online) geöffnet. Danach wird die Verbindung
    mit ``context.set_offline(True)`` getrennt - so wie bei einem Kunden, dessen
    Internet beim Einkaufen plötzlich ausfällt.
    Festgelegte Erwartung (Annahme, mit dem Team abgestimmt): Jede Aktion ohne
    Verbindung wird gestoppt und der Benutzer sieht einen klaren Offline-Hinweis.
    Die Anwendung zeigt keinen solchen Hinweis -> alle Fälle gehören zu BUG-07.
    Hinweis (geprüft am 14.11.2026): Die Offline-Seite des Browsers erscheint nur,
    wenn eine Seite neu geladen wird (z. B. F5). Aktionen innerhalb der Seite
    (Add to cart, Produkt öffnen, Zurück, Finish) laufen ohne Meldung weiter, weil
    die Seite eine Single-Page-App ist. Deshalb muss die Anwendung selbst warnen.

Langsam (SLOW):
    Alle Produktbilder werden "festgehalten" und erst am Testende ausgeliefert.
    Das simuliert einen sehr langsamen Bildserver. Erwartung: Die Seite bleibt
    trotzdem bedienbar.
"""

import re

import pytest
from playwright.sync_api import expect

from config.settings import PASSWORD
from data.known_bugs import known_bug
from data.test_data import PRODUCT_NAMES, Users
from pages import CheckoutCompletePage, InventoryPage, LoginPage, ProductPage
from pages.dynamic_catalog_page import LazyLoadPage
from utils.flows import go_to_overview, login_as
from utils.priority import HOCH, MITTEL, NIEDRIG

OFFLINE_HINT = re.compile(r"offline|no internet|no connection|keine verbindung", re.IGNORECASE)


def go_offline(page):
    page.context.set_offline(True)


def expect_offline_hint(page):
    """Erwartung: Ein sichtbarer Hinweis, dass keine Internetverbindung besteht."""
    expect(page.get_by_text(OFFLINE_HINT).first).to_be_visible(timeout=3_000)


# --- Offline -----------------------------------------------------------------

@known_bug("BUG-07")
@HOCH
def test_off_01_login_offline(login_page: LoginPage):
    """OFF-01: Login ohne Verbindung zeigt einen Offline-Hinweis."""
    go_offline(login_page.page)

    login_page.login(Users.STANDARD, PASSWORD)

    expect_offline_hint(login_page.page)


@known_bug("BUG-07")
@NIEDRIG
def test_off_02_sort_offline(inventory_page: InventoryPage):
    """OFF-02: Sortieren ohne Verbindung zeigt einen Offline-Hinweis."""
    go_offline(inventory_page.page)

    inventory_page.sort_by("za")

    expect_offline_hint(inventory_page.page)


@known_bug("BUG-07")
@MITTEL
def test_off_03_add_to_cart_offline(inventory_page: InventoryPage):
    """OFF-03: 'Add to cart' ohne Verbindung zeigt einen Offline-Hinweis."""
    go_offline(inventory_page.page)

    inventory_page.add_to_cart(PRODUCT_NAMES[0])

    expect_offline_hint(inventory_page.page)


@known_bug("BUG-07")
@NIEDRIG
def test_off_04_product_details_offline(inventory_page: InventoryPage):
    """OFF-04: Öffnen eines Produkts ohne Verbindung zeigt einen Offline-Hinweis."""
    go_offline(inventory_page.page)

    inventory_page.open_product(PRODUCT_NAMES[0])

    expect_offline_hint(inventory_page.page)


@known_bug("BUG-07")
@HOCH
def test_off_05_finish_order_offline(inventory_page: InventoryPage):
    """OFF-05: 'Finish' ohne Verbindung schließt die Bestellung NICHT ab und zeigt einen Hinweis."""
    overview = go_to_overview(inventory_page.page, [PRODUCT_NAMES[0]])
    go_offline(inventory_page.page)

    overview.finish()

    expect(CheckoutCompletePage(inventory_page.page).complete_header).to_be_hidden(timeout=3_000)
    expect_offline_hint(inventory_page.page)


@known_bug("BUG-07")
@MITTEL
def test_off_06_pdf_download_offline(inventory_page: InventoryPage):
    """OFF-06: 'Generate PDF order' ohne Verbindung zeigt einen Hinweis."""
    overview = go_to_overview(inventory_page.page, [PRODUCT_NAMES[0]])
    overview.finish()
    go_offline(inventory_page.page)

    CheckoutCompletePage(inventory_page.page).generate_pdf_button.click()

    expect_offline_hint(inventory_page.page)


@HOCH
def test_off_07_app_recovers_after_reconnect(inventory_page: InventoryPage):
    """OFF-07: Nach Rückkehr der Verbindung funktioniert die Seite wieder, der Warenkorb ist erhalten."""
    inventory_page.add_to_cart(PRODUCT_NAMES[0])
    go_offline(inventory_page.page)
    inventory_page.page.context.set_offline(False)

    inventory_page.page.reload()

    expect(inventory_page.inventory_list).to_be_visible()
    expect(inventory_page.header.cart_badge).to_have_text("1")


@known_bug("BUG-07")
@NIEDRIG
def test_off_08_logout_offline(inventory_page: InventoryPage):
    """OFF-08: Logout ohne Verbindung zeigt einen Offline-Hinweis."""
    go_offline(inventory_page.page)

    inventory_page.header.logout()

    expect_offline_hint(inventory_page.page)


# --- Langsame Verbindung -----------------------------------------------------

@pytest.fixture
def slow_images(page):
    """Hält alle Bild-Anfragen fest, bis der Test vorbei ist (sehr langsamer Bildserver)."""
    held_requests = []
    page.route("**/*.{jpg,jpeg,png,svg}", lambda route: held_requests.append(route))
    yield held_requests
    for route in held_requests:  # am Ende alle Bilder freigeben
        try:
            route.continue_()
        except Exception:
            pass


@MITTEL
def test_slow_01_login_and_products_without_images(page, slow_images):
    """SLOW-01: Login und Produktliste funktionieren, auch wenn die Bilder noch laden."""
    inventory = login_as(page, Users.STANDARD)

    assert slow_images, "Die Simulation hat keine Bild-Anfrage abgefangen"
    expect(inventory.item_names).to_have_count(len(PRODUCT_NAMES))
    expect(inventory.item_prices.first).to_be_visible()


@MITTEL
def test_slow_02_add_to_cart_while_images_load(page, slow_images):
    """SLOW-02: 'Add to cart' funktioniert, während die Bilder noch laden."""
    inventory = login_as(page, Users.STANDARD)

    inventory.add_to_cart(PRODUCT_NAMES[0])

    expect(inventory.header.cart_badge).to_have_text("1")


@MITTEL
def test_slow_03_product_details_while_images_load(page, slow_images):
    """SLOW-03: Die Detailseite öffnet sich und 'Add to cart' funktioniert ohne geladenes Bild."""
    inventory = login_as(page, Users.STANDARD)
    inventory.open_product(PRODUCT_NAMES[0])
    details = ProductPage(page)

    details.add_to_cart()

    expect(details.name).to_have_text(PRODUCT_NAMES[0])
    expect(details.header.cart_badge).to_have_text("1")


@MITTEL
def test_slow_04_complete_order_while_images_load(page, slow_images):
    """SLOW-04: Der komplette Kauf funktioniert, auch wenn die Bilder nicht geladen sind."""
    login_as(page, Users.STANDARD)
    overview = go_to_overview(page, [PRODUCT_NAMES[0]])

    overview.finish()

    expect(CheckoutCompletePage(page).complete_header).to_be_visible()


@MITTEL
def test_slow_05_lazy_load_while_images_load(page, slow_images):
    """SLOW-05: Lazy Load lädt beim Scrollen weitere Produkte, auch ohne geladene Bilder."""
    login_as(page, Users.STANDARD)
    lazy = LazyLoadPage(page).open(wait_until="domcontentloaded")
    expect(lazy.item_names).to_have_count(8)

    lazy.scroll_to_end()

    expect(lazy.item_names).not_to_have_count(8)
