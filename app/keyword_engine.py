import re
from dataclasses import dataclass

RULES: list[dict] = [
    {
        "name": "price",
        "keywords": ["price", "rate", "cost", "pricing", "bhav", "kitne ka"],
        "text": "Thank you for contacting Shree Annapure Foods. Please find our latest price list attached.",
        "image_filename": "price_list.jpg",
    },
    {
        "name": "catalog",
        "keywords": ["catalog", "menu", "products", "product list"],
        "text": "Please find our latest product catalog attached.",
        "image_filename": "catalog.jpg",
    },
    {
        "name": "wholesale",
        "keywords": ["wholesale", "bulk", "dealer", "distributor", "reseller"],
        "text": "Thank you for your wholesale inquiry. Our team will contact you shortly.",
        "image_filename": "wholesale.jpg",
    },
    {
        "name": "location",
        "keywords": ["location", "address", "shop", "store", "where"],
        "text": (
            "Our products are available through direct orders and selected delivery platforms. "
            "Please contact us for exact location details."
        ),
        "image_filename": None,
    },
    {
        "name": "greeting",
        "keywords": ["hi", "hello", "hey", "namaste"],
        "text": (
            "Welcome to Shree Annapure Foods. "
            "Reply with PRICE, CATALOG, WHOLESALE, or LOCATION to get information."
        ),
        "image_filename": None,
    },
]

DEFAULT_RESPONSE = (
    "Thank you for contacting Shree Annapure Foods. "
    "Please send PRICE, CATALOG, WHOLESALE, or LOCATION for more information."
)


@dataclass(frozen=True)
class KeywordMatch:
    rule_name: str
    response_text: str
    image_filename: str | None


def normalize_message(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _keywords_match(keywords: list[str], normalized: str, words: set[str]) -> bool:
    for keyword in keywords:
        if " " in keyword:
            if keyword in normalized:
                return True
        elif keyword in words:
            return True
    return False


def match(text: str) -> KeywordMatch:
    normalized = normalize_message(text)
    words = set(normalized.split())

    for rule in RULES:
        if _keywords_match(rule["keywords"], normalized, words):
            return KeywordMatch(
                rule_name=rule["name"],
                response_text=rule["text"],
                image_filename=rule["image_filename"],
            )

    return KeywordMatch(
        rule_name="default",
        response_text=DEFAULT_RESPONSE,
        image_filename=None,
    )
