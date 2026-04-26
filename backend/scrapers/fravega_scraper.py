"""Fravega scraper.

Local:       Playwright (headless Chrome).
Production:  curl_cffi (impersonate Chrome TLS fingerprint) — bypasses Cloudflare.
Fallback:    httpx (may fail on datacenter IPs).
"""
import re
import asyncio
import random
from bs4 import BeautifulSoup
from .utils import truncate, random_delay

BASE_URL = "https://www.fravega.com"
SEARCH_URL = "https://www.fravega.com/l/?keyword={query}"


async def search_fravega(query: str, limit: int = 10) -> list[dict]:
    if _has_playwright():
        html = await _playwright_fetch(query)
    else:
        html = await _curl_fetch(query)
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


async def _curl_fetch(query: str) -> str:
    """curl_cffi primary — bypasses Cloudflare on datacenter IPs."""
    url = SEARCH_URL.format(query=query.replace(" ", "+"))
    await random_delay(0.5, 1.5)
    try:
        from curl_cffi.requests import AsyncSession
        async with AsyncSession() as session:
            resp = await session.get(url, impersonate="chrome124", timeout=12)
            resp.raise_for_status()
            return resp.text
    except ImportError:
        pass
    except Exception as e:
        print(f"[Fravega] curl_cffi error: {e}")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "es-AR,es;q=0.9",
                "Referer": "https://www.fravega.com/",
            })
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        print(f"[Fravega] httpx error: {e}")
        return ""


def _parse_fravega_price(text: str) -> float | None:
    """Parse Argentine price format: $1.624.999,99 → 1624999.99"""
    m = re.match(r"^\$([\d.,]+)$", text.strip())
    if not m:
        return None
    raw = m.group(1)
    # Remove thousand separators (dots), convert decimal comma to dot
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(".", "")
    try:
        return float(raw)
    except ValueError:
        return None


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
            if len(txt) > 10 and not txt.startswith("$") and not re.match(r"^\d+$", txt):
                title = txt
                break
        if not title:
            continue

        # Take the lowest price found in the article (sale price)
        price = None
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            candidate = _parse_fravega_price(txt)
            if candidate and (price is None or candidate < price):
                price = candidate

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
