"""Debug a single product fetch from the terminal.

Usage:  python -m tools.diagnose 457340
        python -m tools.diagnose https://www.elkjop.no/product/.../457340

Shows which URLs were tried, how many specs were found, the detected
category and which guide rules matched. Useful when a varekode fails or a
spec is not picked up – adjust patterns in src/categories/guide.py.
"""
import sys

from src.categories import detect_category
from src.categories.detector import score_categories
from src.comparison.spec_matcher import select_rules
from src.comparison.comparer import value_for
from src.fetching import FetchError, InputError, fetch_product


def main(text: str) -> None:
    try:
        product = fetch_product(text)
    except (InputError, FetchError) as err:
        print(f"FEIL: {err}")
        return

    print(f"Navn:      {product.name}")
    print(f"Varekode:  {product.sku}")
    print(f"URL:       {product.url}")
    print(f"Pris:      {product.price}")
    print(f"Kategori:  {product.category_path}")
    category = detect_category(product)
    print(f"Guide:     {category.name if category else 'IKKE FUNNET'}")
    top = ", ".join(f"{c.name} {score}" for score, c in score_categories(product)[:3])
    print(f"           (poeng: {top})")
    print(f"Beskrivelse: {len(product.description)} tegn")
    print(f"  {product.description[:300]}{'…' if len(product.description) > 300 else ''}")
    print(f"\n{len(product.specs)} spesifikasjoner funnet:")
    for label, value in product.specs.items():
        print(f"  {label}: {value}")

    if category:
        print("\nRegler i guiden:")
        used: set[str] = set()
        rules, _ = select_rules([category])
        for rule in rules:
            value, source = value_for(product, rule, used)
            where = f"  (fra {source})" if source else ""
            print(f"  {'OK ' if value else '-- '} {rule.label}: {value or 'ikke funnet'}{where}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
    else:
        main(sys.argv[1])
