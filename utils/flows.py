"""Wiederverwendbare Abläufe (Flows), die in vielen Tests vorkommen.

Statt in jedem Test dieselben Schritte zu wiederholen (Login, Produkte hinzufügen,
Checkout ausfüllen ...), stehen sie hier einmal. Das vermeidet doppelten Code.
"""

from playwright.sync_api import Page, expect

from config.settings import PASSWORD
from data.test_data import CUSTOMER
from pages import CartPage, CheckoutInfoPage, CheckoutOverviewPage, InventoryPage, LoginPage


def login_as(page: Page, username: str) -> InventoryPage:
    """Meldet einen Benutzer an und wartet, bis die Produktseite geladen ist."""
    LoginPage(page).open().login(username, PASSWORD)
    inventory = InventoryPage(page)
    expect(inventory.inventory_list).to_be_visible()
    return inventory


def add_products(inventory: InventoryPage, product_names: list[str]) -> None:
    """Legt mehrere Produkte von der Produktseite aus in den Warenkorb."""
    for name in product_names:
        inventory.add_to_cart(name)


def go_to_overview(page: Page, product_names: list[str]) -> CheckoutOverviewPage:
    """Legt Produkte in den Warenkorb, füllt Checkout-Schritt 1 aus und öffnet die Übersicht.

    Voraussetzung: Der Benutzer ist bereits angemeldet und auf der Produktseite.
    """
    inventory = InventoryPage(page)
    add_products(inventory, product_names)
    inventory.header.open_cart()
    CartPage(page).checkout()
    info = CheckoutInfoPage(page)
    info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])
    info.continue_checkout()
    overview = CheckoutOverviewPage(page)
    expect(overview.finish_button).to_be_visible()
    return overview
