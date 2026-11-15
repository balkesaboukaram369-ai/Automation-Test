"""Tests für die Seiten unter 'Dynamic Catalog': Lazy Load, Spinner und Slider.

Der Slider wechselt automatisch per Zeitgeber (Timer). Damit die Tests nicht vom
Zufall abhängen, übernehmen wir mit ``page.clock`` die Uhr des Browsers:
Die Zeit läuft dann nur weiter, wenn der Test es sagt (``clock.run_for``).
"""

from datetime import datetime, timedelta

from playwright.sync_api import expect

from data.known_bugs import known_bug
from data.test_data import PRODUCTS
from pages.dynamic_catalog_page import LazyLoadPage, SliderPage, SpinnerPage
from utils.priority import MITTEL, NIEDRIG

PRICE_BY_NAME = {p["name"]: f"${p['price']}" for p in PRODUCTS}


# --- Lazy Load ---------------------------------------------------------------

def load_at_least(lazy: LazyLoadPage, minimum: int, max_scrolls: int = 15) -> int:
    """Scrollt so lange nach unten, bis mindestens `minimum` Produkte geladen sind."""
    for _ in range(max_scrolls):
        if lazy.item_names.count() >= minimum:
            break
        before = lazy.item_names.count()
        lazy.scroll_to_end()
        expect(lazy.item_names).not_to_have_count(before)
    return lazy.item_names.count()


@NIEDRIG
def test_lazy_01_initial_items_and_placeholders(inventory_page):
    """LAZY-01: Beim Öffnen sind 8 Produkte geladen und 4 Platzhalter ('Loading…') sichtbar."""
    lazy = LazyLoadPage(inventory_page.page).open()

    expect(lazy.item_names).to_have_count(8)
    expect(lazy.placeholders).to_have_count(4)
    expect(lazy.placeholders.first).to_have_text("Loading…")


@MITTEL
def test_lazy_02_scrolling_loads_more_items(inventory_page):
    """LAZY-02: Beim Herunterscrollen werden weitere Produkte nachgeladen."""
    lazy = LazyLoadPage(inventory_page.page).open()
    expect(lazy.item_names).to_have_count(8)

    lazy.scroll_to_end()

    expect(lazy.item_names).not_to_have_count(8)
    assert lazy.item_names.count() > 8


@known_bug("BUG-08")
@NIEDRIG
def test_lazy_03_no_duplicate_entries(inventory_page):
    """LAZY-03: Unter den ersten 20 Einträgen kommt kein Produkt (inkl. Größe) doppelt vor."""
    lazy = LazyLoadPage(inventory_page.page).open()
    load_at_least(lazy, 20)

    names = lazy.item_names.all_inner_texts()[:20]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    assert not duplicates, f"Doppelte Einträge: {duplicates}"


@known_bug("BUG-09")
@NIEDRIG
def test_lazy_04_list_has_an_end(inventory_page):
    """LAZY-04: Die Liste endet, nachdem alle Produkte geladen sind (keine endlose Wiederholung)."""
    lazy = LazyLoadPage(inventory_page.page).open()

    # Ein Katalog mit 6 Produkten in je bis zu 6 Größen hat höchstens 36 Einträge
    count = load_at_least(lazy, 40)
    assert count <= 36, f"Nach dem Scrollen sind {count} Einträge geladen - die Liste wiederholt sich"


# --- Spinner -----------------------------------------------------------------

# Kleines Beobachter-Skript: Es merkt sich, ob der Spinner jemals erschienen ist und ob
# zu diesem Zeitpunkt schon Produkte sichtbar waren. So hängt der Test nicht davon ab,
# ob er den Spinner (der nur ca. 0,5 s sichtbar ist) "rechtzeitig" erwischt.
SPINNER_OBSERVER = """
window.__spinner = { seen: false, itemsWhileSpinning: 0 };
new MutationObserver(() => {
    if (document.querySelector("[data-test='dynamic-catalog-spinner']")) {
        window.__spinner.seen = true;
        window.__spinner.itemsWhileSpinning = Math.max(window.__spinner.itemsWhileSpinning,
            document.querySelectorAll("[data-test^='spinner-item-'][data-test$='-name']").length);
    }
}).observe(document, { childList: true, subtree: true });
"""


@NIEDRIG
def test_spin_01_spinner_is_shown_while_loading(inventory_page):
    """SPIN-01: Beim Öffnen wird zuerst der Lade-Spinner angezeigt, noch ohne Produkte."""
    inventory_page.page.add_init_script(SPINNER_OBSERVER)
    spinner_page = SpinnerPage(inventory_page.page).open()
    expect(spinner_page.item_names).to_have_count(len(PRODUCTS))  # warten, bis fertig geladen

    observed = inventory_page.page.evaluate("window.__spinner")
    assert observed["seen"], "Der Spinner wurde nie angezeigt"
    assert observed["itemsWhileSpinning"] == 0, "Produkte waren schon während des Ladens sichtbar"


@NIEDRIG
def test_spin_02_products_shown_after_loading(inventory_page):
    """SPIN-02: Nach dem Laden verschwindet der Spinner und alle 6 Produkte erscheinen mit korrektem Preis."""
    spinner_page = SpinnerPage(inventory_page.page).open()

    expect(spinner_page.spinner).to_be_hidden()
    expect(spinner_page.item_names).to_have_count(len(PRODUCTS))
    names = spinner_page.item_names.all_inner_texts()
    prices = spinner_page.item_prices.all_inner_texts()
    assert sorted(names) == sorted(PRICE_BY_NAME)
    for name, price in zip(names, prices):
        assert price == PRICE_BY_NAME[name], f"Falscher Preis bei {name}: {price}"


# --- Slider ------------------------------------------------------------------

def freeze_clock(page):
    """Hält die Uhr des Browsers an. Der Slider wechselt dann nicht mehr von selbst.

    Wichtig: install() allein reicht nicht - die Zeit läuft danach normal weiter.
    Erst pause_at() hält sie an (hier: 1 Sekunde in der Zukunft).
    """
    page.clock.install()
    page.clock.pause_at(datetime.now() + timedelta(seconds=1))


@NIEDRIG
def test_sld_01_dots_show_matching_product(inventory_page):
    """SLD-01: Ein Klick auf einen Punkt zeigt genau das Produkt, für das der Punkt steht."""
    freeze_clock(inventory_page.page)  # verhindert, dass der automatische Wechsel stört
    slider = SliderPage(inventory_page.page).open()
    expect(slider.dots).to_have_count(len(PRODUCTS))

    for index in range(len(PRODUCTS)):
        dot = slider.dot(index)
        # Der Punkt beschreibt sich selbst, z. B. aria-label="Show Sauce Labs Onesie"
        expected_name = dot.get_attribute("aria-label").removeprefix("Show ")
        dot.click()
        expect(slider.item_name).to_have_text(expected_name)
        expect(dot).to_have_attribute("aria-current", "true")


@NIEDRIG
def test_sld_02_slider_changes_automatically(inventory_page):
    """SLD-02: Ohne Klick wechselt der Slider nach einiger Zeit automatisch zum nächsten Produkt."""
    freeze_clock(inventory_page.page)
    slider = SliderPage(inventory_page.page).open()
    expect(slider.item_name).not_to_have_text("")
    first_product = slider.item_name.inner_text()

    inventory_page.page.clock.run_for(3_000)  # 3 Sekunden vorspulen (Wechsel erfolgt alle 2 s)
    # Uhr wieder normal laufen lassen, damit die Seite die Änderung auch anzeigen kann
    inventory_page.page.clock.resume()

    expect(slider.item_name).not_to_have_text(first_product)
