"""Thin HTTP layer: one shared session with browser-like headers."""
from __future__ import annotations

from dataclasses import dataclass

import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "nb-NO,nb;q=0.9,no;q=0.8,en;q=0.6",
}

_session = requests.Session()
_session.headers.update(_HEADERS)


@dataclass
class Page:
    """Result of one HTTP request.

    Attributes:
        requested_url: The URL we asked for.
        final_url: The URL after redirects.
        status: HTTP status code (0 if the request failed entirely).
        html: Response body ("" on failure).
        error: Error message when the request failed.
    """

    requested_url: str
    final_url: str
    status: int
    html: str
    error: str = ""

    @property
    def ok(self) -> bool:
        """True for a 2xx response with a body."""
        return 200 <= self.status < 300 and bool(self.html)


def get(url: str, timeout: float = 15) -> Page:
    """GET a URL and never raise; errors are returned in Page.error."""
    try:
        response = _session.get(url, timeout=timeout, allow_redirects=True)
        return Page(url, response.url, response.status_code, response.text)
    except requests.RequestException as err:
        return Page(url, url, 0, "", str(err))
