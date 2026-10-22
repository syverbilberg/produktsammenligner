"""Approximate performance ranking for processors (CPU) and graphics cards (GPU).

Elkjøp pages state the model ("Intel Core i7 14700F", "GeForce RTX 5070")
but not how fast it is. These tables turn a model into a rough score so the
app can say which is stronger.

The scores are deliberately coarse:
- GPU: relative gaming performance, RTX 4090 = 100 (typical review averages).
- CPU: series + generation + suffix, roughly in line with typical reviews.
A winner is only declared when the gap is clear (see MARGIN), so near-equal
chips end as "Likt" instead of a made-up win. Update the tables when new
models arrive; unknown models simply give no winner.
"""
from __future__ import annotations

import re

import numpy as np

# ------------------------------------------------------------------- GPU
_GPU_INDEX: dict[str, float] = {
    # NVIDIA RTX 50
    "rtx 5090": 130, "rtx 5080": 85, "rtx 5070 ti": 72, "rtx 5070": 58, "rtx 5060 ti": 44,
    "rtx 5060": 38, "rtx 5050": 30,
    # NVIDIA RTX 40
    "rtx 4090": 100, "rtx 4080 super": 78, "rtx 4080": 76, "rtx 4070 ti super": 66, "rtx 4070 ti": 61,
    "rtx 4070 super": 56, "rtx 4070": 48, "rtx 4060 ti": 38, "rtx 4060": 32, "rtx 4050": 26,
    # NVIDIA RTX 30 / 20 / GTX 16
    "rtx 3090 ti": 63, "rtx 3090": 57, "rtx 3080 ti": 55, "rtx 3080": 50, "rtx 3070 ti": 42, "rtx 3070": 39,
    "rtx 3060 ti": 34, "rtx 3060": 26, "rtx 3050": 18, "rtx 2080 ti": 40, "rtx 2080 super": 34, "rtx 2080": 32,
    "rtx 2070 super": 30, "rtx 2070": 26, "rtx 2060 super": 25, "rtx 2060": 21,
    "gtx 1660 super": 17, "gtx 1660 ti": 17, "gtx 1660": 15, "gtx 1650": 11,
    # AMD Radeon
    "rx 9070 xt": 70, "rx 9070": 62, "rx 9060 xt": 40, "rx 7900 xtx": 80, "rx 7900 xt": 68, "rx 7900 gre": 58,
    "rx 7800 xt": 52, "rx 7700 xt": 44, "rx 7600 xt": 32, "rx 7600": 30, "rx 6950 xt": 58, "rx 6900 xt": 55,
    "rx 6800 xt": 52, "rx 6800": 46, "rx 6750 xt": 38, "rx 6700 xt": 36, "rx 6650 xt": 30, "rx 6600 xt": 29,
    "rx 6600": 26, "rx 6500 xt": 13,
    # Intel Arc
    "arc b580": 33, "arc b570": 29, "arc a770": 28, "arc a750": 25, "arc a580": 22, "arc a380": 10,
}
_INTEGRATED = re.compile(r"\b(delt|integrert|integrated|shared|iris|uhd graphics|radeon \d{3}m|arc graphics|"
                         r"adreno|apple gpu)\b|^intel$|^amd$")
_INTEGRATED_SCORE = 6.0
_LAPTOP_FACTOR = 0.75  # laptop versions of the same GPU are clearly slower


def gpu_score(value: str | None) -> float:
    """Rough gaming score for a GPU text, or nan if unknown."""
    if not value:
        return np.nan
    text = re.sub(r"\s+", " ", value.lower().replace("geforce", "").replace("radeon", "").replace("-", " "))
    text = re.sub(r"(rtx|gtx|rx)\s?(\d{4})", r"\1 \2", text)          # "rtx5070" → "rtx 5070"
    text = re.sub(r"(\d{4})\s?(ti|xtx|xt|gre)\b", r"\1 \2", text)      # "5070ti" → "5070 ti"
    best = np.nan
    for model in sorted(_GPU_INDEX, key=len, reverse=True):            # longest first: "5070 ti" before "5070"
        if re.search(rf"\b{re.escape(model)}\b", text):
            best = _GPU_INDEX[model]
            break
    if np.isnan(best):
        bare = re.search(r"\b([2-5]0[5-9]0)(?: (ti|super))?\b", text)  # just "5070" in a name
        if bare:
            best = _GPU_INDEX.get(f"rtx {bare.group(1)}" + (f" {bare.group(2)}" if bare.group(2) else ""), np.nan)
    if np.isnan(best) and _INTEGRATED.search(text):
        return _INTEGRATED_SCORE
    if not np.isnan(best) and re.search(r"laptop|mobile|\bmax-q\b", text):
        best *= _LAPTOP_FACTOR
    return float(best)


