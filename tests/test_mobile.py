"""Kernabläufe auf emulierten Mobilgeräten (iPhone 15, Pixel 7, iPad).

Hinweis: Playwright emuliert Bildschirmgröße, Touch und User-Agent. Für Safari
wird WebKit verwendet - die Engine von Safari, aber nicht das echte Safari.

Die Fixture ``mobile_page`` (tests/conftest.py) läuft automatisch einmal pro Gerät.
"""

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from data.test_data import PRODUCT_NAMES, PRODUCTS, Users
from pages import CheckoutCompletePage, LoginPage
from utils.flows import go_to_overview, login_as
from utils.priority import HOCH, MITTEL

pytestmark = pytest.mark.mobile  # alle Tests dieser Datei tragen die Markierung "mobile"


@HOCH
def test_mob_01_login_and_layout(mobile_page):
    """MOB-01: Login funktioniert, alle Produkte sind sichtbar, kein horizontales Scrollen."""
    inventory = login_as(mobile_page, Users.STANDARD)

    expect(inventory.items).to_have_count(len(PRODUCTS))
    overflow = mobile_page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"Seite ist {overflow}px breiter als der Bildschirm"


@MITTEL
def test_mob_02_menu_and_logout(mobile_page):
    """MOB-02: Das Menü lässt sich öffnen und der Logout funktioniert."""
    inventory = login_as(mobile_page, Users.STANDARD)

    inventory.header.logout()

    expect(mobile_page).to_have_url(BASE_URL)
    expect(LoginPage(mobile_page).login_button).to_be_visible()


@HOCH
def test_mob_03_complete_purchase(mobile_page):
    """MOB-03: Kompletter Kauf inkl. Warenkorb-Zähler auf dem Mobilgerät."""
    inventory = login_as(mobile_page, Users.STANDARD)
    inventory.add_to_cart(PRODUCT_NAMES[0])
    expect(inventory.header.cart_badge).to_have_text("1")
    inventory.remove_from_cart(PRODUCT_NAMES[0])  # go_to_overview legt das Produkt selbst hinein

    overview = go_to_overview(mobile_page, [PRODUCT_NAMES[0]])
    overview.finish()

    expect(CheckoutCompletePage(mobile_page).complete_header).to_be_visible()
