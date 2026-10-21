"""Varehenting: everything that talks to elkjop.no."""
from src.fetching.product_fetcher import FetchError, fetch_product
from src.fetching.url_resolver import InputError

__all__ = ["FetchError", "InputError", "fetch_product"]