# ------------------------------------------------------------------- CPU
_PHONE_CHIPS: dict[str, float] = {
    "snapdragon 8 elite gen 5": 96, "snapdragon 8 elite": 90, "snapdragon 8 gen 3": 82, "snapdragon 8 gen 2": 74,
    "snapdragon 8 gen 1": 65, "snapdragon 8s gen 4": 78, "snapdragon 8s gen 3": 70, "snapdragon 7": 50,
    "snapdragon 6": 38, "snapdragon 4": 28,
    "exynos 2600": 88, "exynos 2500": 84, "exynos 2400": 78, "exynos 2200": 65, "exynos 1580": 48, "exynos 1480": 44,
    "exynos 1380": 38, "dimensity 9500": 94, "dimensity 9400": 88, "dimensity 9300": 80, "dimensity 9200": 72,
    "dimensity 8": 58, "dimensity 7": 44, "dimensity 6": 32,
    "tensor g5": 80, "tensor g4": 70, "tensor g3": 66, "tensor g2": 60,
    "a19 pro": 100, "a19": 95, "a18 pro": 93, "a18": 88, "a17 pro": 85, "a16": 78, "a15": 70,
}


def _intel_core_i(text: str) -> float:
    match = re.search(r"\bi([3579])[\s-]*(\d{4,5})([a-z]*)", text) or re.search(r"\bi([3579])\b.*?\b(\d{4,5})([a-z]*)\b", text)
    if not match:
        bare = re.search(r"\bi([3579])\b", text)
        return {3: 30, 5: 45, 7: 60, 9: 72}[int(bare.group(1))] if bare else np.nan
    tier, number, suffix = int(match.group(1)), match.group(2), match.group(3)
    generation = int(number[:2]) if len(number) == 5 else int(number[0])
    score = {3: 30, 5: 45, 7: 60, 9: 72}[tier] + (generation - 12) * 4
    return score + _suffix(suffix)


def _intel_ultra(text: str) -> float:
    match = re.search(r"ultra\s*([579])[\s-]*(\d{3})?([a-z]*)", text)
    if not match:
        return np.nan
    score = {5: 50, 7: 62, 9: 72}[int(match.group(1))]
    number = match.group(2) or ""
    if number.startswith("2"):
        score += 6                                                    # Series 2 (Arrow/Lunar Lake)
    return score + _suffix(match.group(3))


def _intel_core_n(text: str) -> float:
    match = re.search(r"\bcore\s*([357])[\s-]*(\d{3})?([a-z]*)", text)
    if not match:
        return np.nan
    return {3: 30, 5: 40, 7: 50}[int(match.group(1))] + _suffix(match.group(3))


def _ryzen(text: str) -> float:
    match = re.search(r"\b(?:ryzen|r)\s*(?:ai\s*)?([3579])[\s-]*(?:pro\s*)?(\d{3,4})?([a-z0-9]*)", text)
    if not match:
        return np.nan
    tier, number, suffix = int(match.group(1)), match.group(2) or "", match.group(3)
    score = {3: 30, 5: 46, 7: 60, 9: 74}[tier]
    if "ai" in text:
        generation = 9
    elif len(number) == 4:
        generation = {5: 5, 6: 6, 7: 7, 8: 7, 9: 9}.get(int(number[0]), 7)   # 8000-series is Zen 4, like 7000
    else:
        generation = 7
    score += (generation - 7) * 4
    if "x3d" in suffix or "x3d" in text:
        score += 6                                                    # big gaming cache
    return score + _suffix(suffix.replace("x3d", ""))


def _apple_m(text: str) -> float:
    match = re.search(r"\bm([1-5])\b(?:\s*(pro|max|ultra))?", text)
    if not match:
        return np.nan
    return 50 + (int(match.group(1)) - 1) * 8 + {"pro": 12, "max": 24, "ultra": 36}.get(match.group(2) or "", 0)


def _suffix(suffix: str) -> float:
    """Intel/AMD letters after the model number."""
    suffix = (suffix or "").lower()
    if suffix.startswith("hx"):
        return 3
    if suffix.startswith(("u", "v")):
        return -12
    if suffix.startswith("p"):
        return -6
    if suffix.startswith("k") or suffix == "x":
        return 3
    return 0


def cpu_score(value: str | None) -> float:
    """Rough performance score for a processor text, or nan if unknown."""
    if not value:
        return np.nan
    text = re.sub(r"\s+", " ", value.lower().replace("®", "").replace("™", ""))
    for chip in sorted(_PHONE_CHIPS, key=len, reverse=True):
        if chip in text:
            return float(_PHONE_CHIPS[chip])
    if "ultra" in text and ("intel" in text or "core" in text or re.search(r"\bu[579]\b", text)):
        return _intel_ultra(text.replace("u7-", "ultra 7 ").replace("u5-", "ultra 5 ").replace("u9-", "ultra 9 "))
    if re.search(r"\bu([579])[\s-]\d{3}", text):                        # "U7-265K" from a name
        return _intel_ultra(re.sub(r"\bu([579])", r"ultra \1", text))
    if re.search(r"\bi[3579]\b|\bi[3579][\s-]\d", text):
        return _intel_core_i(text)
    if "ryzen" in text or re.search(r"\br[3579][\s-]", text):
        return _ryzen(text)
    if re.search(r"\bcore\s*[357]\b", text):
        return _intel_core_n(text)
    if "apple" in text or re.search(r"\bm[1-5]\b", text):
        return _apple_m(text)
    return np.nan


# Minimum gap before one chip is called better than another.
MARGIN = {"cpu": 4.0, "gpu": 4.0}
