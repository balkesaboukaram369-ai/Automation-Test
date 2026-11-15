"""Tests für den Warenkorb."""

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL, PASSWORD
from data.test_data import PRODUCTS, PageTitles, Users
from pages import CartPage, CheckoutInfoPage, InventoryPage, LoginPage
from utils.flows import add_products
from utils.priority import HOCH, MITTEL, NIEDRIG

# Zwei Beispielprodukte für die Warenkorb-Tests
SELECTED = [PRODUCTS[0], PRODUCTS[1]]
SELECTED_NAMES = [p["name"] for p in SELECTED]


@pytest.fixture
def cart_with_products(inventory_page: InventoryPage) -> CartPage:
    """Zwei Produkte im Warenkorb, Warenkorb-Seite ist geöffnet."""
    add_products(inventory_page, SELECTED_NAMES)
    inventory_page.header.open_cart()
    return CartPage(inventory_page.page)


@MITTEL
def test_cart_01_empty_cart(inventory_page: InventoryPage):
    """CART-01: Ein leerer Warenkorb zeigt keine Produkte und kein Zähler-Symbol."""
    inventory_page.header.open_cart()

    cart = CartPage(inventory_page.page)
    expect(cart.title).to_have_text(PageTitles.CART)
    expect(cart.items).to_have_count(0)
    expect(cart.header.cart_badge).to_be_hidden()


@pytest.mark.smoke
@HOCH
def test_cart_02_shows_added_products(cart_with_products: CartPage):
    """CART-02: Der Warenkorb zeigt die hinzugefügten Produkte mit Preis und Menge 1."""
    assert cart_with_products.product_names() == SELECTED_NAMES
    assert cart_with_products.product_prices() == [p["price"] for p in SELECTED]
    expect(cart_with_products.item_quantities).to_have_text(["1", "1"])


@HOCH
def test_cart_03_remove_product_in_cart(cart_with_products: CartPage):
    """CART-03: 'Remove' im Warenkorb entfernt das Produkt und aktualisiert den Zähler."""
    cart_with_products.remove(SELECTED_NAMES[0])

    assert cart_with_products.product_names() == [SELECTED_NAMES[1]]
    expect(cart_with_products.header.cart_badge).to_have_text("1")


@MITTEL
def test_cart_04_continue_shopping(cart_with_products: CartPage):
    """CART-04: 'Continue Shopping' führt zurück zur Produktseite, der Warenkorb bleibt erhalten."""
    cart_with_products.continue_shopping()

    expect(cart_with_products.page).to_have_url(BASE_URL + "inventory.html")
    expect(cart_with_products.header.cart_badge).to_have_text("2")


@MITTEL
def test_cart_05_cart_survives_reload(cart_with_products: CartPage):
    """CART-05: Der Warenkorb bleibt nach dem Neuladen der Seite erhalten."""
    cart_with_products.page.reload()

    assert cart_with_products.product_names() == SELECTED_NAMES


@MITTEL
def test_cart_06_cart_survives_logout_and_login(cart_with_products: CartPage):
    """CART-06: Der Warenkorb bleibt nach Logout und erneutem Login erhalten."""
    cart_with_products.header.logout()
    LoginPage(cart_with_products.page).login(Users.STANDARD, PASSWORD)

    expect(cart_with_products.header.cart_badge).to_have_text("2")


@HOCH
def test_cart_07_checkout_button_opens_checkout(cart_with_products: CartPage):
    """CART-07: 'Checkout' öffnet die Seite mit den Kundendaten."""
    cart_with_products.checkout()

    info = CheckoutInfoPage(cart_with_products.page)
    expect(info.title).to_have_text(PageTitles.CHECKOUT_INFO)


@NIEDRIG
def test_cart_08_cart_shared_between_tabs(inventory_page: InventoryPage):
    """CART-08: Ein im ersten Tab hinzugefügtes Produkt erscheint nach dem Neuladen auch im zweiten Tab."""
    second_tab = InventoryPage(inventory_page.page.context.new_page()).open()

    inventory_page.add_to_cart(PRODUCTS[0]["name"])
    second_tab.page.reload()

    expect(second_tab.header.cart_badge).to_have_text("1")
