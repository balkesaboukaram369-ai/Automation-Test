"""Tests für die Links im Footer (X, Facebook, LinkedIn).

Geprüft wird nur, dass ein neuer Tab mit der richtigen Domain geöffnet wird.
Der Inhalt fremder Webseiten wird bewusst NICHT geprüft: Er liegt nicht in der
Verantwortung unseres Kunden und ändert sich ständig (Login-Seiten, Cookie-Banner).
"""

from datetime import date
from urllib.parse import urlparse

import pytest
from playwright.sync_api import expect

from data.test_data import SOCIAL_LINKS
from pages import InventoryPage
from utils.priority import NIEDRIG


@pytest.mark.external
@pytest.mark.parametrize("test_id, domain", SOCIAL_LINKS.items(), ids=["LINK-01_X", "LINK-02_Facebook", "LINK-03_LinkedIn"])
@NIEDRIG
def test_social_link_opens_correct_site(inventory_page: InventoryPage, test_id, domain):
    """LINK-01 bis 03: Social-Media-Link öffnet in einem neuen Tab die richtige Webseite."""
    context = inventory_page.page.context

    # Alle Adressen merken, die ein neuer Tab aufruft. Grund: Manche Seiten (z. B. x.com)
    # blockieren automatisierte Browser. Dann zeigt der Tab eine Fehlerseite, obwohl der
    # Link richtig ist. Wir prüfen deshalb die aufgerufene Adresse, nicht den Inhalt.
    called_urls = []
    context.on("request", lambda request: called_urls.append(request.url) if request.is_navigation_request() else None)

    # Warten, bis sich durch den Klick ein neuer Tab öffnet
    with context.expect_page(timeout=30_000) as new_tab_info:
        inventory_page.header.social_link(test_id).click()
    new_tab = new_tab_info.value
    new_tab.wait_for_load_state("domcontentloaded", timeout=30_000)

    hosts = [urlparse(url).hostname or "" for url in called_urls]
    assert any(host == domain or host.endswith("." + domain) for host in hosts), (
        f"Unerwartete Adresse: {called_urls}"
    )


@NIEDRIG
def test_link_04_footer_copyright(inventory_page: InventoryPage):
    """LINK-04: Der Footer zeigt den Copyright-Hinweis mit dem aktuellen Jahr."""
    expect(inventory_page.header.footer_copy).to_contain_text(f"© {date.today().year} Sauce Labs. All Rights Reserved.")
