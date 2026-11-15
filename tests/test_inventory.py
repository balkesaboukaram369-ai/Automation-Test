"""Tests für die Produktübersicht und die Sortierung."""

import pytest
from playwright.sync_api import expect

from data.test_data import PRODUCT_NAMES, PRODUCTS, SORT_OPTIONS
from pages import InventoryPage
from utils.priority import HOCH, MITTEL, NIEDRIG


@pytest.mark.smoke
@HOCH
def test_inv_01_all_products_with_correct_data(inventory_page: InventoryPage):
    """INV-01: Alle 6 Produkte werden mit korrektem Namen, Preis und Beschreibung angezeigt."""
    expect(inventory_page.items).to_have_count(len(PRODUCTS))

    for product in PRODUCTS:
        item = inventory_page.item(product["name"])
        expect(item.get_by_test_id("inventory-item-price")).to_have_text(f"${product['price']}")
        expect(item.get_by_test_id("inventory-item-desc")).to_have_text(product["description"])


@MITTEL
def test_inv_02_product_images_are_correct(inventory_page: InventoryPage):
    """INV-02: Jedes Produkt zeigt sein eigenes Bild."""
    for product in PRODUCTS:
        image = inventory_page.item(product["name"]).locator("img")
        assert product["image"] in image.get_attribute("src"), f"Falsches Bild bei {product['name']}"


@MITTEL
def test_inv_03_default_sort_is_name_a_to_z(inventory_page: InventoryPage):
    """INV-03: Standard-Sortierung ist 'Name (A to Z)'."""
    expect(inventory_page.active_sort).to_have_text(SORT_OPTIONS["az"])

    # Geprüft wird die Regel ("alphabetisch sortiert"), nicht eine feste Liste:
    # So bleibt der Test gültig, wenn ein neues Produkt dazukommt.
    names = inventory_page.product_names()
    assert names == sorted(names)
    assert len(names) == len(PRODUCTS)


@pytest.mark.parametrize("option, reverse", [("az", False), ("za", True)], ids=["INV-04_A-Z", "INV-05_Z-A"])
@MITTEL
def test_inv_sort_by_name(inventory_page: InventoryPage, option, reverse):
    """INV-04/05: Sortierung nach Name (A-Z und Z-A).

    Wie bei den Preisen wird die Regel geprüft, nicht eine feste Liste von Namen.
    """
    inventory_page.sort_by(option)

    expect(inventory_page.active_sort).to_have_text(SORT_OPTIONS[option])
    names = inventory_page.product_names()
    assert names == sorted(names, reverse=reverse)
    assert len(names) == len(PRODUCTS)


@pytest.mark.parametrize(
    "option, reverse", [("lohi", False), ("hilo", True)], ids=["INV-06_Preis_aufsteigend", "INV-07_Preis_absteigend"]
)
@MITTEL
def test_inv_sort_by_price(inventory_page: InventoryPage, option, reverse):
    """INV-06/07: Sortierung nach Preis (aufsteigend und absteigend).

    Geprüft werden die Preise, nicht die Namen: Zwei Produkte kosten gleich viel
    ($15.99) und ihre Reihenfolge untereinander ist nicht festgelegt.
    """
    inventory_page.sort_by(option)

    prices = inventory_page.product_prices()
    assert prices == sorted(prices, reverse=reverse)
    assert len(prices) == len(PRODUCTS)


@pytest.mark.smoke
@HOCH
def test_inv_08_add_product_to_cart(inventory_page: InventoryPage):
    """INV-08: 'Add to cart' ändert den Button zu 'Remove' und das Warenkorb-Symbol zeigt 1."""
    product = PRODUCT_NAMES[0]

    inventory_page.add_to_cart(product)

    expect(inventory_page.item_button(product)).to_have_text("Remove")
    expect(inventory_page.header.cart_badge).to_have_text("1")


@MITTEL
def test_inv_09_add_multiple_products(inventory_page: InventoryPage):
    """INV-09: Das Warenkorb-Symbol zählt mehrere Produkte korrekt."""
    for count, product in enumerate(PRODUCT_NAMES, start=1):
        inventory_page.add_to_cart(product)
        expect(inventory_page.header.cart_badge).to_have_text(str(count))


@MITTEL
def test_inv_10_remove_product_from_inventory(inventory_page: InventoryPage):
    """INV-10: 'Remove' auf der Produktseite entfernt das Produkt wieder."""
    inventory_page.add_to_cart(PRODUCT_NAMES[0])
    inventory_page.add_to_cart(PRODUCT_NAMES[1])

    inventory_page.remove_from_cart(PRODUCT_NAMES[0])
    expect(inventory_page.header.cart_badge).to_have_text("1")
    expect(inventory_page.item_button(PRODUCT_NAMES[0])).to_have_text("Add to cart")

    inventory_page.remove_from_cart(PRODUCT_NAMES[1])
    expect(inventory_page.header.cart_badge).to_be_hidden()


@NIEDRIG
def test_inv_11_sorting_keeps_cart(inventory_page: InventoryPage):
    """INV-11: Eine Änderung der Sortierung verändert den Warenkorb nicht."""
    inventory_page.add_to_cart(PRODUCT_NAMES[0])

    inventory_page.sort_by("hilo")

    expect(inventory_page.header.cart_badge).to_have_text("1")
    expect(inventory_page.item_button(PRODUCT_NAMES[0])).to_have_text("Remove")
