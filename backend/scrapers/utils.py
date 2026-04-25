import asyncio
import random
from typing import Any

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def get_ml_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def get_amazon_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


async def random_delay(min_s: float = 1.0, max_s: float = 3.0) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


def clean_price(raw: str) -> float | None:
    """Convert price string to float regardless of locale format."""
    if not raw:
        return None
    cleaned = raw.strip().replace("\xa0", "").replace(" ", "")
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def truncate(text: str, max_len: int = 120) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


def safe_get(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d
