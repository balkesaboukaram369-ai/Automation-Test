"""Tests für den Checkout (Kundendaten -> Übersicht -> Bestätigung)."""

from decimal import ROUND_HALF_UP, Decimal

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from data.known_bugs import known_bug
from data.test_data import CUSTOMER, PRODUCTS, TAX_RATE, Messages
from pages import CartPage, CheckoutCompletePage, CheckoutInfoPage, CheckoutOverviewPage, InventoryPage
from utils.flows import add_products, go_to_overview
from utils.priority import HOCH, MITTEL

# Drei Produkte für die Berechnung der Summen
ORDER = [PRODUCTS[0], PRODUCTS[1], PRODUCTS[4]]
ORDER_NAMES = [p["name"] for p in ORDER]


@pytest.fixture
def checkout_info(inventory_page: InventoryPage) -> CheckoutInfoPage:
    """Ein Produkt im Warenkorb, Checkout-Schritt 1 ist geöffnet."""
    add_products(inventory_page, [ORDER_NAMES[0]])
    inventory_page.header.open_cart()
    CartPage(inventory_page.page).checkout()
    return CheckoutInfoPage(inventory_page.page)


@pytest.fixture
def overview(inventory_page: InventoryPage) -> CheckoutOverviewPage:
    """Drei Produkte bestellt, die Übersicht (Schritt 2) ist geöffnet."""
    return go_to_overview(inventory_page.page, ORDER_NAMES)


@pytest.mark.smoke
@HOCH
def test_co_01_complete_order_end_to_end(overview: CheckoutOverviewPage):
    """CO-01: Kompletter Kaufprozess endet mit der Bestellbestätigung."""
    overview.finish()

    complete = CheckoutCompletePage(overview.page)
    expect(complete.page).to_have_url(BASE_URL + "checkout-complete.html")
    expect(complete.complete_header).to_have_text(Messages.ORDER_COMPLETE_HEADER)


# Entscheidungstabelle der Pflichtfelder: (ID, Vorname, Nachname, PLZ, erwartete Meldung)
MISSING_FIELDS = [
    ("CO-02", "", "", "", Messages.FIRST_NAME_REQUIRED),
    ("CO-03", CUSTOMER["first_name"], "", "", Messages.LAST_NAME_REQUIRED),
    ("CO-04", CUSTOMER["first_name"], CUSTOMER["last_name"], "", Messages.POSTAL_CODE_REQUIRED),
    ("CO-05", "", CUSTOMER["last_name"], CUSTOMER["postal_code"], Messages.FIRST_NAME_REQUIRED),
]


@pytest.mark.parametrize("case_id, first, last, postal, message", MISSING_FIELDS, ids=[r[0] for r in MISSING_FIELDS])
@HOCH
def test_co_required_fields(checkout_info: CheckoutInfoPage, case_id, first, last, postal, message):
    """CO-02 bis 05: Fehlende Pflichtfelder werden gemeldet, der Checkout geht nicht weiter."""
    checkout_info.fill_information(first, last, postal)
    checkout_info.continue_checkout()

    expect(checkout_info.error_message).to_have_text(message)
    expect(checkout_info.page).to_have_url(BASE_URL + "checkout-step-one.html")


@MITTEL
def test_co_06_cancel_on_step_one(checkout_info: CheckoutInfoPage):
    """CO-06: 'Cancel' in Schritt 1 führt zurück zum Warenkorb."""
    checkout_info.cancel()

    expect(checkout_info.page).to_have_url(BASE_URL + "cart.html")


@MITTEL
def test_co_07_overview_shows_order_details(overview: CheckoutOverviewPage):
    """CO-07: Die Übersicht zeigt die Produkte sowie Zahlungs- und Versandinformationen."""
    assert overview.product_names() == ORDER_NAMES
    expect(overview.payment_info).to_have_text("SauceCard #31337")
    expect(overview.shipping_info).to_have_text("Free Pony Express Delivery!")


@HOCH
def test_co_08_item_total_is_sum_of_prices(overview: CheckoutOverviewPage):
    """CO-08: 'Item total' ist die Summe der Produktpreise."""
    expected = sum(p["price"] for p in ORDER)
    assert overview.subtotal() == expected


