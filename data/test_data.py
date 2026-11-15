"""Testdaten für die SauceDemo-Test-Suite.

Alle erwarteten Werte wurden am 07.11.2026 direkt auf https://www.saucedemo.com/
überprüft (Ist-Verhalten der Anwendung), nicht geraten.
"""

from decimal import Decimal


class Users:
    """Die öffentlichen Demo-Benutzer, die auf der Login-Seite angezeigt werden."""

    STANDARD = "standard_user"
    LOCKED_OUT = "locked_out_user"
    PROBLEM = "problem_user"
    PERFORMANCE_GLITCH = "performance_glitch_user"
    ERROR = "error_user"
    VISUAL = "visual_user"

    # Alle Benutzer, die sich erfolgreich anmelden können
    ALL_ACTIVE = [STANDARD, PROBLEM, PERFORMANCE_GLITCH, ERROR, VISUAL]


class Messages:
    """Erwartete Fehlermeldungen (Originaltexte der Anwendung)."""

    LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out."
    WRONG_CREDENTIALS = "Epic sadface: Username and password do not match any user in this service"
    USERNAME_REQUIRED = "Epic sadface: Username is required"
    PASSWORD_REQUIRED = "Epic sadface: Password is required"

    FIRST_NAME_REQUIRED = "Error: First Name is required"
    LAST_NAME_REQUIRED = "Error: Last Name is required"
    POSTAL_CODE_REQUIRED = "Error: Postal Code is required"

    ORDER_COMPLETE_HEADER = "Thank you for your order!"

    @staticmethod
    def not_logged_in(path: str) -> str:
        return f"Epic sadface: You can only access '/{path}' when you are logged in."


class PageTitles:
    """Seitenüberschriften (data-test="title"). An einer Stelle, damit eine Änderung
    der Anwendung nur hier nachgezogen werden muss."""

    INVENTORY = "Products"
    CART = "Your Cart"
    CHECKOUT_INFO = "Checkout: Your Information"

    @staticmethod
    def dynamic_catalog(entry: str) -> str:
        return f"Dynamic Catalog - {entry}"


# Referenzdaten aller 6 Produkte.
# "image" ist ein Teil des Bild-Dateinamens, an dem das richtige Bild erkennbar ist.
PRODUCTS = [
    {
        "name": "Sauce Labs Backpack",
        "price": Decimal("29.99"),
        "image": "sauce-backpack",
        "description": "carry.allTheThings() with the sleek, streamlined Sly Pack that melds "
        "uncompromising style with unequaled laptop and tablet protection.",
    },
    {
        "name": "Sauce Labs Bike Light",
        "price": Decimal("9.99"),
        "image": "bike-light",
        "description": "A red light isn't the desired state in testing but it sure helps when "
        "riding your bike at night. Water-resistant with 3 lighting modes, 1 AAA battery included.",
    },
    {
        "name": "Sauce Labs Bolt T-Shirt",
        "price": Decimal("15.99"),
        "image": "bolt-shirt",
        "description": "Get your testing superhero on with the Sauce Labs bolt T-shirt. From "
        "American Apparel, 100% ringspun combed cotton, heather gray with red bolt.",
    },
    {
        "name": "Sauce Labs Fleece Jacket",
        "price": Decimal("49.99"),
        "image": "sauce-pullover",
        "description": "It's not every day that you come across a midweight quarter-zip fleece "
        "jacket capable of handling everything from a relaxing day outdoors to a busy day at the office.",
    },
    {
        "name": "Sauce Labs Onesie",
        "price": Decimal("7.99"),
        "image": "red-onesie",
        "description": "Rib snap infant onesie for the junior automation engineer in development. "
        "Reinforced 3-snap bottom closure, two-needle hemmed sleeved and bottom won't unravel.",
    },
    {
        "name": "Test.allTheThings() T-Shirt (Red)",
        "price": Decimal("15.99"),
        "image": "red-tatt",
        "description": "This classic Sauce Labs t-shirt is perfect to wear when cozying up to your "
        "keyboard to automate a few tests. Super-soft and comfy ringspun combed cotton.",
    },
]

PRODUCT_NAMES = [p["name"] for p in PRODUCTS]

# Sortieroptionen: Wert im <select> -> angezeigter Text
SORT_OPTIONS = {
    "az": "Name (A to Z)",
    "za": "Name (Z to A)",
    "lohi": "Price (low to high)",
    "hilo": "Price (high to low)",
}

# Steuersatz im Checkout (aus Ist-Verhalten abgeleitet: 39.98 -> Tax 3.20)
TAX_RATE = Decimal("0.08")

# Gültige Kundendaten für den Checkout
CUSTOMER = {"first_name": "Max", "last_name": "Mustermann", "postal_code": "12345"}

# Externe Links: Name -> erwartete Domain nach dem Öffnen
SOCIAL_LINKS = {
    "social-x": "x.com",
    "social-facebook": "facebook.com",
    "social-linkedin": "linkedin.com",
}
ABOUT_DOMAIN = "saucelabs.com"
