"""Tests für die Produkt-Detailseite."""

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from data.test_data import PRODUCT_NAMES, PRODUCTS
from pages import InventoryPage, ProductPage
from utils.priority import HOCH, MITTEL, NIEDRIG


@pytest.mark.parametrize("product", PRODUCTS, ids=[p["name"] for p in PRODUCTS])
@HOCH
def test_pd_01_details_match_product_list(inventory_page: InventoryPage, product):
    """PD-01: Die Detailseite zeigt denselben Namen, Preis und dieselbe Beschreibung wie die Liste."""
    inventory_page.open_product(product["name"])

    details = ProductPage(inventory_page.page)
    expect(details.name).to_have_text(product["name"])
    expect(details.price).to_have_text(f"${product['price']}")
    expect(details.description).to_have_text(product["description"])


@NIEDRIG
def test_pd_02_open_details_via_image(inventory_page: InventoryPage):
    """PD-02: Ein Klick auf das Produktbild öffnet die Detailseite."""
    inventory_page.open_product_by_image(PRODUCT_NAMES[0])

    expect(ProductPage(inventory_page.page).name).to_have_text(PRODUCT_NAMES[0])


@HOCH
def test_pd_03_add_to_cart_from_details(inventory_page: InventoryPage):
    """PD-03: 'Add to cart' auf der Detailseite legt das Produkt in den Warenkorb."""
    inventory_page.open_product(PRODUCT_NAMES[0])
    details = ProductPage(inventory_page.page)

    details.add_to_cart()

    expect(details.header.cart_badge).to_have_text("1")
    expect(details.remove_button).to_be_visible()


@MITTEL
def test_pd_04_remove_from_details(inventory_page: InventoryPage):
    """PD-04: 'Remove' auf der Detailseite entfernt das Produkt aus dem Warenkorb."""
    inventory_page.open_product(PRODUCT_NAMES[0])
    details = ProductPage(inventory_page.page)
    details.add_to_cart()

    details.remove_from_cart()

    expect(details.header.cart_badge).to_be_hidden()
    expect(details.add_to_cart_button).to_be_visible()


@MITTEL
def test_pd_05_back_to_products(inventory_page: InventoryPage):
    """PD-05: 'Back to products' führt zurück zur Produktliste."""
    inventory_page.open_product(PRODUCT_NAMES[0])

    ProductPage(inventory_page.page).back_to_products()

    expect(inventory_page.page).to_have_url(BASE_URL + "inventory.html")
    expect(inventory_page.items).to_have_count(len(PRODUCTS))


@MITTEL
def test_pd_06_state_is_shared_with_product_list(inventory_page: InventoryPage):
    """PD-06: Ein auf der Detailseite hinzugefügtes Produkt zeigt auch in der Liste 'Remove'."""
    inventory_page.open_product(PRODUCT_NAMES[0])
    details = ProductPage(inventory_page.page)
    details.add_to_cart()

    details.back_to_products()

    expect(inventory_page.item_button(PRODUCT_NAMES[0])).to_have_text("Remove")


@NIEDRIG
@pytest.mark.parametrize("product_id", ["99", "-1", "abc"])
def test_pd_07_unknown_product_id(inventory_page: InventoryPage, product_id):
    """PD-07: Eine ungültige Produkt-ID in der URL zeigt 'ITEM NOT FOUND' statt eines Absturzes."""
    inventory_page.page.goto(f"{BASE_URL}inventory-item.html?id={product_id}")

    details = ProductPage(inventory_page.page)
    expect(details.name).to_have_text("ITEM NOT FOUND")
    details.back_to_products()  # der Weg zurück funktioniert
