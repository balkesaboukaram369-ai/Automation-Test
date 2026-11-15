"""Grundlegende Prüfungen der Barrierefreiheit (Accessibility).

Kein vollständiger Barrierefreiheits-Test (dafür eignen sich Werkzeuge wie axe-core),
sondern einige wichtige Punkte:
- Bilder haben einen beschreibenden Alternativtext (für Screenreader)
- Der Login ist komplett mit der Tastatur bedienbar
- Das Menü lässt sich mit der Tastatur öffnen
"""

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL, PASSWORD
from data.test_data import PRODUCTS, Users
from pages import InventoryPage, LoginPage
from utils.priority import MITTEL, NIEDRIG

pytestmark = pytest.mark.accessibility


@NIEDRIG
def test_a11y_01_product_images_have_alt_text(inventory_page: InventoryPage):
    """A11Y-01: Jedes Produktbild hat den Produktnamen als Alternativtext."""
    for product in PRODUCTS:
        image = inventory_page.item(product["name"]).locator("img")
        expect(image).to_have_attribute("alt", product["name"])


@MITTEL
def test_a11y_02_login_with_keyboard_only(login_page: LoginPage):
    """A11Y-02: Der Login ist nur mit der Tastatur möglich (Tab, Eingabe, Enter)."""
    page = login_page.page
    # Startpunkt: frisch geladene Seite, nichts ist ausgewählt (kein Mausklick -
    # Firefox würde sonst ab der Klickposition weiter-tabben).
    # WebKit braucht am Seitenanfang 1-2 zusätzliche Tab-Drücke (Verhalten des Browsers,
    # kein Fehler der Seite). Deshalb: Tab drücken, bis das Benutzerfeld den Fokus hat.
    for _ in range(5):
        page.keyboard.press("Tab")
        if login_page.username_input.evaluate("el => el === document.activeElement"):
            break
    expect(login_page.username_input).to_be_focused()
    page.keyboard.type(Users.STANDARD)
    page.keyboard.press("Tab")
    expect(login_page.password_input).to_be_focused()
    page.keyboard.type(PASSWORD)
    page.keyboard.press("Enter")

    expect(page).to_have_url(BASE_URL + "inventory.html")


@NIEDRIG
def test_a11y_03_menu_opens_with_keyboard(inventory_page: InventoryPage):
    """A11Y-03: Das Menü lässt sich mit der Tastatur öffnen (Fokus auf Menü-Button + Enter)."""
    header = inventory_page.header
    header.menu_button.focus()

    inventory_page.page.keyboard.press("Enter")

    expect(header.menu_panel).to_have_attribute("aria-hidden", "false")
    expect(header.logout_link).to_be_visible()
