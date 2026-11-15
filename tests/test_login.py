"""Tests für die Login-Seite.

Testverfahren:
- Äquivalenzklassen: Benutzername (gültig / gesperrt / unbekannt / leer / falsche
  Schreibweise) und Passwort (richtig / falsch / leer / falsche Schreibweise)
- Entscheidungstabelle für die Pflichtfelder (leer / ausgefüllt)
- Erfahrungsbasiertes Testen (Sicherheit, Enter-Taste)
"""

import time

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL, LOGIN_TIME_LIMIT_SECONDS, PASSWORD
from data.known_bugs import known_bug
from data.test_data import Messages, PageTitles, Users
from pages import InventoryPage, LoginPage
from utils.flows import login_as
from utils.priority import HOCH, MITTEL, NIEDRIG


@HOCH
@pytest.mark.smoke
def test_login_01_standard_user(login_page: LoginPage):
    """LOGIN-01: Login mit gültigen Daten öffnet die Produktseite."""
    login_page.login(Users.STANDARD, PASSWORD)

    inventory = InventoryPage(login_page.page)
    expect(login_page.page).to_have_url(BASE_URL + "inventory.html")
    expect(inventory.title).to_have_text(PageTitles.INVENTORY)


# Jede Zeile ist ein eigener Testfall: Benutzername, Passwort, erwartete Meldung,
# dazu die ID (id=...) und die Priorität (marks=...).
INVALID_LOGINS = [
    pytest.param(Users.LOCKED_OUT, PASSWORD, Messages.LOCKED_OUT, id="LOGIN-02", marks=HOCH),
    pytest.param(Users.STANDARD, "falsches_passwort", Messages.WRONG_CREDENTIALS, id="LOGIN-03", marks=HOCH),
    pytest.param("unbekannter_benutzer", PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-04", marks=MITTEL),
    pytest.param("", "", Messages.USERNAME_REQUIRED, id="LOGIN-05", marks=MITTEL),
    pytest.param(Users.STANDARD, "", Messages.PASSWORD_REQUIRED, id="LOGIN-06", marks=MITTEL),
    pytest.param("", PASSWORD, Messages.USERNAME_REQUIRED, id="LOGIN-07", marks=MITTEL),
    pytest.param("STANDARD_USER", PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-12", marks=MITTEL),
    pytest.param(" " + Users.STANDARD, PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-13a", marks=MITTEL),
    pytest.param(Users.STANDARD + " ", PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-13b", marks=MITTEL),
    pytest.param(Users.STANDARD, PASSWORD.upper(), Messages.WRONG_CREDENTIALS, id="LOGIN-17a", marks=HOCH),
    pytest.param(Users.STANDARD, PASSWORD.capitalize(), Messages.WRONG_CREDENTIALS, id="LOGIN-17b", marks=HOCH),
    pytest.param(Users.STANDARD, " " + PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-18a", marks=MITTEL),
    pytest.param(Users.STANDARD, PASSWORD + " ", Messages.WRONG_CREDENTIALS, id="LOGIN-18b", marks=MITTEL),
    # SQL-Injection: einmal im Benutzernamen, einmal im Passwort, einmal in beiden Feldern
    pytest.param("' OR 1=1 --", PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-19a", marks=HOCH),
    pytest.param(Users.STANDARD, "' OR 1=1 --", Messages.WRONG_CREDENTIALS, id="LOGIN-19b", marks=HOCH),
    pytest.param("' OR 1=1 --", "' OR 1=1 --", Messages.WRONG_CREDENTIALS, id="LOGIN-19c", marks=HOCH),
    # Sehr langer Benutzername (1000 Zeichen): Die Seite darf nicht hängen oder abstürzen
    pytest.param("a" * 1000, PASSWORD, Messages.WRONG_CREDENTIALS, id="LOGIN-20", marks=NIEDRIG),
]


@pytest.mark.parametrize("username, password, expected_message", INVALID_LOGINS)
def test_login_invalid_data_shows_error(login_page: LoginPage, username, password, expected_message):
    """LOGIN-02 bis 07, 12, 13, 17 bis 20: Ungültige Anmeldedaten werden abgelehnt."""
    login_page.login(username, password)

    expect(login_page.error_message).to_have_text(expected_message)
    # Der Benutzer bleibt auf der Login-Seite
    expect(login_page.page).to_have_url(BASE_URL)


@NIEDRIG
def test_login_08_close_error_message(login_page: LoginPage):
    """LOGIN-08: Das X in der Fehlermeldung schließt Meldung und Fehler-Symbole."""
    login_page.login("", "")
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_icons).to_have_count(2)

    login_page.close_error()

    expect(login_page.error_message).to_be_hidden()
    expect(login_page.error_icons).to_have_count(0)


@MITTEL
@pytest.mark.parametrize(
    "username",
    [
        pytest.param(Users.STANDARD, id=Users.STANDARD),
        pytest.param(Users.PERFORMANCE_GLITCH, id="performance_glitch_user-BUG-01", marks=known_bug("BUG-01")),
    ],
)
def test_login_09_login_time_within_limit(login_page: LoginPage, username):
    """LOGIN-09: Nach dem Klick auf Login ist die Produktseite innerhalb des Zeitlimits sichtbar."""
    inventory = InventoryPage(login_page.page)
    login_page.fill_credentials(username, PASSWORD)

    start = time.perf_counter()
    login_page.login_button.click()
    expect(inventory.inventory_list).to_be_visible(timeout=15_000)
    duration = time.perf_counter() - start

    assert duration <= LOGIN_TIME_LIMIT_SECONDS, (
        f"Login dauerte {duration:.2f} s (Limit: {LOGIN_TIME_LIMIT_SECONDS} s)"
    )


@HOCH
@pytest.mark.parametrize(
    "path",
    ["inventory.html", "cart.html", "checkout-step-one.html", "checkout-step-two.html", "checkout-complete.html"],
)
def test_login_10_protected_pages_require_login(page, path):
    """LOGIN-10: Interne Seiten sind ohne Login nicht erreichbar."""
    page.goto(BASE_URL + path)

    login_page = LoginPage(page)
    expect(login_page.login_button).to_be_visible()
    expect(login_page.error_message).to_have_text(Messages.not_logged_in(path))


@HOCH
def test_login_11_back_button_after_logout(page):
    """LOGIN-11: Nach dem Logout führt Browser-Zurück nicht zurück ins Konto."""
    inventory = login_as(page, Users.STANDARD)
    inventory.header.logout()

    page.go_back()

    login_page = LoginPage(page)
    expect(login_page.login_button).to_be_visible()
    expect(inventory.inventory_list).to_be_hidden()
    expect(login_page.error_message).to_have_text(Messages.not_logged_in("inventory.html"))


@known_bug("BUG-25")
@NIEDRIG
def test_login_21_closed_error_stays_closed_after_reload(page):
    """LOGIN-21: Eine geschlossene Fehlermeldung erscheint nach dem Neuladen (F5) nicht wieder.

    Vergleich: Die Meldung bei falschem Passwort verschwindet nach F5. Die Meldung
    nach Logout + Zurück bleibt dagegen, weil die Seite sie in history.state speichert
    (geprüft am 14.11.2026 in Chromium, Firefox und WebKit).
    """
    inventory = login_as(page, Users.STANDARD)
    inventory.header.logout()
    page.go_back()
    login_page = LoginPage(page)
    expect(login_page.error_message).to_have_text(Messages.not_logged_in("inventory.html"))

    login_page.close_error()
    page.reload()
    expect(login_page.login_button).to_be_visible()
    # Kurz warten: Die Meldung wird erst nach dem Button eingeblendet (vor allem in WebKit).
    # Sonst wäre ein "unsichtbar"-Check zu früh wahr.
    page.wait_for_timeout(1_000)

    expect(login_page.error_message).to_be_hidden()


@NIEDRIG
def test_login_14_password_is_masked(login_page: LoginPage):
    """LOGIN-14: Das Passwortfeld zeigt die Eingabe verdeckt an."""
    expect(login_page.password_input).to_have_attribute("type", "password")


@MITTEL
def test_login_15_login_with_enter_key(login_page: LoginPage):
    """LOGIN-15: Login funktioniert auch mit der Enter-Taste."""
    login_page.login_with_enter(Users.STANDARD, PASSWORD)

    expect(login_page.page).to_have_url(BASE_URL + "inventory.html")


@MITTEL

@pytest.mark.parametrize("username", Users.ALL_ACTIVE)
def test_login_16_all_active_users_can_log_in(page, username):
    """LOGIN-16: Alle aktiven Demo-Benutzer können sich anmelden."""
    inventory = login_as(page, username)

    expect(inventory.title).to_have_text(PageTitles.INVENTORY)
