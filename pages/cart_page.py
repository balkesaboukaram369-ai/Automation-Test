"""Page Object für den Warenkorb (cart.html)."""

from decimal import Decimal

from playwright.sync_api import expect

from data.test_data import PageTitles
from pages.base_page import BasePage


class CartPage(BasePage):
    PATH = "cart.html"

    def __init__(self, page):
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.item_quantities = page.get_by_test_id("item-quantity")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")
        self.checkout_button = page.get_by_test_id("checkout")

    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def product_prices(self) -> list[Decimal]:
        return [self.parse_price(text) for text in self.item_prices.all_inner_texts()]

    def remove(self, product_name: str):
        item = self.items.filter(has=self.page.get_by_text(product_name, exact=True))
        item.get_by_role("button", name="Remove").click()

    def continue_shopping(self):
        self.continue_shopping_button.click()
        expect(self.title).to_have_text(PageTitles.INVENTORY)

    def checkout(self):
        self.checkout_button.click()
        expect(self.title).to_have_text(PageTitles.CHECKOUT_INFO)
