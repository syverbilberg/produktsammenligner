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
        s("Alt i ett", "vil ha ovn med mikro eller to ovnsrom", ("micro_combo", "oven_count"), "layers"),
    ),
    "washer": (
        s("Stor familie", "vasker mye tøy", ("capacity_kg", "auto_dose", "programs"), "users"),
        s("Kortere tørketid", "vil ha tørrere tøy etter vask", ("spin",), "clock"),
        s("Lave strømutgifter", "vil spare strøm og vann", ("energy", "energy_100", "water", "weight_sensor"), "leaf"),
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
        s("Stort hjem", "har mye gulv å støvsuge", ("runtime", "removable_battery", "dust", "clean_width"), "home"),
        s("Allergi og dyrehår", "har allergi eller kjæledyr", ("hepa", "pet", "suction", "bagless"), "heart"),
        s("Tepper og dyp rengjøring", "har mange tepper", ("suction", "power_w", "dust_sensor"), "bolt"),
    ),
    "robot_vacuum": (
        s("Store hjem", "har mye gulvflate", ("battery_life", "auto_empty", "navigation"), "home"),
        s("Allergi og dyrehår", "har allergi eller kjæledyr", ("hepa", "suction", "obstacle"), "heart"),
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
    "emobility": (
        s("Lange turer", "kjører langt", ("range", "motor"), "battery"),
        s("Bæres opp trapper", "må bære den ofte", ("weight",), "layers"),
        s("Tyngre fører", "trenger høy maks belastning", ("max_load",), "users"),
    ),
    # ------------------------------------------------------------ added v9
    "speaker": (
        s("Fest og utendørs", "skal ha den med ut", ("sound_w", "battery_life", "ip", "stereo_pair"), "volume"),
        s("Hjemme med strømming", "strømmer musikk hjemme", ("wifi", "airplay", "chromecast", "voice"), "home"),
    ),
    "projector": (
        s("Hjemmekino", "ser film i mørkt rom", ("resolution", "contrast", "hdr", "light_source"), "screen"),
        s("Lyst rom", "skal bruke den med litt lys i rommet", ("brightness", "light_source"), "sparkle"),
        s("Liten stue", "har kort avstand til veggen", ("throw",), "home"),
    ),
    "storage": (
        s("Store filer og video", "flytter store filer ofte", ("read_speed", "write_speed", "storage"), "bolt"),
        s("På farten", "tar disken med seg", ("ip", "weight", "encryption"), "shield"),
    ),
    "mouse": (
        s("Gaming", "spiller konkurranse-spill", ("dpi", "polling", "weight"), "bolt"),
        s("Jobb og snarveier", "bruker mange snarveier", ("buttons", "programmable", "battery_life"), "pen"),
    ),
    "keyboard": (
        s("Gaming", "spiller mye", ("polling", "switch", "hotswap"), "bolt"),
        s("Skriving og kontor", "skriver mye", ("layout", "size", "backlight", "battery_life"), "pen"),
    ),
    "router": (
        s("Stor bolig", "har stort hus eller flere etasjer", ("nodes", "mesh", "backhaul", "bands"), "home"),
        s("Mange enheter og gaming", "har mange enheter eller spiller online", ("wifi_std", "wireless_speed", "mu_mimo"), "bolt"),
    ),
    "pc_speaker": (
        s("Mye bass", "vil ha kraftig lyd til spill og film", ("sound_w", "subwoofer", "channels"), "volume"),
        s("Ryddig oppsett", "vil ha få ledninger", ("bluetooth", "connection"), "plug"),
    ),
    "console": (
        s("Mange spill", "laster ned mange spill", ("storage", "edition"), "layers"),
        s("Spill på farten", "vil spille utenfor stua", ("portable", "battery_life"), "battery"),
        s("Best bilde", "har en god 4K-TV", ("max_res", "generation"), "screen"),
    ),
    "controller": (
        s("Konkurransespill", "spiller skytespill eller e-sport", ("paddles", "hall_effect"), "bolt"),
        s("Lange spilløkter", "spiller lenge uten pause", ("battery_life", "connection"), "battery"),
    ),
    "racing": (
        s("Realistisk kjørefølelse", "vil ha mest mulig ekte følelse", ("direct_drive", "torque", "force_feedback"), "bolt"),
        s("Komplett oppsett", "vil ha alt i én pakke", ("pedals", "shifter", "rotation"), "layers"),
    ),
    "streaming_gear": (
        s("Video", "strømmer med kamera", ("resolution", "fps", "webcam_af"), "camera"),
        s("Lyd", "strømmer eller lager podkast", ("polar", "bit_depth"), "volume"),
    ),
    "component": (
        s("Spillytelse", "oppgraderer for spill", ("gpu", "vram", "processor"), "bolt"),
        s("Rom for oppgradering", "vil oppgradere mer senere", ("psu", "recommended_psu"), "shield"),
    ),
    "american_fridge": (
        s("Stor familie", "har en stor husstand", ("fridge_volume", "freezer_volume"), "users"),
        s("Is og kaldt vann", "vil ha is og kaldt vann rett fra døra", ("dispenser", "ice_maker", "water_inlet"), "cup"),
        s("Lave strømutgifter", "vil spare strøm", ("energy", "energy_year", "door_in_door"), "leaf"),
    ),
    "wine_fridge": (
        s("Stor samling", "har mange flasker", ("bottles",), "layers"),
        s("Rødt og hvitt", "drikker både rød- og hvitvin", ("wine_zones", "temp_range"), "cup"),
        s("Lagring over tid", "lagrer vin over lang tid", ("uv_glass", "noise", "wood_shelves"), "shield"),
    ),
    "hob": (
        s("Rask matlaging", "vil ha raskt oppkok", ("hob_type", "boosters", "total_power"), "bolt"),
        s("Store panner og grillplater", "bruker store kjeler og panner", ("flex", "zones", "width"), "layers"),
        s("Smart og trygg", "vil ha hjelp under matlagingen", ("pan_detect", "fry_sensor", "hob2hood", "timer"), "sparkle"),
    ),
    "microwave": (
        s("Rask oppvarming", "varmer mye mat", ("mw_power", "mw_volume"), "clock"),
        s("Mer enn mikro", "vil også grille og steke", ("grill", "hot_air", "auto_programs"), "cake"),
    ),
    "hood": (
        s("Mye matos", "steker og wokker mye", ("airflow", "grease_class", "speeds"), "bolt"),
        s("Stille kjøkken", "har åpen kjøkkenløsning", ("noise_low", "noise_high"), "volume"),
        s("Lave strømutgifter", "vil spare strøm", ("energy", "energy_year"), "leaf"),
    ),
    "washer_dryer": (
        s("Liten plass", "har bare plass til én maskin", ("capacity_kg", "dry_capacity"), "home"),
        s("Tørrere tøy", "vil ha tørrest mulig tøy", ("spin", "dry_capacity"), "clock"),
        s("Lave strømutgifter", "vil spare strøm og vann", ("energy", "energy_100", "water"), "leaf"),
    ),
    "stick_mixer": (
        s("Allsidig", "vil hakke, piske og mose med samme maskin", ("accessories", "chopper", "whisk"), "layers"),
        s("Kraft", "lager mye suppe og smoothie", ("power_w", "speeds", "turbo"), "bolt"),
    ),
    "sandwich": (
        s("Familien", "lager til mange", ("servings", "power_w"), "users"),
        s("Enkel rengjøring", "vil slippe skrubbing", ("removable_plates", "nonstick", "dishwasher_safe"), "sparkle"),
    ),
    "soda": (
        s("Enkel bruk", "vil ha det enkelt", ("electric", "co2_type"), "sparkle"),
        s("Mye brus", "drikker mye kullsyrevann", ("bottles", "carbonation_levels"), "cup"),
    ),
    "capsule": (
        s("Melkedrikker", "drikker mye cappuccino og latte", ("milk", "frother"), "cup"),
        s("Kapselvalg og pris", "vil ha mange kapsler å velge mellom", ("system",), "leaf"),
        s("Store kopper", "drikker store kopper kaffe", ("cup_sizes", "water_tank"), "cup"),
    ),
    "filter_coffee": (
        s("Mange kaffedrikkere", "lager mye kaffe på en gang", ("cups", "capacity_l", "thermos"), "users"),
        s("Best smak", "vil ha best mulig filterkaffe", ("certified", "grinder"), "cup"),
    ),
    "grinder": (
        s("Espresso", "maler til espresso", ("burr", "grind_levels"), "cup"),
        s("Mye kaffe", "maler mye på en gang", ("hopper", "dosing"), "layers"),
    ),
    "toothbrush": (
        s("Sensitivt tannkjøtt", "har sensitive tenner eller tannkjøtt",
          ("pressure_sensor", "smart_sensor", "brush_modes", "intensity"), "heart"),
        s("Hjelp til bedre pussing", "vil ha tilbakemelding på pussingen", ("app", "ai_tracking", "display", "timer"), "sparkle"),
        s("Reise", "reiser mye", ("travel_case", "charging_case", "battery_life", "fast_charger"), "battery"),
    ),
    "shaver": (
        s("Tett barbering", "barberer seg hver dag", ("shaver_type", "flex_head", "sensitive"), "sparkle"),
        s("Lite vedlikehold", "vil slippe rengjøring", ("clean_station", "wet_dry"), "sparkle"),
        s("Reise", "reiser mye", ("battery_life", "travel_case", "charge_time"), "battery"),
    ),
    "hair": (
        s("Rask tørking", "vil bli raskt ferdig", ("power_w", "speeds", "ionic"), "clock"),
        s("Skånsomt for håret", "har tynt eller skadet hår", ("temps", "ionic", "cold_shot"), "heart"),
        s("Krøller og styling", "styler håret mye", ("diffuser", "accessories", "plates"), "sparkle"),
    ),
    "ipl": (
        s("Hele kroppen", "vil behandle store områder", ("flashes", "intensity", "accessories"), "layers"),
        s("Ansikt og sensitive områder", "vil fjerne hår i ansiktet eller bikinilinje",
          ("face", "sensitive_areas", "skin_sensor"), "heart"),
    ),
    "scale": (
        s("Trening og helse", "vil følge med på kroppssammensetning", ("body_analysis", "app"), "heart"),
        s("Hele familien", "skal dele vekten med flere", ("users", "max_load"), "users"),
    ),
    "air_purifier": (
        s("Allergi", "har pollen- eller støvallergi", ("hepa", "cadr", "aq_sensor"), "heart"),
        s("Soverom", "skal ha den på soverommet", ("noise_low", "night_mode"), "volume"),
        s("Stort rom", "skal rense stue eller stort rom", ("room_size", "cadr"), "home"),
    ),
    "dehumidifier": (
        s("Kjeller og hytte", "skal bruke den i kalde rom", ("min_temp", "tech", "drain"), "home"),
        s("Mye fukt", "har mye fukt eller tørker klær inne", ("dehum_capacity", "water_tank", "drain"), "bolt"),
    ),
    "fan": (
        s("Soverom", "skal ha den på soverommet", ("noise", "timer", "remote"), "volume"),
        s("Stort rom", "vil kjøle ned et stort rom", ("power_w", "speeds", "oscillation"), "home"),
    ),
    "heater": (
        s("Lave strømutgifter", "vil spare strøm", ("thermostat_type", "energy_saving", "app"), "leaf"),
        s("Bad og våtrom", "skal varme opp bad eller vaskerom", ("wet_room", "ip"), "home"),
        s("Barnefamilie", "har små barn", ("child_lock", "tip_over"), "shield"),
    ),
    "air_conditioner": (
        s("Varme sommerdager", "vil kjøle ned et rom", ("cool_power", "room_size"), "sparkle"),
        s("Hele året", "vil bruke den både sommer og vinter", ("heating", "dehum_mode"), "home"),
        s("Soverom", "skal bruke den om natten", ("noise", "timer"), "volume"),
    ),
}
