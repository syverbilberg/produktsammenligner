"""Typical use cases per category, shown in the "Funksjoner og bruk" tab.

Each scenario names the rule keys that decide it (keys from guide.py, plus
"release_year" for all and "generation" where names carry generations).
The product that wins most of those specs wins the scenario; the actual
values are shown as the reason, so nothing is guessed.

`choose_text` completes the sentence "Velg X hvis du …".
Icons: see ICONS in src/ui/components.py.
"""
from __future__ import annotations

from src.models import Scenario


def s(title: str, choose_text: str, keys: tuple[str, ...], icon: str = "star") -> Scenario:
    """Short constructor."""
    return Scenario(title, choose_text, keys, icon)


SCENARIOS: dict[str, tuple[Scenario, ...]] = {
    "mobile": (
        s("Foto og video", "tar mye bilder og video",
          ("camera_count", "ois", "optical_zoom", "aperture", "video", "camera"), "camera"),
        s("Batteri og lading", "vil ha lang batteritid og rask lading",
          ("battery_mah", "battery_life", "fast_charge", "wireless_charge"), "battery"),
        s("Lang levetid", "vil beholde telefonen i mange år",
          ("generation", "updates", "battery_cycles", "ip", "storage"), "shield"),
        s("Spill og tunge apper", "spiller mye eller bruker tunge apper",
          ("processor", "ram", "refresh", "generation"), "bolt"),
    ),
    "tablet": (
        s("Film og strømming", "ser mye film og serier", ("screen_type", "resolution", "refresh", "screen_size"), "screen"),
        s("Skole og notater", "skal skrive notater og jobbe", ("pen", "battery_life", "storage", "ram"), "pen"),
        s("På farten", "bruker nettbrettet mye på farten", ("cellular", "battery_life", "weight"), "battery"),
    ),
    "watch": (
        s("Trening og tur", "trener mye ute", ("gps", "battery_life", "water_resist"), "bolt"),
        s("Helse og søvn", "vil følge med på helse og søvn", ("ecg", "spo2", "sleep"), "heart"),
        s("Uten mobilen", "vil kunne la mobilen ligge hjemme", ("lte", "gps"), "shield"),
    ),
    "headphones": (
        s("Reise og pendling", "reiser og pendler mye", ("anc", "battery_anc", "battery_life"), "volume"),
        s("Trening", "skal bruke dem på trening", ("ip", "battery_life"), "bolt"),
        s("Jobb og samtaler", "har mange samtaler og møter", ("mic", "multipoint"), "users"),
    ),
    "laptop": (
        s("Skole og kontor", "trenger en lett PC til skole og kontor",
          ("battery_life", "weight", "ram", "storage", "fast_charge"), "pen"),
        s("Spill og tunge oppgaver", "spiller eller redigerer bilder/video",
          ("gpu", "processor", "ram", "vram", "refresh"), "bolt"),
        s("Lang levetid", "vil bruke PC-en i mange år", ("ram_max", "release_year", "ram", "storage"), "shield"),
        s("Tilkoblinger", "kobler til skjermer og tilbehør",
          ("hdmi", "thunderbolt", "usbc_pd", "card_reader"), "plug"),
    ),
    "desktop": (
        s("Spill", "spiller nye spill", ("gpu", "vram", "processor", "ram"), "bolt"),
        s("Streaming og videoredigering", "redigerer video eller strømmer spill", ("processor", "cores", "ram", "gpu"), "screen"),
        s("Oppgraderbarhet", "vil kunne oppgradere senere", ("psu", "ram_max", "storage"), "shield"),
    ),
    "monitor": (
        s("Gaming", "spiller mye", ("refresh", "response", "panel"), "bolt"),
        s("Kontor og laptop", "skal koble til en laptop for kontorarbeid", ("usbc_pd", "height_adjust", "resolution"), "plug"),
    ),
    "printer": (
        s("Lave driftskostnader", "skriver ut mye", ("ink_tank", "page_cost"), "leaf"),
        s("Hjemmekontor", "trenger skanner og tosidig utskrift", ("duplex", "scan", "wifi"), "home"),
    ),
    "tv": (
        s("Film i mørkt rom", "ser mye film om kvelden", ("contrast_score", "panel", "dolby_vision", "panel_score"), "screen"),
        s("Lyst rom", "har TV-en i et lyst rom", ("brightness_score", "panel_score"), "sparkle"),
        s("Sport og gaming", "ser sport eller spiller på konsoll",
          ("refresh", "hdmi_standard", "vrr", "allm", "hdmi_count"), "bolt"),
        s("Lyd uten lydplanke", "ikke vil kjøpe lydplanke", ("sound_w", "atmos"), "volume"),
    ),
    "soundbar": (
        s("Filmkveld", "vil ha kinofølelse hjemme", ("atmos", "dtsx", "earc"), "screen"),
        s("Musikk og strømming", "strømmer mye musikk", ("wifi", "airplay", "chromecast", "bluetooth"), "volume"),
    ),
    "gaming": (
        s("Rask og presis", "spiller konkurranse-spill", ("dpi", "weight"), "bolt"),
        s("Plass til spill", "laster ned mange spill", ("storage",), "layers"),
    ),
    "camera": (
        s("Dårlig lys", "fotograferer mye innendørs eller om kvelden", ("sensor", "ibis"), "camera"),
        s("Video", "filmer mye", ("video_res", "ibis"), "camera"),
    ),
    "fridge": (
        s("Stor familie", "har en stor husstand", ("volume", "fridge_volume", "freezer_volume"), "users"),
        s("Åpen kjøkkenløsning", "har åpen kjøkkenløsning", ("noise",), "volume"),
        s("Lave strømutgifter", "vil spare strøm", ("energy",), "leaf"),
        s("Fersk mat lenger", "vil at maten holder seg lenger", ("zero_zone", "nofrost"), "sparkle"),
    ),
    "oven": (
        s("Baking", "baker mye", ("hot_air", "steam", "oven_volume"), "cake"),
        s("Steking av kjøtt", "steker mye kjøtt", ("probe", "steam"), "bolt"),
        s("Enkel rengjøring", "vil slippe å skrubbe ovnen", ("cleaning",), "sparkle"),
        s("Rask platetopp", "lager mye mat på platetoppen", ("hob_type", "booster", "zones", "flex"), "bolt"),
    ),
    "washer": (
        s("Stor familie", "vasker mye tøy", ("capacity_kg", "auto_dose", "programs"), "users"),
        s("Kortere tørketid", "vil ha tørrere tøy etter vask", ("spin",), "clock"),
        s("Lave strømutgifter", "vil spare strøm og vann", ("energy", "energy_year", "water"), "leaf"),
        s("Stille drift", "har vaskemaskinen nær stue eller soverom", ("noise",), "volume"),
    ),
    "dryer": (
        s("Lave strømutgifter", "vil spare strøm", ("heat_pump", "energy", "energy_year"), "leaf"),
        s("Skånsomt for klærne", "vil være skånsom mot tøyet", ("heat_pump", "moisture", "steam"), "sparkle"),
        s("Stor familie", "tørker mye tøy", ("capacity_kg",), "users"),
    ),
    "dishwasher": (
        s("Stille i åpen løsning", "har åpen kjøkkenløsning", ("noise",), "volume"),
        s("Stor husstand", "har mye oppvask", ("place_settings", "cutlery", "basket_adjust"), "users"),
        s("Lave driftskostnader", "vil spare strøm og vann", ("energy", "water"), "leaf"),
        s("Best tørkeresultat", "vil ha tørt servise rett ut av maskinen", ("auto_open",), "sparkle"),
    ),
    "vacuum": (
        s("Store hjem", "har mye gulvflate", ("battery_life", "auto_empty", "navigation", "dust"), "home"),
        s("Allergi og dyrehår", "har allergi eller kjæledyr", ("hepa", "suction"), "heart"),
        s("Gulvvask", "vil at den også vasker gulvet", ("mop", "water_tank", "mop_type"), "sparkle"),
    ),
    "coffee": (
        s("Melkedrikker", "drikker mye cappuccino og latte", ("milk", "frother"), "cup"),
        s("Espresso", "vil ha best mulig espresso", ("grinder", "grind_levels", "pressure"), "cup"),
        s("Lite vedlikehold", "vil bruke lite tid på rengjøring", ("rinse", "brew_group", "descale_alert", "water_tank"), "sparkle"),
    ),
    "kitchen_machine": (
        s("Brød, pizza og tunge gjærdeiger", "baker mye brød og tunge deiger",
          ("motor_power", "dough_capacity", "bowl_volume"), "bread"),
        s("Kaker, marengs og krem", "baker mye kaker og vil ha automatiske programmer",
          ("auto_programs", "speeds", "scale", "timer", "display"), "cake"),
        s("Store bakeprosjekter og flere oppskrifter etter hverandre", "baker store mengder eller flere oppskrifter etter hverandre",
          ("bowls", "bowl_volume", "outlets"), "layers"),
    ),
    "airfryer": (
        s("Middag til familien", "lager mat til flere", ("capacity_l", "baskets"), "users"),
        s("Rask matlaging", "vil ha maten fort på bordet", ("power_w",), "clock"),
        s("Enkel rengjøring", "vil slippe mye oppvask", ("dishwasher_safe", "window"), "sparkle"),
    ),
    "blender": (
        s("Smoothies og is", "lager smoothies og frosne drinker", ("power_w", "ice_crush"), "cup"),
        s("Store porsjoner", "lager mye på én gang", ("jug_volume",), "users"),
    ),
    "kitchen": (
        s("Kraft", "vil ha raske og kraftige resultater", ("power_w",), "bolt"),
        s("Store porsjoner", "lager mye på én gang", ("capacity_l",), "users"),
    ),
    "personal": (
        s("Rask styling", "vil bli raskt ferdig", ("power_w", "temps", "ionic"), "clock"),
        s("Reise og dusj", "vil bruke den på reise eller i dusjen", ("battery_life", "wet_dry"), "battery"),
    ),
    "emobility": (
        s("Lange turer", "kjører langt", ("range", "motor"), "battery"),
        s("Bæres opp trapper", "må bære den ofte", ("weight",), "layers"),
        s("Tyngre fører", "trenger høy maks belastning", ("max_load",), "users"),
    ),
}
