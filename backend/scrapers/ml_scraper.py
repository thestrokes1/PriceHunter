"""MercadoLibre Argentina scraper — poly-card design system."""
import re
import httpx
from bs4 import BeautifulSoup
from .utils import get_ml_headers, random_delay, clean_price, truncate

SEARCH_URL = "https://listado.mercadolibre.com.ar/{query}"


async def search_ml(query: str, limit: int = 10) -> list[dict]:
    url = SEARCH_URL.format(query=query.replace(" ", "-"))
    headers = get_ml_headers()

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            await random_delay(0.5, 1.5)
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        print(f"[ML] Error fetching: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("li.ui-search-layout__item")[:limit]
    results = []

    for item in items:
        # Title & direct product URL
        title_el = item.select_one("a.poly-component__title")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        # Prefer direct ML URL; some sponsored items only have tracking links
        raw_href = title_el.get("href", "")
        product_url = raw_href.split("#")[0].split("?")[0]
        # If it's a tracking URL, look for a direct ML link anywhere in the item
        if "click1.mercadolibre" in product_url or not product_url:
            direct = re.search(r'(https://www\.mercadolibre\.com\.ar/[^"#?]+)', str(item))
            if direct:
                product_url = direct.group(1)
            else:
                product_url = raw_href  # keep tracking URL as fallback
        if not product_url:
            continue

        # Price
        price_el = item.select_one("div.poly-price__current span.andes-money-amount__fraction")
        if not price_el:
            price_el = item.select_one("span.andes-money-amount__fraction")
        if not price_el:
            continue
        price = clean_price(price_el.get_text(strip=True))
        if price is None:
            continue

        # Image
        img_el = item.select_one("img")
        imagen_url = None
        if img_el:
            imagen_url = img_el.get("data-src") or img_el.get("src")

        # Rating
        rating_el = item.select_one("span.poly-component__review-compacted, span[class*=review-rating]")
        rating = None
        if rating_el:
            try:
                rating = float(rating_el.get_text(strip=True).replace(",", ".").split()[0])
            except (ValueError, IndexError):
                pass

        # Review count — extract from aria-label or nearby element
        reviews_el = item.select_one("[class*=review] span:not([class*=rating])")
        reviews = None
        if reviews_el:
            text = re.sub(r"[^\d]", "", reviews_el.get_text())
            reviews = int(text) if text else None

        results.append({
            "title": truncate(title),
            "url": product_url,
            "source": "mercadolibre",
            "price": price,
            "currency": "ARS",
            "imagen_url": imagen_url,
            "rating": rating,
            "reviews": reviews,
        })

    return results
