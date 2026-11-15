"""Tests für die Sitzung (Session) und die Darstellung von Fehlermeldungen.

Die Sitzung wird in einem Cookie namens 'session-username' gespeichert.
Er läuft 10 Minuten nach dem Login ab (geprüft am 07.11.2026).

Statt 10 Minuten zu warten, löschen wir den Cookie. Für die Anwendung sieht das
genauso aus wie eine abgelaufene Sitzung - der Test dauert so nur wenige Sekunden.
"""

import re
import time

import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL, PASSWORD
from data.known_bugs import expect_bug_except_in, known_bug
from data.test_data import Messages, Users
from pages import LoginPage
from utils.flows import login_as
from utils.priority import HOCH, NIEDRIG

SESSION_COOKIE = "session-username"
EXPECTED_LIFETIME_SECONDS = 600  # 10 Minuten


@HOCH
def test_sess_01_expired_session_redirects_to_login(page):
    """SESS-01: Nach Ablauf der Sitzung führt der nächste Klick zur Login-Seite."""
    inventory = login_as(page, Users.STANDARD)
    page.context.clear_cookies()  # simuliert die abgelaufene Sitzung

    inventory.header.cart_link.click()

    login_page = LoginPage(page)
    expect(login_page.login_button).to_be_visible()
    expect(login_page.error_message).to_have_text(Messages.not_logged_in("cart.html"))


@known_bug("BUG-11")
@NIEDRIG
def test_sess_02_expired_session_message_is_clear(page):
    """SESS-02: Die Meldung nach Ablauf der Sitzung sagt klar, dass die Sitzung abgelaufen ist."""
    inventory = login_as(page, Users.STANDARD)
    page.context.clear_cookies()

    inventory.header.cart_link.click()

    expect(LoginPage(page).error_message).to_have_text(re.compile(r"session|expired|abgelaufen", re.IGNORECASE))


@NIEDRIG
def test_sess_04_session_cookie_lifetime(page):
    """SESS-04: Der Sitzungs-Cookie ist 10 Minuten gültig (Ist-Verhalten als Regressionsschutz)."""
    login_as(page, Users.STANDARD)

    cookies = {c["name"]: c for c in page.context.cookies()}
    assert SESSION_COOKIE in cookies, "Sitzungs-Cookie wurde nicht gesetzt"

    remaining = cookies[SESSION_COOKIE]["expires"] - time.time()
    # 30 Sekunden Toleranz für die Laufzeit des Tests
    assert abs(remaining - EXPECTED_LIFETIME_SECONDS) <= 30, f"Restlaufzeit: {remaining:.0f} s"


@HOCH
def test_sess_05_logout_deletes_session_cookie(page):
    """SESS-05: Beim Logout wird der Sitzungs-Cookie gelöscht."""
    inventory = login_as(page, Users.STANDARD)

    inventory.header.logout()

    names = [c["name"] for c in page.context.cookies()]
    assert SESSION_COOKIE not in names


def _trigger_not_logged_in(page):
    page.goto(BASE_URL + "inventory.html")  # ohne Login -> "You can only access ..."


def _trigger_wrong_credentials(page):
    LoginPage(page).open().login(Users.STANDARD, "falsches-passwort")


def _trigger_locked_out(page):
    LoginPage(page).open().login(Users.LOCKED_OUT, PASSWORD)


# Gemessen am 14.11.2026 (Fenster 1920 x 1080): Die ersten beiden Meldungen sind in allen
# Browsern abgeschnitten, "locked out" nur in Firefox (dort ist die Schrift etwas breiter).
LONG_MESSAGES = [
    pytest.param(_trigger_not_logged_in, [], id="UI-01a_not_logged_in"),
    pytest.param(_trigger_wrong_credentials, [], id="UI-01b_wrong_credentials"),
    pytest.param(_trigger_locked_out, ["chromium", "webkit"], id="UI-01c_locked_out"),
]


@NIEDRIG
@pytest.mark.parametrize("trigger, unaffected_browsers", LONG_MESSAGES)
def test_ui_01_long_error_message_is_fully_visible(page, trigger, unaffected_browsers, request, browser_name):
    """UI-01: Lange Fehlermeldungen werden vollständig angezeigt (nicht abgeschnitten)."""
    expect_bug_except_in(request, browser_name, "BUG-10", unaffected_browsers)
    page.set_viewport_size({"width": 1920, "height": 1080})
    trigger(page)
    login_page = LoginPage(page)
    expect(login_page.error_message).to_be_visible()

    # scrollHeight = benötigte Höhe des Inhalts, clientHeight = tatsächlich sichtbare Höhe.
    # 4 px Toleranz: Firefox rundet auch bei einzeiligen Meldungen um 2 px auf.
    container = page.locator(".error-message-container")
    needed = container.evaluate("el => el.scrollHeight")
    visible = container.evaluate("el => el.clientHeight")
    assert needed <= visible + 4, f"Text braucht {needed}px, sichtbar sind nur {visible}px"
