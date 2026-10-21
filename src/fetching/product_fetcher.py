"""Public entry point for fetching: varekode or link in, Product out."""
from __future__ import annotations

from pathlib import Path

from src.fetching import http_client
from src.fetching.page_parser import find_product_link, looks_like_product_page, parse_product_page
from src.fetching.url_resolver import candidate_urls, category_from_url, sku_from_url
from src.models import Product

DEBUG_DIR = Path(__file__).resolve().parents[2] / "debug"


class FetchError(RuntimeError):
    """Raised when no product page could be found or read."""


def _save_debug(name: str, html: str) -> Path:
    """Save HTML so a failed fetch can be inspected later."""
    DEBUG_DIR.mkdir(exist_ok=True)
    path = DEBUG_DIR / f"{name}.html"
    path.write_text(html, encoding="utf-8")
    return path


def _find_product_page(text: str) -> tuple[str, http_client.Page, list[str]]:
    """Try each candidate URL until one leads to a product page.

    Returns (sku, page, log). Search pages are scanned for a product link,
    which is then fetched.
    """
    sku, urls = candidate_urls(text)
    log: list[str] = []
    last_page: http_client.Page | None = None

    for url in urls:
        page = http_client.get(url)
        last_page = page
        log.append(f"{url} → {page.status or page.error}")
        if not page.ok:
            continue
        if "/product/" in page.final_url and looks_like_product_page(page.html):
            return sku or sku_from_url(page.final_url), page, log
        link = find_product_link(page.html, sku) if sku else ""
        if link:
            product_page = http_client.get(link)
            log.append(f"{link} → {product_page.status or product_page.error}")
            if product_page.ok:
                return sku, product_page, log

    if last_page is not None and last_page.html:
        saved = _save_debug(sku or "ukjent", last_page.html)
        log.append(f"Siste svar lagret i {saved}")
    raise FetchError("Fant ikke produktsiden.\n" + "\n".join(log))


def fetch_product(text: str) -> Product:
    """Fetch and parse one product from a varekode or an Elkjøp link."""
    sku, page, log = _find_product_page(text)
    product = Product(
        sku=sku or sku_from_url(page.final_url),
        url=page.final_url,
        category_path=category_from_url(page.final_url),
    )
    parse_product_page(page.html, product)
    if not product.specs:
        saved = _save_debug(product.sku or "ukjent", page.html)
        raise FetchError(
            "Fant produktsiden, men ingen spesifikasjoner i den.\n"
            + "\n".join(log)
            + f"\nSiden er lagret i {saved}"
        )
    return product
