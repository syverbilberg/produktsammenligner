"""Kategoriguiden: which specs matter for which product type."""
from src.categories.detector import detect_category
from src.categories.guide import BY_ID, CATEGORIES

__all__ = ["BY_ID", "CATEGORIES", "detect_category"]
