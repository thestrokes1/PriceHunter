"""Fravega scraper via Playwright DOM (Fravega no tiene anti-bot)."""
import re
import asyncio
import random
from bs4 import BeautifulSoup
from .utils import truncate, clean_price

BASE_URL = "https://www.fravega.com"
SEARCH_URL = "https://www.fravega.com/l/?keyword={query}"


async def search_fravega(query: str, limit: int = 10) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            await page.goto(
                SEARCH_URL.format(query=query.replace(" ", "+")),
                wait_until="domcontentloaded",
                timeout=20000,
            )
            # Wait for product articles to appear
            try:
                await page.wait_for_selector("article", timeout=8000)
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.0, 2.0))
            html = await page.content()
            await browser.close()
    except Exception as e:
        print(f"[Fravega] Playwright error: {e}")
        return []

    return _parse(html, limit)


def _parse(html: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select("article")[:limit]
    results = []

    for article in articles:
        link_el = article.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href", "")
        url = f"{BASE_URL}{href}" if href.startswith("/") else href

        # Image
        img_el = article.select_one("img[src]")
        imagen_url = img_el.get("src") if img_el else None

        # Title — first meaningful span text
        title = None
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            if len(txt) > 10 and not txt.startswith("$") and not txt.isdigit():
                title = txt
                break
        if not title:
            continue

        # Price — look for sale price pattern ($999.999)
        price = None
        currency = "ARS"
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            # Match Argentine price format: $1.234.567 or $123.456
            m = re.match(r"^\$[\d.]+$", txt)
            if m:
                raw = txt.replace("$", "").replace(".", "")
                try:
                    candidate = float(raw)
                    # Take the lower price (sale price, not list price)
                    if price is None or candidate < price:
                        price = candidate
                except ValueError:
                    pass

        if not price:
            continue

        results.append({
            "title": truncate(title),
            "url": url,
            "source": "fravega",
            "price": price,
            "currency": currency,
            "imagen_url": imagen_url,
            "rating": None,
            "reviews": None,
        })

    return results
