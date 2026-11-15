"""Tests für den PDF-Beleg ('Generate PDF order') nach dem Bestellabschluss.

Der Inhalt des PDFs wird mit der Bibliothek pypdf als Text ausgelesen und mit
der Bestellung verglichen.
"""

import re
from datetime import date

import pytest
from pypdf import PdfReader

from data.test_data import CUSTOMER, PRODUCTS
from pages import CheckoutCompletePage, InventoryPage
from utils.flows import go_to_overview
from utils.priority import HOCH, MITTEL, NIEDRIG

ORDER = [PRODUCTS[0], PRODUCTS[1]]


@pytest.fixture
def order_pdf(inventory_page: InventoryPage, tmp_path):
    """Schließt eine Bestellung ab, lädt den PDF-Beleg herunter und liefert Datei, Name und Text."""
    overview = go_to_overview(inventory_page.page, [p["name"] for p in ORDER])
    totals = {"subtotal": overview.subtotal(), "tax": overview.tax(), "total": overview.total()}
    overview.finish()
    complete = CheckoutCompletePage(inventory_page.page)

    # Auf den Download warten, der durch den Klick ausgelöst wird
    with inventory_page.page.expect_download() as download_info:
        complete.generate_pdf_button.click()
    download = download_info.value

    file_path = tmp_path / download.suggested_filename
    download.save_as(file_path)
    text = "\n".join(page.extract_text() for page in PdfReader(file_path).pages)
    return {"path": file_path, "name": download.suggested_filename, "text": text, "totals": totals}


@MITTEL
def test_pdf_01_valid_pdf_file(order_pdf):
    """PDF-01: Es wird eine gültige PDF-Datei mit sinnvollem Namen heruntergeladen."""
    assert re.fullmatch(r"swag-labs-order-[\d_-]+\.pdf", order_pdf["name"]), order_pdf["name"]
    assert order_pdf["path"].read_bytes().startswith(b"%PDF")


@MITTEL
def test_pdf_02_contains_customer_data(order_pdf):
    """PDF-02: Der Beleg enthält Name und Postleitzahl des Kunden."""
    assert f"{CUSTOMER['first_name']} {CUSTOMER['last_name']}" in order_pdf["text"]
    assert CUSTOMER["postal_code"] in order_pdf["text"]


@HOCH
def test_pdf_03_contains_ordered_products(order_pdf):
    """PDF-03: Der Beleg enthält alle bestellten Produkte mit Preis."""
    for product in ORDER:
        assert f"{product['name']} ${product['price']}" in order_pdf["text"]


@HOCH
def test_pdf_04_totals_match_overview(order_pdf):
    """PDF-04: Zwischensumme, Steuer und Gesamtbetrag stimmen mit der Übersicht überein."""
    totals = order_pdf["totals"]
    assert f"Item total ${totals['subtotal']}" in order_pdf["text"]
    assert f"Tax ${totals['tax']}" in order_pdf["text"]
    assert f"Total ${totals['total']}" in order_pdf["text"]


@NIEDRIG
def test_pdf_05_contains_todays_date(order_pdf):
    """PDF-05: Der Beleg trägt das heutige Datum (z. B. 'November 7, 2026')."""
    today = date.today()
    expected = f"{today:%B} {today.day}, {today.year}"
    assert expected in order_pdf["text"]
