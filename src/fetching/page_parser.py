"""Reads product info and specs out of an Elkjøp product page's HTML.

The page is read in layers, each filling what the previous one missed:
1. JSON-LD (schema.org Product) – name, price, brand, image, rating.
2. Spec tables (<tr><th/td>…) and definition lists (<dl>).
3. Embedded JSON in <script> tags – label/value pairs.
4. Plain fallbacks – <h1>, og:image, "13 757.-" price text.
"""
from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

from src.models import Product

# Labels that never help a buyer (packaging, ids, registry numbers).
# Matched as whole words: "ean" must not hit "Clean Air Delivery Rate".
_IGNORED_LABEL_WORDS = re.compile(r"\b(emballasje|ean|eprel|artikkelnummer|varenummer)\b")

_LABEL_KEYS = ("label", "name", "key", "title", "attributeName", "displayName")
_VALUE_KEYS = ("value", "displayValue", "attributeValue", "values", "formattedValue")


def _clean(text: str) -> str:
    """Collapse whitespace."""
    return re.sub(r"\s+", " ", text or "").strip()


def _usable_label(label: str) -> bool:
    """Skip empty, absurdly long or useless labels."""
    lower = label.lower()
    return 0 < len(label) <= 90 and not _IGNORED_LABEL_WORDS.search(lower)


def _add_spec(specs: dict[str, str], label: str, value: str) -> None:
    """Add a spec unless it is useless or already present."""
    label, value = _clean(label).rstrip(":"), _clean(value)
    if _usable_label(label) and value and len(value) <= 250:
        specs.setdefault(label, value)


def parse_price(text: str) -> float | None:
    """Parse '13 757.-', '13757,00' or 13757 into a float."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    match = re.search(r"\d[\d\s ]*(?:[.,]\d{1,2})?", str(text))
    if not match:
        return None
    number = re.sub(r"[\s ]", "", match.group()).replace(",", ".")
    try:
        return float(number)
    except ValueError:
        return None


def _read_json_ld(soup: BeautifulSoup, product: Product) -> None:
    """Fill basic fields from schema.org Product data."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or tag.get_text() or "")
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else data.get("@graph", [data])
        for item in candidates:
            if not isinstance(item, dict) or "Product" not in str(item.get("@type")):
                continue
            product.name = product.name or _clean(item.get("name", ""))
            product.description = _clean(BeautifulSoup(item.get("description") or "", "html.parser").get_text(" "))
            brand = item.get("brand")
            product.brand = brand.get("name", "") if isinstance(brand, dict) else str(brand or "")
            image = item.get("image")
            product.image = image[0] if isinstance(image, list) and image else str(image or "")
            offers = item.get("offers")
            if isinstance(offers, list) and offers:
                offers = offers[0]
            if isinstance(offers, dict):
                product.price = parse_price(offers.get("price") or offers.get("lowPrice"))
            rating = item.get("aggregateRating")
            if isinstance(rating, dict) and rating.get("ratingValue"):
                product.rating = float(str(rating["ratingValue"]).replace(",", "."))
                count = rating.get("reviewCount") or rating.get("ratingCount")
                product.review_count = int(count) if str(count or "").isdigit() else None
            return


def _read_tables(soup: BeautifulSoup, specs: dict[str, str]) -> None:
    """Read <tr> rows with two cells and <dl> lists."""
    for row in soup.find_all("tr"):
        cells = row.find_all(["th", "td"], recursive=False) or row.find_all(["th", "td"])
        if len(cells) == 2:
            _add_spec(specs, cells[0].get_text(" "), cells[1].get_text(" "))
    for dl in soup.find_all("dl"):
        for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
            _add_spec(specs, dt.get_text(" "), dd.get_text(" "))


def _walk_json(node: Any, specs: dict[str, str]) -> None:
    """Recursively collect {label: …, value: …} pairs from embedded JSON."""
    if isinstance(node, dict):
        label = next((node[k] for k in _LABEL_KEYS if isinstance(node.get(k), str)), None)
        value = next((node[k] for k in _VALUE_KEYS if k in node), None)
        if isinstance(value, list) and all(isinstance(v, (str, int, float)) for v in value):
            value = ", ".join(str(v) for v in value)
        if label and isinstance(value, (str, int, float)) and not isinstance(value, bool):
            _add_spec(specs, label, str(value))
        for child in node.values():
            _walk_json(child, specs)
    elif isinstance(node, list):
        for child in node:
            _walk_json(child, specs)


