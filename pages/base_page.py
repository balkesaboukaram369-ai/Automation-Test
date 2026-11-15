"""Basisklasse für alle Page Objects."""

from decimal import Decimal

from playwright.sync_api import Page

from config.settings import BASE_URL
from pages.header import Header


class BasePage:
    """Gemeinsame Funktionen aller Seiten.

    Jede Seite kennt ihren eigenen Pfad (PATH) und hat Zugriff auf den Header
    (Menü, Warenkorb-Symbol, Footer-Links), der auf allen Seiten nach dem Login gleich ist.
    """

    PATH = ""

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.title = page.get_by_test_id("title")

    def open(self, wait_until: str = "load"):
        """Öffnet die Seite direkt über ihre URL.

        wait_until="load" wartet auf alle Inhalte inkl. Bilder (Standard).
        wait_until="domcontentloaded" wartet nur auf das HTML - nötig, wenn Bilder
        absichtlich verzögert werden (Tests mit langsamer Verbindung).
        """
        self.page.goto(BASE_URL + self.PATH, wait_until=wait_until)
        return self

    @staticmethod
    def parse_price(text: str) -> Decimal:
        """Wandelt z. B. '$29.99' oder 'Total: $43.18' in Decimal('29.99') / Decimal('43.18') um."""
        return Decimal(text.split("$")[-1].strip())
