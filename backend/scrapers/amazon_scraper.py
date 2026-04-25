"""Amazon.com scraper.

Local dev:  uses Playwright (headless Chrome) to bypass anti-bot.
Production: uses httpx with realistic headers; Amazon may block some requests.
            Set env var USE_PLAYWRIGHT=false to force httpx mode.
"""
import asyncio
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from .utils import clean_price, get_amazon_headers, random_delay, truncate

BASE_URL = "https://www.amazon.com/s?k={query}"
_executor = ThreadPoolExecutor(max_workers=1)

# Detect if we should use Playwright (local) or httpx (production)
USE_PLAYWRIGHT = os.environ.get("USE_PLAYWRIGHT", "true").lower() != "false"


# ---------------------------------------------------------------------------
# Playwright path (local dev)
# ---------------------------------------------------------------------------

def _sync_playwright_fetch(query: str) -> str:
    import asyncio as _asyncio
    loop = _asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_playwright_fetch(query))
    finally:
        loop.close()


async def _playwright_fetch(query: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()
        await page.goto(BASE_URL.format(query=query.replace(" ", "+")), wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(random.uniform(1.5, 2.5))
        html = await page.content()
        await browser.close()
    return html


# ---------------------------------------------------------------------------
# httpx path (production / fallback)
# ---------------------------------------------------------------------------

async def _httpx_fetch(query: str) -> str:
    import httpx
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, http2=True) as client:
        await random_delay(2.0, 4.0)
        resp = await client.get(
            BASE_URL.format(query=query.replace(" ", "+")),
            headers=get_amazon_headers(),
        )
        resp.raise_for_status()
        return resp.text


# ---------------------------------------------------------------------------
# Parser (shared)
# ---------------------------------------------------------------------------

def _parse_items(html: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title_text = title_tag.get_text() if title_tag else ""
    if "robot" in title_text.lower() or len(html) < 10000:
        print("[Amazon] Bot/captcha page")
        return []

    items = soup.select("div[data-component-type='s-search-result']")[:limit]
    results = []

    for item in items:
        h2 = item.find("h2")
        if not h2:
            continue
        title = h2.get("aria-label") or h2.get_text(strip=True)
        if not title:
            continue

        link_el = item.select_one("a[href*='/dp/']") or item.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href", "")
        url = f"https://www.amazon.com{href.split('?')[0]}" if href.startswith("/") else href

        price_whole = item.select_one("span.a-price-whole")
        price_frac = item.select_one("span.a-price-fraction")
        if not price_whole:
            continue

        raw_whole = re.sub(r"[^\d]", "", price_whole.get_text(strip=True))
        raw_frac = re.sub(r"[^\d]", "", price_frac.get_text(strip=True)) if price_frac else "00"
        try:
            price = float(f"{raw_whole}.{raw_frac}")
        except ValueError:
            continue
        if price <= 0:
            continue

        price_outer = item.select_one("span.a-price")
        price_text = price_outer.get_text(strip=True) if price_outer else ""
        currency = "ARS" if ("ARS" in price_text or price > 500) else "USD"

        img_el = item.select_one("img.s-image")
        rating_el = item.select_one("span.a-icon-alt")
        rating = None
        if rating_el:
            try:
                rating = float(rating_el.get_text(strip=True).split()[0].replace(",", "."))
            except (ValueError, IndexError):
                pass

        results.append({
            "title": truncate(title),
            "url": url,
            "source": "amazon",
            "price": price,
            "currency": currency,
            "imagen_url": img_el.get("src") if img_el else None,
            "rating": rating,
            "reviews": None,
        })

    return results


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def search_amazon(query: str, limit: int = 10) -> list[dict]:
    loop = asyncio.get_running_loop()

    for attempt in range(2):
        try:
            if attempt > 0:
                await asyncio.sleep(3)

            if USE_PLAYWRIGHT:
                try:
                    html = await loop.run_in_executor(_executor, _sync_playwright_fetch, query)
                except Exception as pw_err:
                    print(f"[Amazon] Playwright failed: {pw_err} — falling back to httpx")
                    html = await _httpx_fetch(query)
            else:
                html = await _httpx_fetch(query)

            results = _parse_items(html, limit)
            if results:
                return results

        except Exception as e:
            print(f"[Amazon] Attempt {attempt + 1} error: {e}")

    print("[Amazon] No results after retries")
    return []
