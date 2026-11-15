"""Tests für das Burger-Menü (☰)."""

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from config.settings import BASE_URL
from data.known_bugs import known_bug
from data.test_data import ABOUT_DOMAIN, PRODUCT_NAMES, PageTitles
from pages import CartPage, InventoryPage, LoginPage
from utils.priority import HOCH, MITTEL, NIEDRIG

MENU_ENTRIES = ["All Items", "Dynamic Catalog", "About", "Logout", "Reset App State"]


@MITTEL
def test_menu_01_open_menu_shows_all_entries(inventory_page: InventoryPage):
    """MENU-01: Das Menü öffnet sich und zeigt alle Einträge."""
    inventory_page.header.open_menu()

    expect(inventory_page.header.menu_links).to_have_text(MENU_ENTRIES)


@NIEDRIG
def test_menu_02_close_menu(inventory_page: InventoryPage):
    """MENU-02: Das X schließt das Menü wieder."""
    header = inventory_page.header
    header.open_menu()

    header.close_menu()

    expect(header.menu_panel).to_have_attribute("aria-hidden", "true")


@MITTEL
def test_menu_03_all_items_from_cart(inventory_page: InventoryPage):
    """MENU-03: 'All Items' führt von jeder Seite zur Produktübersicht."""
    inventory_page.header.open_cart()
    cart = CartPage(inventory_page.page)

    cart.header.go_to_all_items()

    expect(cart.page).to_have_url(BASE_URL + "inventory.html")


@NIEDRIG
@pytest.mark.external
def test_menu_04_about_opens_saucelabs(inventory_page: InventoryPage):
    """MENU-04: 'About' öffnet die Webseite von Sauce Labs."""
    inventory_page.header.open_about()

    inventory_page.page.wait_for_url(f"**{ABOUT_DOMAIN}/**", wait_until="domcontentloaded", timeout=30_000)


@HOCH
@pytest.mark.smoke
def test_menu_05_logout(inventory_page: InventoryPage):
    """MENU-05: 'Logout' meldet ab und zeigt die Login-Seite."""
    inventory_page.header.logout()

    expect(inventory_page.page).to_have_url(BASE_URL)
    expect(LoginPage(inventory_page.page).login_button).to_be_visible()


@MITTEL
def test_menu_06_reset_app_state_empties_cart(inventory_page: InventoryPage):
    """MENU-06: 'Reset App State' leert den Warenkorb."""
    inventory_page.add_to_cart(PRODUCT_NAMES[0])

    inventory_page.header.reset_app_state()

    expect(inventory_page.header.cart_badge).to_be_hidden()


@MITTEL
@known_bug("BUG-02")
def test_menu_07_reset_app_state_resets_buttons(inventory_page: InventoryPage):
    """MENU-07: Nach 'Reset App State' zeigen alle Produkte wieder 'Add to cart'."""
    inventory_page.add_to_cart(PRODUCT_NAMES[0])

    inventory_page.header.reset_app_state()

    expect(inventory_page.item_button(PRODUCT_NAMES[0])).to_have_text("Add to cart", timeout=3_000)


@NIEDRIG
@pytest.mark.parametrize(
    "entry, path",
    [
        ("Lazy Load", "dynamic-catalog-lazy-load.html"),
        ("Spinner", "dynamic-catalog-spinner.html"),
        ("Slider", "dynamic-catalog-slider.html"),
    ],
)
def test_menu_08_dynamic_catalog_entries(inventory_page: InventoryPage, entry, path):
    """MENU-08: 'Dynamic Catalog' klappt ein Untermenü auf, jeder Eintrag öffnet seine Seite."""
    header = inventory_page.header
    header.open_menu()
    inventory_page.page.get_by_test_id("dynamic-catalog-sidebar-link").click()

    inventory_page.page.get_by_text(entry, exact=True).click()

    expect(inventory_page.page).to_have_url(BASE_URL + path)
    expect(inventory_page.title).to_have_text(PageTitles.dynamic_catalog(entry))


@NIEDRIG
@known_bug("BUG-22")
def test_menu_09_click_outside_closes_menu(inventory_page: InventoryPage):
    """MENU-09: Ein Klick neben das geöffnete Menü schließt es (übliches Verhalten von Seitenmenüs)."""
    header = inventory_page.header
    header.open_menu()

    # Auf eine freie Stelle rechts unten auf der Seite klicken
    viewport = inventory_page.page.viewport_size
    inventory_page.page.mouse.click(viewport["width"] - 50, viewport["height"] - 50)

    expect(header.menu_panel).to_have_attribute("aria-hidden", "true", timeout=3_000)


@NIEDRIG
def test_menu_10_escape_closes_menu(inventory_page: InventoryPage):
    """MENU-10: Die Escape-Taste schließt das geöffnete Menü."""
    header = inventory_page.header
    header.open_menu()
    # Das Menü setzt den Tastatur-Fokus auf den ersten Eintrag, sobald es bereit ist
    expect(header.all_items_link).to_be_focused()

    inventory_page.page.keyboard.press("Escape")

    expect(header.menu_panel).to_have_attribute("aria-hidden", "true")


@MITTEL
@known_bug("BUG-23")
def test_menu_11_page_not_usable_while_menu_open(inventory_page: InventoryPage):
    """MENU-11: Bei geöffnetem Menü löst ein Klick auf die Seite dahinter keine Aktion aus.

    Risiko: Der Kunde legt versehentlich ein Produkt in den Warenkorb,
    obwohl er nur das Menü schließen wollte.
    """
    inventory_page.header.open_menu()

    try:
        # Produkt in der rechten Spalte, nicht vom Menü verdeckt
        inventory_page.item_button(PRODUCT_NAMES[1]).click(timeout=3_000)
    except PlaywrightTimeoutError:
        pass  # Klick wurde blockiert - das ist das erwartete Verhalten
    # Kurz warten: Ein "unsichtbar"-Check wäre sonst wahr, bevor die Seite reagiert hat
    inventory_page.page.wait_for_timeout(500)

    expect(inventory_page.header.cart_badge).to_be_hidden()
