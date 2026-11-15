"""Tests mit den speziellen Demo-Benutzern, die absichtlich eingebaute Fehler haben.

Jeder Test läuft mit mehreren Benutzern:
- standard_user ist die Referenz und muss immer bestehen.
- Benutzer mit bekanntem Fehler sind mit ``with_bug(...)`` markiert (Status XFAIL).

Welcher Benutzer bei welchem Test fehlschlägt, wurde am 07.11.2026 auf der
Webseite überprüft.
"""

import pytest
from playwright.sync_api import expect

from data.known_bugs import with_bug
from data.test_data import CUSTOMER, PRODUCT_NAMES, PRODUCTS, Users
from pages import CartPage, CheckoutCompletePage, CheckoutInfoPage, ProductPage
from utils.flows import go_to_overview, login_as
from utils.priority import MITTEL


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.ERROR, with_bug(Users.PROBLEM, "BUG-12"), with_bug(Users.VISUAL, "BUG-19")],
)
@MITTEL
def test_su_01_product_images(page, username):
    """SU-01: Jedes Produkt zeigt sein eigenes Bild."""
    inventory = login_as(page, username)

    for product in PRODUCTS:
        src = inventory.item(product["name"]).locator("img").get_attribute("src")
        assert product["image"] in src, f"Falsches Bild bei {product['name']}: {src}"


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.VISUAL, with_bug(Users.PROBLEM, "BUG-13"), with_bug(Users.ERROR, "BUG-20")],
)
@MITTEL
def test_su_02_sort_name_z_to_a(page, username):
    """SU-02: Sortierung 'Name (Z to A)' funktioniert."""
    inventory = login_as(page, username)

    inventory.sort_by("za")

    names = inventory.product_names()
    assert names == sorted(names, reverse=True)
    assert len(names) == len(PRODUCTS)


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.VISUAL, with_bug(Users.PROBLEM, "BUG-14"), with_bug(Users.ERROR, "BUG-14")],
)
@MITTEL
def test_su_03_add_all_products_to_cart(page, username):
    """SU-03: Alle 6 Produkte lassen sich in den Warenkorb legen."""
    inventory = login_as(page, username)

    inventory.add_all_to_cart()

    expect(inventory.header.cart_badge).to_have_text(str(len(PRODUCTS)), timeout=3_000)


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.ERROR, Users.VISUAL, with_bug(Users.PROBLEM, "BUG-15")],
)
@MITTEL
def test_su_04_product_link_opens_correct_product(page, username):
    """SU-04: Ein Klick auf ein Produkt öffnet die Detailseite genau dieses Produkts."""
    inventory = login_as(page, username)
    details = ProductPage(page)

    for name in PRODUCT_NAMES:
        inventory.open_product(name)
        expect(details.name).to_have_text(name, timeout=3_000)
        details.back_to_products()


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.VISUAL, with_bug(Users.PROBLEM, "BUG-16"), with_bug(Users.ERROR, "BUG-16")],
)
@MITTEL
def test_su_05_checkout_fields_keep_input(page, username):
    """SU-05: Die Felder im Checkout übernehmen die eingegebenen Werte korrekt."""
    inventory = login_as(page, username)
    inventory.add_to_cart(PRODUCT_NAMES[0])
    inventory.header.open_cart()
    CartPage(page).checkout()
    info = CheckoutInfoPage(page)

    info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])

    expect(info.first_name_input).to_have_value(CUSTOMER["first_name"])
    expect(info.last_name_input).to_have_value(CUSTOMER["last_name"], timeout=3_000)
    expect(info.postal_code_input).to_have_value(CUSTOMER["postal_code"])


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.VISUAL, with_bug(Users.ERROR, "BUG-17")],
)
@MITTEL
def test_su_06_finish_completes_order(page, username):
    """SU-06: 'Finish' schließt die Bestellung ab."""
    login_as(page, username)
    overview = go_to_overview(page, [PRODUCT_NAMES[0]])

    overview.finish()

    expect(CheckoutCompletePage(page).complete_header).to_be_visible(timeout=3_000)


@pytest.mark.parametrize(
    "username",
    [Users.STANDARD, Users.PROBLEM, Users.ERROR, with_bug(Users.VISUAL, "BUG-18")],
)
@MITTEL
def test_su_07_product_prices(page, username):
    """SU-07: Alle Produkte zeigen den korrekten Preis."""
    inventory = login_as(page, username)

    for product in PRODUCTS:
        price = inventory.item(product["name"]).get_by_test_id("inventory-item-price")
        expect(price).to_have_text(f"${product['price']}", timeout=3_000)
