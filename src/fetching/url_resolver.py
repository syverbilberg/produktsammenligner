"""Turns what the user typed (varekode or link) into URLs worth trying.

Elkjøp uses several URL shapes, all handled here:
  /product/hvitevarer/oppvaskmaskin/asko-oppvaskmaskin-dbi8557mimxxls/457340   (category/slug/code)
  /product/hjem-og-husholdning/kjokkenapparater/351830/kenwood-titanium-…     (older: code before slug)
  /product/…/kjokkenmaskin/bosch-universal-kjokkenmaskin-mum6n20a1/MUM6N20A1  (letters in the code)
  /bedrift/product/outlet/bosch-serie-6-vaskemaskin-wgg244fesn-9kg/804466      (business/outlet)
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

BASE_URL = "https://www.elkjop.no"

# A varekode: 4–20 letters/digits (dots allowed), at least one digit, no spaces.
_CODE = re.compile(r"(?=[A-Za-z0-9.]*\d)[A-Za-z0-9.]{4,20}")


class InputError(ValueError):
    """Raised when the input is neither a varekode nor an Elkjøp link."""


def normalize(text: str) -> str:
    """Trim whitespace and add https:// to bare elkjop.no links."""
    text = (text or "").strip()
    if text.lower().startswith(("www.elkjop.no", "elkjop.no")):
        text = "https://" + text
    return text


def is_url(text: str) -> bool:
    """True if the text is an http(s) link."""
    return text.startswith(("http://", "https://"))


def _is_code(segment: str) -> bool:
    """True for a varekode segment ('457340', 'MUM6N20A1'), False for slugs ('asko-oppvask…')."""
    return bool(_CODE.fullmatch(segment)) and "-" not in segment


def _product_segments(url: str) -> list[str]:
    """Path segments after '/product/'."""
    parts = [p for p in urlparse(url).path.split("/") if p]
    if "product" not in parts:
        return []
    return parts[parts.index("product") + 1:]


def _code_index(segments: list[str]) -> int | None:
    """Position of the varekode: the last segment if it is a code, else the first numeric one."""
    if segments and _is_code(segments[-1]):
        return len(segments) - 1
    for i, segment in enumerate(segments):
        if segment.isdigit() and 4 <= len(segment) <= 8:
            return i
    return None


def sku_from_url(url: str) -> str:
    """Extract the varekode from a product URL, or "" if there is none."""
    segments = _product_segments(url)
    index = _code_index(segments)
    return segments[index] if index is not None else ""


def category_from_url(url: str) -> str:
    """Category path without slug and code, e.g. "hvitevarer/oppvaskmaskin"."""
    segments = _product_segments(url)
    index = _code_index(segments)
    if index is None:
        return "/".join(segments[:-1])
    slug = index - 1 if index == len(segments) - 1 else index + 1
    return "/".join(s for i, s in enumerate(segments) if i not in (index, slug))


def candidate_urls(text: str) -> tuple[str, list[str]]:
    """Return (sku, urls to try in order) for a varekode or a link.

    For a varekode we try a direct product URL first and then search pages.
    Search pages are scanned for a link to the product (see product_fetcher).
    """
    text = normalize(text)
    if not text:
        raise InputError("Feltet er tomt.")

    if is_url(text):
        if "elkjop.no" not in text:
            raise InputError("Lenken må være til elkjop.no.")
        return sku_from_url(text), [text]

    code = text.replace(" ", "")
    if not _CODE.fullmatch(code):
        raise InputError(f"«{text}» ser ikke ut som en varekode eller en Elkjøp-lenke.")

    return code, [
        f"{BASE_URL}/product/{code}",
        f"{BASE_URL}/search?SearchTerm={code}",
        f"{BASE_URL}/search?q={code}",
        f"{BASE_URL}/search/{code}",
    ]
