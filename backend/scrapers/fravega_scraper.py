"""Fravega scraper — parses __NEXT_DATA__ Apollo state (JSON, no HTML fragility).

Local:       Playwright (headless Chrome).
Production:  curl_cffi (Chrome TLS impersonation, bypasses Cloudflare).
Fallback:    httpx (may fail on datacenter IPs without Argentine geo).
"""
import asyncio
import json
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
    if not html:
        return []
    return _parse_next_data(html, limit) or _parse_articles(html, limit)


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
    from backend.config import settings
    url = SEARCH_URL.format(query=query.replace(" ", "+"))
    proxy = settings.fravega_proxy or None
    await random_delay(0.5, 1.5)
    try:
        from curl_cffi.requests import AsyncSession
        kwargs = dict(impersonate="chrome124", timeout=12)
        if proxy:
            kwargs["proxy"] = proxy
        async with AsyncSession() as session:
            resp = await session.get(url, **kwargs)
            resp.raise_for_status()
            return resp.text
    except ImportError:
        pass
    except Exception as e:
        print(f"[Fravega] curl_cffi error: {e}")
    try:
        import httpx
        client_kwargs = dict(timeout=10, follow_redirects=True)
        if proxy:
            client_kwargs["proxy"] = proxy
        async with httpx.AsyncClient(**client_kwargs) as client:
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


def _parse_next_data(html: str, limit: int) -> list[dict]:
    """Extract products from Next.js Apollo state — reliable JSON, no HTML fragility."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            return []
        data = json.loads(script.string)
        apollo = data["props"]["pageProps"].get("__APOLLO_STATE__", {})
        root = apollo.get("ROOT_QUERY", {})

        items_key = next((k for k in root if k.startswith("items(")), None)
        if not items_key:
            return []
        items = root[items_key]

        results_key = next((k for k in items if k.startswith("results(")), None)
        if not results_key:
            return []
        products = items[results_key][:limit]

    except Exception as e:
        print(f"[Fravega] NEXT_DATA parse error: {e}")
        return []

    results = []
    for p in products:
        title = p.get("title", "").strip()
        if not title:
            continue

        slug = p.get("slug", "")
        url = f"{BASE_URL}/producto/{slug}/" if slug else BASE_URL

        # salePrice.amounts[0].min preferred, fallback to listPrice
        try:
            sale = p.get("salePrice", {})
            list_ = p.get("listPrice", {})
            price = (
                sale.get("amounts", [{}])[0].get("min")
                or list_.get("amounts", [{}])[0].get("min")
            )
            price = float(price)
        except (TypeError, ValueError, IndexError):
            continue
        if not price or price <= 0:
            continue

        # Images are filenames; construct CDN URL
        images = p.get("images") or []
        imagen_url = (
            f"https://images.fravega.com/f300/{images[0]}"
            if images and isinstance(images[0], str)
            else None
        )

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


def _parse_articles(html: str, limit: int) -> list[dict]:
    """Fallback: parse <article> tags from rendered HTML."""
    import re
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
        price = None
        for span in article.find_all("span"):
            txt = span.get_text(strip=True)
            m = re.match(r"^\$([\d.,]+)$", txt.strip())
            if m:
                raw = m.group(1)
                raw = raw.replace(".", "").replace(",", ".") if "," in raw else raw.replace(".", "")
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
