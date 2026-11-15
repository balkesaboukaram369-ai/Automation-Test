"""Page Objects für die drei Checkout-Schritte."""

from decimal import Decimal

from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    """Schritt 1: Kundendaten (checkout-step-one.html)."""

    PATH = "checkout-step-one.html"

    def __init__(self, page):
        super().__init__(page)
        self.first_name_input = page.get_by_test_id("firstName")
        self.last_name_input = page.get_by_test_id("lastName")
        self.postal_code_input = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error_message = page.get_by_test_id("error")

    def fill_information(self, first_name: str, last_name: str, postal_code: str):
        self._fill(self.first_name_input, first_name)
        self._fill(self.last_name_input, last_name)
        self._fill(self.postal_code_input, postal_code)

    @staticmethod
    def _fill(field, value: str):
        """Füllt ein Feld aus und prüft, ob der Wert angekommen ist.

        Beobachtung (vor allem WebKit): Direkt nach dem Seitenwechsel geht die erste
        Eingabe gelegentlich verloren, weil die Seite noch nicht ganz bereit ist.
        Deshalb wird bis zu dreimal versucht. Die absichtlichen Fehler der
        Demo-Benutzer (BUG-16) bleiben trotzdem sichtbar, weil sie bei jedem Versuch auftreten.
        """
        for _ in range(3):
            field.fill(value)
            if field.input_value() == value:
                return

    def continue_checkout(self):
        self.continue_button.click()

    def cancel(self):
        self.cancel_button.click()


class CheckoutOverviewPage(BasePage):
    """Schritt 2: Bestellübersicht (checkout-step-two.html)."""

    PATH = "checkout-step-two.html"

    def __init__(self, page):
        super().__init__(page)
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.payment_info = page.get_by_test_id("payment-info-value")
        self.shipping_info = page.get_by_test_id("shipping-info-value")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")

    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def subtotal(self) -> Decimal:
        return self.parse_price(self.subtotal_label.inner_text())

    def tax(self) -> Decimal:
        return self.parse_price(self.tax_label.inner_text())

    def total(self) -> Decimal:
        return self.parse_price(self.total_label.inner_text())

    def finish(self):
        self.finish_button.click()

    def cancel(self):
        self.cancel_button.click()


class CheckoutCompletePage(BasePage):
    """Schritt 3: Bestellbestätigung (checkout-complete.html)."""

    PATH = "checkout-complete.html"

    def __init__(self, page):
        super().__init__(page)
        self.complete_header = page.get_by_test_id("complete-header")
        self.complete_text = page.get_by_test_id("complete-text")
        self.back_home_button = page.get_by_test_id("back-to-products")
        self.generate_pdf_button = page.get_by_test_id("generate-pdf-order")

    def back_home(self):
        self.back_home_button.click()
