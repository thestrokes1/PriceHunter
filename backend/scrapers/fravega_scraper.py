"""Fravega scraper.

Local:       Playwright (headless Chrome).
Production:  httpx fallback (Fravega has no strong anti-bot).
"""
import re
import asyncio
import random
from bs4 import BeautifulSoup
from .utils import truncate, random_delay, get_ml_headers

BASE_URL = "https://www.fravega.com"
SEARCH_URL = "https://www.fravega.com/l/?keyword={query}"


async def search_fravega(query: str, limit: int = 10) -> list[dict]:
    html = await _playwright_fetch(query) if _has_playwright() else await _httpx_fetch(query)
    return _parse(html, limit) if html else []


def _has_playwright() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


async def _playwright_fetch(query: str) -> str:
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            )
            await page.goto(
                SEARCH_URL.format(query=query.replace(" ", "+")),
                wait_until="domcontentloaded",
                timeout=20000,
            )
            try:
                await page.wait_for_selector("article", timeout=8000)
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.0, 2.0))
            html = await page.content()
            await browser.close()
            return html
    except Exception as e:
        print(f"[Fravega] Playwright error: {e}")
        return ""


async def _httpx_fetch(query: str) -> str:
    try:
        import httpx
        headers = {
            **get_ml_headers(),
            "Accept-Language": "es-AR,es;q=0.9",
            "Referer": "https://www.fravega.com/",
        }
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            await random_delay(0.5, 1.5)
            resp = await client.get(
                SEARCH_URL.format(query=query.replace(" ", "+")),
                headers=headers,
            )
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        print(f"[Fravega] httpx error: {e}")
        return ""


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

        img_el = article.select_one("img[src]")
        imagen_url = img_el.get("src") if img_el else None

        title = None
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            if len(txt) > 10 and not txt.startswith("$") and not txt.isdigit():
                title = txt
                break
        if not title:
            continue

        price = None
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            m = re.match(r"^\$[\d.]+$", txt)
            if m:
                raw = txt.replace("$", "").replace(".", "")
                try:
                    candidate = float(raw)
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
            "currency": "ARS",
            "imagen_url": imagen_url,
            "rating": None,
            "reviews": None,
        })

    return results
