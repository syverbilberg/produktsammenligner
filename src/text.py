"""Small text helpers shared by several modules."""
from __future__ import annotations

import re

_FOLD = str.maketrans({"æ": "ae", "ø": "o", "å": "a", "Æ": "AE", "Ø": "O", "Å": "A"})


def fold(text: str) -> str:
    """Lowercase and write æøå the way Elkjøp URLs do: 'Kjøkkenmaskin' → 'kjokkenmaskin'."""
    return (text or "").lower().translate(_FOLD)


_UNIT_ALIASES = {
    "watt": "W", "w": "W", "itr": "liter", "ltr": "liter", "l": "liter", "tommer": '"', "gb": "GB", "tb": "TB",
    "minutter": "min", "minutt": "min", "min": "min", "timer": "timer", "t": "timer", "mah": "mAh", "pa": "Pa",
    "db": "dB", "ml": "ml", "kg": "kg", "g": "g", "cm": "cm", "mm": "mm", "hz": "Hz", "wh": "Wh",
}


def unit_of(label: str) -> str:
    """Unit in a label's parentheses, normalised.

    'Motorkraft (Watt)' → 'W' · 'Brukstid når fulladet (minutter)' → 'min' ·
    'Påkrevd ladeeffekt (max. i W)' → 'W' · 'Kapasitet vannbeholder (ml)' → 'ml'
    """
    match = re.search(r"\(([^)]*)\)\s*$", label or "")
    if not match:
        # No parentheses: "Ladetid i timer", "… holdbarhet per syklus i timer og minutter …"
        inline = re.search(r"\bi (timer|minutter|min|watt|kg|liter|ml|cm|mm|gb)\b", (label or "").lower())
        return _UNIT_ALIASES.get(inline.group(1), inline.group(1)) if inline else ""
    unit = match.group(1).strip()
    if " i " in f" {unit} ":
        unit = unit.split(" i ")[-1].strip() if " i " in unit else unit[2:].strip()
    return _UNIT_ALIASES.get(unit.lower(), unit)


def strip_unit(label: str) -> str:
    """'Motorkraft (Watt)' → 'Motorkraft'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", label or "").strip()


def with_unit(value: str, label: str) -> str:
    """Add the label's unit to a bare number: ('1600', 'Motorkraft (W)') → '1600 W'."""
    if value is None:
        return value
    unit = unit_of(label)
    bare_number = re.fullmatch(r"\d+(?:[.,]\d+)?", value.strip())
    if not unit or not bare_number:
        return value
    if unit == '"':
        return f'{value.strip()}"'
    if unit.startswith("antall") or " " in unit or len(unit) > 14:
        return value  # descriptive parentheses, not a unit
    return f"{value.strip()} {unit}"


def decimal_comma(value: str) -> str:
    """'5.5 liter' → '5,5 liter' (Norwegian), leaving '8K UHD (4320p)' and 'Wi-Fi 6' alone."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", value) if re.match(r"^\d+\.\d+(\s|$)", value) else value


def display(value: str | None, label: str, missing: str = "ikke oppgitt") -> str:
    """Value as the customer sees it: ('5.5', 'Bollevolum (liter)') → '5,5 liter'."""
    if value is None:
        return missing
    return decimal_comma(with_unit(value, label))
