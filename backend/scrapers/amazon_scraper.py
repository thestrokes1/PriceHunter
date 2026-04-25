"""Amazon.com scraper using Playwright to bypass anti-bot protection."""
import asyncio
import random
import re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from .utils import clean_price, truncate

BASE_URL = "https://www.amazon.com/s?k={query}"

_executor = ThreadPoolExecutor(max_workers=1)


def _sync_fetch_amazon_html(query: str) -> str:
    """Run Playwright in its own thread+event loop to avoid conflicts with uvicorn."""
    import asyncio as _asyncio
    loop = _asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_fetch_amazon_html_inner(query))
    finally:
        loop.close()


async def _fetch_amazon_html_inner(query: str) -> str:
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
        url = BASE_URL.format(query=query.replace(" ", "+"))
        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(random.uniform(1.5, 2.5))
        html = await page.content()
        await browser.close()
    return html


def _parse_items(html: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")

    # Detect hard bot block (very short page with "robot" in title)
    title_el = soup.find("title")
    title_text = title_el.get_text() if title_el else ""
    if "robot" in title_text.lower() or len(html) < 10000:
        print("[Amazon] Bot/captcha page detected")
        return []

    items = soup.select("div[data-component-type='s-search-result']")[:limit]
    results = []

    for item in items:
        # Title from h2 aria-label (most reliable) or h2 span text
        h2 = item.find("h2")
        if not h2:
            continue
        title = h2.get("aria-label") or h2.get_text(strip=True)
        if not title:
            continue

        # Product link: first /dp/ link in the item
        link_el = item.select_one("a[href*='/dp/']")
        if not link_el:
            link_el = item.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href", "")
        url = f"https://www.amazon.com{href.split('?')[0]}" if href.startswith("/") else href

        # Price
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

        # Currency — Amazon geo-localizes; from Argentina it shows ARS
        price_outer = item.select_one("span.a-price")
        price_text = price_outer.get_text(strip=True) if price_outer else ""
        if "ARS" in price_text or (price > 500 and "$" in price_text[:5]):
            currency = "ARS"
        else:
            currency = "USD"

        # Image
        img_el = item.select_one("img.s-image")

        # Rating
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


async def search_amazon(query: str, limit: int = 10) -> list[dict]:
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError:
        print("[Amazon] playwright not installed — skipping")
        return []

    loop = asyncio.get_running_loop()
    for attempt in range(2):
        try:
            if attempt > 0:
                await asyncio.sleep(3)
            # Run Playwright in its own thread+loop to avoid uvicorn event-loop conflicts
            html = await loop.run_in_executor(_executor, _sync_fetch_amazon_html, query)
            results = _parse_items(html, limit)
            if results:
                return results
        except Exception as e:
            print(f"[Amazon] Attempt {attempt + 1} error: {e}")

    print("[Amazon] No results after retries")
    return []