@HOCH
def test_co_09_tax_is_eight_percent(overview: CheckoutOverviewPage):
    """CO-09: Die Steuer beträgt 8 % der Zwischensumme (kaufmännisch gerundet)."""
    expected = (overview.subtotal() * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert overview.tax() == expected


@HOCH
def test_co_10_total_is_subtotal_plus_tax(overview: CheckoutOverviewPage):
    """CO-10: 'Total' ist Zwischensumme plus Steuer."""
    assert overview.total() == overview.subtotal() + overview.tax()


@MITTEL
def test_co_11_cancel_on_overview_keeps_cart(overview: CheckoutOverviewPage):
    """CO-11: 'Cancel' in der Übersicht führt zur Produktseite, der Warenkorb bleibt erhalten."""
    overview.cancel()

    expect(overview.page).to_have_url(BASE_URL + "inventory.html")
    expect(overview.header.cart_badge).to_have_text(str(len(ORDER)))


@HOCH
def test_co_12_finish_empties_cart(overview: CheckoutOverviewPage):
    """CO-12: Nach 'Finish' ist der Warenkorb leer."""
    overview.finish()

    expect(overview.header.cart_badge).to_be_hidden()


@MITTEL
def test_co_13_back_home_after_order(overview: CheckoutOverviewPage):
    """CO-13: 'Back Home' führt zur Produktseite, alle Produkte sind wieder bestellbar."""
    overview.finish()
    CheckoutCompletePage(overview.page).back_home()

    inventory = InventoryPage(overview.page)
    expect(inventory.page).to_have_url(BASE_URL + "inventory.html")
    expect(inventory.items.get_by_role("button", name="Remove")).to_have_count(0)


@known_bug("BUG-03")
@MITTEL
def test_co_15_checkout_not_possible_with_empty_cart(inventory_page: InventoryPage):
    """CO-15: Bei leerem Warenkorb ist 'Checkout' deaktiviert oder ausgeblendet."""
    inventory_page.header.open_cart()
    checkout_button = CartPage(inventory_page.page).checkout_button

    # Erwartung: Button ist nicht sichtbar ODER nicht anklickbar
    assert not (checkout_button.is_visible() and checkout_button.is_enabled()), (
        "Checkout-Button ist trotz leerem Warenkorb aktiv"
    )


@known_bug("BUG-04")
@MITTEL
def test_co_16a_overview_not_reachable_by_url(inventory_page: InventoryPage):
    """CO-16a: Die Übersicht ist ohne Kundendaten nicht direkt per URL erreichbar."""
    inventory_page.page.goto(BASE_URL + "checkout-step-two.html")
    # Erst warten, bis überhaupt eine Seite angezeigt wird - sonst wäre "unsichtbar" zu früh wahr
    expect(inventory_page.title).to_be_visible()

    expect(CheckoutOverviewPage(inventory_page.page).finish_button).to_be_hidden(timeout=3_000)


@known_bug("BUG-04")
@MITTEL
def test_co_16b_confirmation_not_reachable_by_url(inventory_page: InventoryPage):
    """CO-16b: Die Bestellbestätigung ist ohne Bestellung nicht direkt per URL erreichbar."""
    inventory_page.page.goto(BASE_URL + "checkout-complete.html")
    expect(inventory_page.title).to_be_visible()

    expect(CheckoutCompletePage(inventory_page.page).complete_header).to_be_hidden(timeout=3_000)


@MITTEL
@known_bug("BUG-24")
def test_co_17_fields_with_only_spaces_are_rejected(checkout_info: CheckoutInfoPage):
    """CO-17: Pflichtfelder, die nur Leerzeichen enthalten, gelten als leer und werden abgelehnt."""
    checkout_info.fill_information("   ", "   ", "   ")

    checkout_info.continue_checkout()

    expect(checkout_info.error_message).to_be_visible(timeout=3_000)
    expect(checkout_info.page).to_have_url(BASE_URL + "checkout-step-one.html")


@HOCH
def test_co_18_html_in_input_is_not_executed(checkout_info: CheckoutInfoPage):
    """CO-18: HTML/JavaScript in den Eingabefeldern wird nicht ausgeführt (Schutz vor XSS)."""
    page = checkout_info.page
    dialogs = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))

    checkout_info.fill_information("<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "10115")
    checkout_info.continue_checkout()
    overview = CheckoutOverviewPage(page)
    overview.finish()
    expect(CheckoutCompletePage(page).complete_header).to_be_visible()

    assert dialogs == [], f"Eingeschleuster Code wurde ausgeführt: {dialogs}"