def _read_embedded_json(soup: BeautifulSoup, specs: dict[str, str]) -> None:
    """Parse JSON blobs in <script> tags (e.g. __NEXT_DATA__)."""
    for tag in soup.find_all("script"):
        if tag.get("type") == "application/ld+json":
            continue
        text = (tag.string or "").strip()
        if not text.startswith(("{", "[")):
            continue
        try:
            _walk_json(json.loads(text), specs)
        except (json.JSONDecodeError, RecursionError):
            continue


def _fallbacks(soup: BeautifulSoup, product: Product) -> None:
    """Name from <h1>, image from og:image, price from '…,-' text."""
    if not product.name:
        h1 = soup.find("h1")
        og_title = soup.find("meta", property="og:title")
        product.name = _clean(h1.get_text(" ")) if h1 else (og_title or {}).get("content", "")
    if not product.image:
        og_image = soup.find("meta", property="og:image")
        product.image = og_image.get("content", "") if og_image else ""
    if product.price is None:
        meta_price = soup.find("meta", property="product:price:amount")
        if meta_price:
            product.price = parse_price(meta_price.get("content"))
        else:
            match = re.search(r"(\d{1,3}(?:[\s ]\d{3})*)\s*[.,]-", soup.get_text(" "))
            product.price = parse_price(match.group(1)) if match else None


# A JSON string in a <script> that reads like prose (the "Mer informasjon" text
# is often only there, rendered later by JavaScript).
_JSON_STRING = re.compile(r'"((?:[^"\\]|\\.){80,})"')


def _model_tokens(name: str) -> set[str]:
    """Words in a product name that contain a digit ("S25", "WH-1000XM6"),
    used to keep only script text about *this* product."""
    return {w.lower() for w in re.findall(r"[\w-]*\d[\w-]*", name or "") if len(w) >= 2 and not w.isdigit()}


def _script_prose(soup: BeautifulSoup, name: str) -> list[str]:
    """Long prose strings from <script> JSON that mention this product's model.

    Other products (recommendations, accessories) are also in the page data,
    so a string is only kept when it names this product's model.
    """
    tokens = _model_tokens(name)
    if not tokens:
        return []
    found: list[str] = []
    for tag in soup.find_all("script"):
        text = tag.string or tag.get_text() or ""
        for raw in _JSON_STRING.findall(text):
            try:
                value = json.loads(f'"{raw}"')
            except ValueError:
                continue
            value = _clean(BeautifulSoup(value, "html.parser").get_text(" ")) if "<" in value else _clean(value)
            lowered = value.lower()
            if value.count(" ") >= 10 and any(re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", lowered) for t in tokens):
                found.append(value)
    return found


def _read_description(soup: BeautifulSoup, product: Product) -> None:
    """Collect description text: JSON-LD first, then meta tags, then the
    page's description section and paragraphs. Product-page text comes
    before anything else on the page, so the first match is the product's own."""
    parts = [product.description]
    for attrs in ({"name": "description"}, {"property": "og:description"}):
        meta = soup.find("meta", attrs=attrs)
        if meta and meta.get("content"):
            parts.append(meta["content"])
    for element in soup.find_all(class_=re.compile(r"description|beskrivelse", re.I)):
        parts.append(element.get_text(" "))
    for paragraph in soup.find_all("p"):
        parts.append(paragraph.get_text(" "))
    parts += _script_prose(soup, product.name)
    seen, unique = set(), []
    for part in (_clean(p) for p in parts):
        if part and part not in seen:
            seen.add(part)
            unique.append(part)
    product.description = " | ".join(unique)[:20000]


def parse_product_page(html: str, product: Product) -> Product:
    """Fill `product` with everything found in the page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    _read_json_ld(soup, product)
    specs: dict[str, str] = {}
    _read_tables(soup, specs)
    _read_embedded_json(soup, specs)
    product.specs = specs
    _fallbacks(soup, product)
    _read_description(soup, product)
    return product


def find_product_link(html: str, sku: str) -> str:
    """Find a link to /product/…/<sku> on a search page (or in its JSON)."""
    code = re.escape(sku)
    pattern = (rf"(?:https://www\.elkjop\.no)?/product/[^\"'\s<>\\]*?/{code}"
               rf"(?:/[^\"'\s<>\\?#/]+)?(?=[\"'?#\\\s<]|$)")
    match = re.search(pattern, html, flags=re.IGNORECASE)
    if not match:
        return ""
    link = match.group()
    return link if link.startswith("http") else "https://www.elkjop.no" + link


def looks_like_product_page(html: str) -> bool:
    """Heuristic: JSON-LD Product or a 'Spesifikasjoner' section."""
    return '"Product"' in html or "Spesifikasjoner" in html
