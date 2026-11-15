"""Wiederverwendbare Fixtures für alle Tests.

Eine Fixture ist eine Vorbereitung, die pytest automatisch vor einem Test ausführt,
wenn der Test sie als Parameter verlangt (z. B. ``def test_x(inventory_page): ...``).

Die Fixture ``page`` kommt von pytest-playwright: Jeder Test bekommt einen
neuen, leeren Browser-Kontext. Dadurch sind alle Tests unabhängig voneinander
(kein geteilter Warenkorb, keine geteilte Sitzung).
"""

import pytest
from playwright.sync_api import Playwright, expect

from data.test_data import Users
from pages import InventoryPage, LoginPage
from utils.flows import login_as

# Wie lange expect(...) maximal auf einen Zustand wartet (Millisekunden)
expect.set_options(timeout=10_000)


# JavaScript, das vor jeder Seite ausgeführt wird und alle CSS-Animationen abschaltet.
# Grund: Bewegte Elemente (z. B. das einfahrende Menü) sind nicht "stabil" und können
# auf langsamen Rechnern nicht zuverlässig angeklickt werden. Die Funktion der Seite
# ändert sich dadurch nicht - nur die Bewegung fällt weg.
DISABLE_ANIMATIONS = """
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
    document.head.appendChild(style);
});
"""


@pytest.fixture(scope="session", autouse=True)
def configure_test_id_attribute(playwright: Playwright):
    """SauceDemo nutzt das Attribut 'data-test' -> get_by_test_id() soll danach suchen."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def page(page):
    """Erweitert die Fixture 'page' von pytest-playwright: Animationen abschalten."""
    page.add_init_script(DISABLE_ANIMATIONS)
    return page


@pytest.fixture
def login_page(page) -> LoginPage:
    """Geöffnete Login-Seite."""
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(page) -> InventoryPage:
    """Als standard_user angemeldet, Produktseite ist geöffnet."""
    return login_as(page, Users.STANDARD)


# --- Mobilgeräte -------------------------------------------------------------

# Gerät -> Browser-Engine. Namen stammen aus der Geräteliste von Playwright.
MOBILE_DEVICES = {
    "iPhone 15": "webkit",
    "Pixel 7": "chromium",
    "iPad (gen 7)": "webkit",
}


@pytest.fixture(params=list(MOBILE_DEVICES), ids=lambda name: name.replace(" ", "_"))
def mobile_page(request, playwright: Playwright):
    """Eine Seite in einem emulierten Mobilgerät (Bildschirmgröße, Touch, User-Agent)."""
    device_name = request.param
    browser_type = getattr(playwright, MOBILE_DEVICES[device_name])
    browser = browser_type.launch(headless=not request.config.getoption("--headed"))
    context = browser.new_context(**playwright.devices[device_name])
    context.add_init_script(DISABLE_ANIMATIONS)
    page = context.new_page()
    yield page
    context.close()
    browser.close()
