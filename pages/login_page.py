"""Page Object für die Login-Seite."""

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = ""

    def __init__(self, page):
        super().__init__(page)
        self.username_input = page.get_by_test_id("username")
        self.password_input = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error_message = page.get_by_test_id("error")
        self.error_close_button = page.get_by_test_id("error-button")
        # Die roten X-Symbole in den Eingabefeldern bei einem Fehler
        self.error_icons = page.locator(".error_icon")

    def fill_credentials(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)

    def login(self, username: str, password: str):
        """Zugangsdaten eingeben und auf 'Login' klicken."""
        self.fill_credentials(username, password)
        self.login_button.click()

    def login_with_enter(self, username: str, password: str):
        """Zugangsdaten eingeben und mit der Enter-Taste absenden."""
        self.fill_credentials(username, password)
        self.password_input.press("Enter")

    def close_error(self):
        self.error_close_button.click()
