"""Builds fake Elkjøp product pages for offline tests.

Spec labels are copied from a real Elkjøp dishwasher page (Asko DBI8557MIMXXLS).
"""
import json

ASKO_SPECS = {
    "Høyde (cm)": "85.9", "Bredde (cm)": "59.5", "Vekt (kg)": "46.5",
    "Høyde (ink. emballasje)": "93,0 cm",
    "Type oppvaskmaskin": "Underbygd", "Bestikkplassering": "Bestikkurv",
    "Energiklasse": "B", "Lydnivå (dB)": "41", "Kapasitet (antall kuverter)": "15",
    "Antall programmer": "9", "Automatisk åpning": "Ja", "Wi-Fi": "Ja",
    "Produkttype": "Oppvaskmaskin", "Strekkode (EAN)": "3838782628481",
    "Høydejustering på øvre kurv": "Ja",
    "Eco-program vannforbruk (EPWC) i liter pr. syklus": "9.6",
}

OTHER_SPECS = {
    "Høyde (cm)": "81.8", "Bredde (cm)": "59.8",
    "Type oppvaskmaskin": "Helintegrert", "Bestikkplassering": "Bestikkskuff",
    "Energiklasse": "C", "Lydnivå (dB)": "44", "Kapasitet (antall kuverter)": "14",
    "Antall programmer": "6", "Automatisk åpning": "Nei", "Wi-Fi": "Nei",
    "Produkttype": "Oppvaskmaskin",
    "Eco-program vannforbruk (EPWC) i liter pr. syklus": "10.5",
}


def product_page(name: str, price: float, specs: dict[str, str], description: str = "") -> str:
    """HTML with JSON-LD and a grouped spec table, like a product page."""
    json_ld = {
        "@context": "https://schema.org", "@type": "Product", "name": name,
        "brand": {"@type": "Brand", "name": name.split()[0]},
        "image": ["https://example.com/img.jpg"],
        "offers": {"@type": "Offer", "price": price, "priceCurrency": "NOK"},
        "description": description,
    }
    rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in specs.items())
    return (
        "<html><head>"
        f'<script type="application/ld+json">{json.dumps(json_ld)}</script>'
        f"</head><body><h1>{name}</h1><h2>Spesifikasjoner</h2><table>{rows}</table></body></html>"
    )


def search_page(sku: str, path: str) -> str:
    """Search result page whose only product link is embedded in JSON."""
    return f'<html><script>window.__DATA__={{"url":"/product/{path}/{sku}"}}</script></html>'
