"""Page Object für die Produktübersicht (inventory.html)."""

from decimal import Decimal

from playwright.sync_api import expect

from pages.base_page import BasePage


class InventoryPage(BasePage):
    PATH = "inventory.html"

    def __init__(self, page):
        super().__init__(page)
        self.inventory_list = page.get_by_test_id("inventory-list")
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.sort_dropdown = page.get_by_test_id("product-sort-container")
        self.active_sort = page.get_by_test_id("active-option")

    # --- Lesen ------------------------------------------------------------
    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def product_prices(self) -> list[Decimal]:
        return [self.parse_price(text) for text in self.item_prices.all_inner_texts()]

    def product_image_sources(self) -> list[str]:
        return [img.get_attribute("src") for img in self.items.locator("img").all()]

    def item(self, product_name: str):
        """Die Produktkachel, die den angegebenen Namen enthält."""
        return self.items.filter(has=self.page.get_by_text(product_name, exact=True))

    def item_button(self, product_name: str):
        """Der Button ('Add to cart' bzw. 'Remove') eines Produkts.

        Hinweis: Bild und Name sind ebenfalls als role="button" markiert,
        deshalb suchen wir hier gezielt das echte <button>-Element.
        """
        return self.item(product_name).locator("button")

    # --- Aktionen ---------------------------------------------------------
    def sort_by(self, option_value: str):
        self.sort_dropdown.select_option(option_value)

    def add_to_cart(self, product_name: str):
        self.item(product_name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name: str):
        self.item(product_name).get_by_role("button", name="Remove").click()

    def add_all_to_cart(self):
        """Klickt bei jedem Produkt einmal auf 'Add to cart' (bzw. auf seinen Button)."""
        for name in self.product_names():
            self.item_button(name).click()

    def open_product(self, product_name: str):
        """Öffnet die Detailseite über den Produktnamen."""
        self.item(product_name).get_by_test_id("inventory-item-name").click()
        self._wait_for_details()

    def open_product_by_image(self, product_name: str):
        """Öffnet die Detailseite über das Produktbild."""
        self.item(product_name).locator("img").click()
        self._wait_for_details()

    def _wait_for_details(self):
        """Wartet, bis die Detailseite wirklich angezeigt wird."""
        expect(self.page.locator(".inventory_details_container")).to_be_visible()
