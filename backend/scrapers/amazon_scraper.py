"""Amazon.com scraper with anti-bot mitigations."""
import httpx
from bs4 import BeautifulSoup
from .utils import get_amazon_headers, random_delay, clean_price, truncate

BASE_URL = "https://www.amazon.com/s"


async def search_amazon(query: str, limit: int = 10) -> list[dict]:
    params = {"k": query, "ref": "nb_sb_noss"}
    headers = get_amazon_headers()

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            http2=True,
        ) as client:
            await random_delay(2.0, 4.0)
            resp = await client.get(BASE_URL, params=params, headers=headers)
            resp.raise_for_status()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        print(f"[Amazon] Error fetching: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")

    # Amazon sometimes returns a bot-check page
    if "robot" in resp.text.lower() and len(resp.text) < 5000:
        print("[Amazon] Bot check triggered")
        return []

    items = soup.select("div[data-component-type='s-search-result']")[:limit]
    results = []

    for item in items:
        title_el = item.select_one("h2 a span") or item.select_one("span.a-size-medium")
        price_whole = item.select_one("span.a-price-whole")
        price_fraction = item.select_one("span.a-price-fraction")
        link_el = item.select_one("h2 a")
        img_el = item.select_one("img.s-image")
        rating_el = item.select_one("span.a-icon-alt")
        reviews_el = item.select_one("span.a-size-base[aria-label]")

        if not title_el or not price_whole or not link_el:
            continue

        raw_whole = price_whole.get_text(strip=True).replace(",", "")
        raw_frac = price_fraction.get_text(strip=True) if price_fraction else "00"
        try:
            price = float(f"{raw_whole}.{raw_frac}")
        except ValueError:
            price = clean_price(raw_whole)
        if price is None:
            continue

        href = link_el.get("href", "")
        url = f"https://www.amazon.com{href.split('?')[0]}" if href.startswith("/") else href

        rating_text = rating_el.get_text(strip=True) if rating_el else None
        try:
            rating = float(rating_text.split()[0].replace(",", ".")) if rating_text else None
        except (ValueError, IndexError):
            rating = None

        reviews_text = reviews_el.get("aria-label", "").replace(",", "") if reviews_el else None
        try:
            reviews = int("".join(filter(str.isdigit, reviews_text))) if reviews_text else None
        except ValueError:
            reviews = None

        results.append({
            "title": truncate(title_el.get_text(strip=True)),
            "url": url,
            "source": "amazon",
            "price": price,
            "currency": "USD",
            "imagen_url": img_el.get("src") if img_el else None,
            "rating": rating,
            "reviews": reviews,
        })

    return results
