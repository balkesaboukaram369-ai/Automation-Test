"""Header-Komponente: Burger-Menü, Warenkorb-Symbol und Footer-Links.

Diese Elemente erscheinen auf jeder Seite nach dem Login. Deshalb liegen sie
in einer eigenen Klasse, statt in jedem Page Object wiederholt zu werden.
"""

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from data.test_data import PageTitles


class Header:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_test_id("title")  # Seitenüberschrift, z. B. "Products"
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.close_menu_button = page.locator("#react-burger-cross-btn")
        self.menu_panel = page.locator(".bm-menu-wrap")
        self.menu_links = page.locator(".bm-item-list a")
        self.all_items_link = page.get_by_test_id("inventory-sidebar-link")
        self.about_link = page.get_by_test_id("about-sidebar-link")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.footer_copy = page.get_by_test_id("footer-copy")

    # --- Menü -------------------------------------------------------------
    def open_menu(self):
        """Öffnet das Burger-Menü.

        Beobachtung: Direkt nach einem Seitenwechsel geht ein Klick auf den Menü-Button
        gelegentlich verloren (die Seite ist noch nicht ganz bereit). Deshalb wird der
        Klick bis zu dreimal versucht, bis das Menü sichtbar ist.
        """
        for attempt in range(3):
            # Nur klicken, wenn das Menü noch geschlossen ist (sonst würde es wieder zugehen)
            if self.menu_panel.get_attribute("aria-hidden") != "false":
                self.menu_button.click()
            try:
                # Warten, bis die Einblend-Animation fertig und das Menü bedienbar ist
                self.logout_link.wait_for(state="visible", timeout=10_000)
                return
            except PlaywrightTimeoutError:
                if attempt == 2:
                    raise

    def close_menu(self):
        self.close_menu_button.click()

    def go_to_all_items(self):
        self.open_menu()
        self.all_items_link.click()
        expect(self.title).to_have_text(PageTitles.INVENTORY)

    def logout(self):
        self.open_menu()
        self.logout_link.click()
        # Warten, bis die Login-Seite angezeigt wird (Logout ist abgeschlossen)
        expect(self.page.get_by_test_id("login-button")).to_be_visible()

    def reset_app_state(self):
        self.open_menu()
        self.reset_link.click()

    def open_about(self):
        self.open_menu()
        self.about_link.click()

    # --- Warenkorb --------------------------------------------------------
    def open_cart(self):
        self.cart_link.click()
        # Warten, bis die Warenkorb-Seite wirklich angezeigt wird. Sonst könnte der
        # nächste Schritt noch die alte Seite lesen (in langsameren Browsern wie WebKit).
        expect(self.title).to_have_text(PageTitles.CART)

    def cart_count(self) -> int:
        """Zahl im Warenkorb-Symbol (0, wenn kein Badge angezeigt wird)."""
        if self.cart_badge.count() == 0:
            return 0
        return int(self.cart_badge.inner_text())

    # --- Footer -----------------------------------------------------------
    def social_link(self, test_id: str):
        return self.page.get_by_test_id(test_id)
