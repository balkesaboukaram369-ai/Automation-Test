"""Page Objects für die drei Seiten unter 'Dynamic Catalog' im Menü."""

from pages.base_page import BasePage


class LazyLoadPage(BasePage):
    """Produkte werden beim Herunterscrollen nachgeladen."""

    PATH = "dynamic-catalog-lazy-load.html"

    def __init__(self, page):
        super().__init__(page)
        # CSS-Selektor: data-test beginnt mit "lazy-load-item-" und endet mit "-name"
        self.item_names = page.locator("[data-test^='lazy-load-item-'][data-test$='-name']")
        self.placeholders = page.locator("[data-test^='lazy-load-item-'][data-test$='-placeholder']")
        self.sentinel = page.get_by_test_id("dynamic-catalog-lazy-load-sentinel")

    def scroll_to_end(self):
        """Scrollt zum unteren Ende der Liste und löst so das Nachladen aus."""
        self.sentinel.scroll_into_view_if_needed()


class SpinnerPage(BasePage):
    """Zeigt zuerst einen Lade-Spinner, danach die Produkte."""

    PATH = "dynamic-catalog-spinner.html"

    def __init__(self, page):
        super().__init__(page)
        self.spinner = page.get_by_test_id("dynamic-catalog-spinner")
        self.item_names = page.locator("[data-test^='spinner-item-'][data-test$='-name']")
        self.item_prices = page.locator("[data-test^='spinner-item-'][data-test$='-price']")


class SliderPage(BasePage):
    """Zeigt immer ein Produkt, mit Punkten zum Umschalten und automatischem Wechsel."""

    PATH = "dynamic-catalog-slider.html"

    def __init__(self, page):
        super().__init__(page)
        self.item_name = page.get_by_test_id("dynamic-catalog-slider-item-name")
        self.dots = page.locator("[data-test^='dynamic-catalog-slider-dot-']")

    def dot(self, index: int):
        return self.page.get_by_test_id(f"dynamic-catalog-slider-dot-{index}")
