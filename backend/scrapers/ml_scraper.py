"""MercadoLibre Argentina scraper."""
import httpx
from bs4 import BeautifulSoup
from .utils import get_ml_headers, random_delay, clean_price, truncate

BASE_URL = "https://www.mercadolibre.com.ar/jm/search"


async def search_ml(query: str, limit: int = 10) -> list[dict]:
    params = {"as_word": query}
    headers = get_ml_headers()

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            await random_delay(0.5, 1.5)
            resp = await client.get(BASE_URL, params=params, headers=headers)
            resp.raise_for_status()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        print(f"[ML] Error fetching: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    items = soup.select("li.ui-search-layout__item")[:limit]
    results = []

    for item in items:
        title_el = item.select_one("h2.ui-search-item__title")
        price_el = item.select_one("span.andes-money-amount__fraction")
        link_el = item.select_one("a.ui-search-link")
        img_el = item.select_one("img.ui-search-result-image__element")
        rating_el = item.select_one("span.ui-search-reviews__rating-number")
        reviews_el = item.select_one("span.ui-search-reviews__amount")

        if not title_el or not price_el or not link_el:
            continue

        raw_price = price_el.get_text(strip=True)
        price = clean_price(raw_price)
        if price is None:
            continue

        reviews_text = reviews_el.get_text(strip=True).strip("()") if reviews_el else None
        try:
            reviews = int(reviews_text.replace(".", "")) if reviews_text else None
        except ValueError:
            reviews = None

        results.append({
            "title": truncate(title_el.get_text(strip=True)),
            "url": link_el["href"].split("?")[0],
            "source": "mercadolibre",
            "price": price,
            "currency": "ARS",
            "imagen_url": img_el.get("data-src") or img_el.get("src") if img_el else None,
            "rating": float(rating_el.get_text(strip=True).replace(",", ".")) if rating_el else None,
            "reviews": reviews,
        })

    return results
