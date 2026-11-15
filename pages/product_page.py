"""Page Object für die Produkt-Detailseite (inventory-item.html?id=...)."""

from decimal import Decimal

from playwright.sync_api import expect

from data.test_data import PageTitles
from pages.base_page import BasePage


class ProductPage(BasePage):
    PATH = "inventory-item.html"

    def __init__(self, page):
        super().__init__(page)
        # Name, Beschreibung und Preis haben dieselben data-test-Werte wie in der
        # Produktliste. Deshalb suchen wir sie nur innerhalb des Detail-Bereichs.
        details = page.locator(".inventory_details_container")
        self.name = details.get_by_test_id("inventory-item-name")
        self.description = details.get_by_test_id("inventory-item-desc")
        self.price = details.get_by_test_id("inventory-item-price")
        self.image = page.locator(".inventory_details_img")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
        self.remove_button = page.get_by_test_id("remove")
        self.back_button = page.get_by_test_id("back-to-products")

    def price_value(self) -> Decimal:
        return self.parse_price(self.price.inner_text())

    def add_to_cart(self):
        self.add_to_cart_button.click()

    def remove_from_cart(self):
        self.remove_button.click()

    def back_to_products(self):
        self.back_button.click()
        expect(self.title).to_have_text(PageTitles.INVENTORY)
