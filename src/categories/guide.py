"""The category guide from elkjop_spec_prompt.md, as data.

Each category lists only the specs that matter to a buyer. Patterns are
lowercase regexes matched against the Norwegian spec labels on Elkjøp pages,
tried in order. A matched value must also suit the rule's kind (a number
rule never takes "Ja"), see comparison/value_parser.fit.

Labels confirmed on real Elkjøp pages (Oct 2026) are noted with "seen:".
Elkjøp reuses the same labels across categories, so shared rules are
defined once at the top.

Rule labels carry the unit in parentheses ("Motorkraft (W)"); the UI adds
it to bare numbers. Run `python -m pytest` after any change: the guide is
validated automatically (src/categories/validation.py).

To tune matching: run `python -m tools.diagnose <varekode>` and adjust here.
"""
from __future__ import annotations

from src.categories import dimensions as d
from src.models import Category, SpecRule


def rule(key, label, patterns, kind, dimension, why, order=(), aggregate="first", append=()) -> SpecRule:
    """Short constructor so the tables below stay readable."""
    if isinstance(patterns, str):
        patterns = (patterns,)
    return SpecRule(key, label, tuple(patterns), kind, dimension, why, tuple(order), aggregate, tuple(append))


# ------------------------------------------------------------ universal rules
# Not matched from the page: filled in from the product names (S25 → S26,
# iPhone 16 → 17) by src/comparison/generation.py, only for categories with
# name_generations=True.
GENERATION = rule("generation", "Modellgenerasjon", (), "higher", d.PERFORMANCE,
                  "Nyere generasjon gir som regel raskere prosessor, bedre kamera og lengre oppdateringsstøtte.")

# Added to every category. seen: "Lanseringsår: 2025" (laptop)
RELEASE_YEAR = rule("release_year", "Lanseringsår", (r"^lanseringsår", r"^lanseringsdato", r"^modellår"),
                    "higher", d.LIFESPAN, "Nyere modell får som regel lengre støtte og nyere teknologi.")
UNIVERSAL_RULES = (RELEASE_YEAR,)

# ---------------------------------------------------------------- shared rules
ENERGY = rule("energy", "Energiklasse", r"^energiklasse", "energy", d.ENERGY,
              "Bedre klasse gir lavere strømregning over mange år.")
# seen: "Lydnivå (dB)", "Lydnivå tørk (dB)", "Luftbåren akustisk lydutslipp sentrifugeringsfase (dB)"
NOISE = rule("noise", "Støynivå (dB)", (r"^(lyd|støy)nivå", r"^støy.*db", r"lydnivå", r"lydutslipp(?!-klasse).*\(db\)"),
             "lower", d.NOISE,
             "Under ca. 40 dB er stille nok for åpen kjøkkenløsning.")
# seen: "Prosessortype: Intel Core i7" + "Nummer: 14700F" (desktop/laptop). Phones: "Prosessor"/"Brikkesett".
# Ranked roughly by comparison/hardware.py; near-equal chips give no winner.
PROCESSOR = rule("processor", "Prosessor",
                 (r"^prosessor(modell)?$", r"^prosessortype$", r"^type prosessor$", r"^brikkesett", r"^chipset$",
                  r"^prosessor \(", r"^cpu"),
                 "cpu", d.PERFORMANCE,
                 "Bestemmer hvor raskt alt føles. Rangert omtrentlig etter serie og generasjon – små forskjeller teller ikke.",
                 append=(r"^nummer$", r"^prosessornummer"))
# seen: "Type prosessor: Snapdragon 8 Elite for Galaxy" (S25 phone page).
# seen: "Internminne/RAM (GB): 16" (laptop). Phones often lack it (then: from the name "12/256GB").
RAM = rule("ram", "RAM (GB)",
           (r"internminne/ram", r"^(ram|arbeidsminne|systemminne|minne)( \(gb\))?$", r"^ram-?størrelse", r"^ram \(gb\)"),
           "higher", d.PERFORMANCE, "Mer RAM gir bedre multitasking og lengre levetid.")
# seen: "Intern lagring (GB): 256" (phone), "Total lagringskapasitet (GB): 512" (laptop)
STORAGE = rule("storage", "Lagring (GB)",
               (r"^intern lagring", r"^total lagringskapasitet", r"^lagringskapasitet( \(gb\))?$", r"^total ssd kapasitet",
                r"^lagringskapasitet ssd", r"^harddiskkapasitet", r"^lagring( \(gb\))?$"),
               "higher", d.CAPACITY, "Plass til bilder, video, apper og spill.")
# seen: "Størrelse (tommer): 6.3" (phone), "Størrelse (tommer): 14" (laptop)
SCREEN_SIZE = rule("screen_size", "Skjermstørrelse (tommer)",
                   (r"^skjermstørrelse", r"^størrelse \(tommer\)", r"skjermdiagonal", r"^diagonal"),
                   "info", d.DISPLAY, "Smak og bruk avgjør – større er ikke alltid bedre.")
# seen: "Oppløsningsstandard: Full HD (1080p)", "Maks oppløsning: 1920x1080", "Skjermoppløsning (i piksler)"
RESOLUTION = rule("resolution", "Oppløsning",
                  (r"^oppløsningsstandard", r"^skjermoppløsning", r"^maks oppløsning", r"^oppløsning$"),
                  "info", d.DISPLAY, "Høyere oppløsning gir skarpere bilde.")
# seen: "Oppdateringsfrekvens: 120"
# seen: "Oppdateringsfrekvens: 120" (phone/laptop), "Bildepanelfrekvens (Hz): 120" (TV)
REFRESH = rule("refresh", "Oppdateringsfrekvens (Hz)",
               (r"^oppdateringsfrekvens", r"^bildepanelfrekvens", r"^bildefrekvens", r"^refresh"),
               "higher", d.DISPLAY, "Høyere Hz gir jevnere bevegelser i spill, sport og scrolling.")
# seen: "Nit: 250" (laptop)
BRIGHTNESS = rule("brightness", "Lysstyrke (nits)", (r"^nits?$", r"^lysstyrke(?!.*score)", r"cd/m", r"ansi"),
                  "higher", d.DISPLAY, "Lysere skjerm er lettere å se i sollys og gir bedre HDR.")
# seen: "Display: OLED" (phone), "Display: SVA" / "Displayteknologi: SVA" (laptop)
DISPLAY_TYPE = rule("screen_type", "Skjermtype",
                    (r"^display$", r"^displayteknologi", r"^skjermtype", r"^skjermteknologi$", r"^paneltype"),
                    "rank", d.DISPLAY, "OLED gir best kontrast og farger; IPS er gode LCD-skjermer.",
                    ("oled", "mini led", "ips", "va", "lcd", "tn"))
# seen: "Leverandørens oppgitte batterilevetid opptil (timer): 7.5" (laptop),
#       "Batteriets holdbarhet per syklus i timer og minutter per full batterilading: 51" (phone)
BATTERY_LIFE = rule("battery_life", "Batteritid",
                    (r"batterilevetid", r"holdbarhet per syklus", r"^batteritid(?!.*stand ?by)", r"spilletid",
                     r"^musikkavspillingstid(?!.*anc)", r"avspillingstid(?!.*anc)", r"^brukstid", r"driftstid"),
                    "higher", d.BATTERY, "Hvor lenge den varer mellom hver lading.")
# seen: "Batteriets holdbarhet i sykluser: 2700" (phone, EU label)
BATTERY_CYCLES = rule("battery_cycles", "Batteriets levetid (ladesykluser)", r"holdbarhet i sykluser",
                      "higher", d.LIFESPAN, "Hvor mange fulle ladinger batteriet tåler før det svekkes merkbart.")
# seen: "Påkrevd ladeeffekt (min. i W): 10" and "Påkrevd ladeeffekt (max. i W): 25" – we want max.
FAST_CHARGE = rule("fast_charge", "Maks ladeeffekt (W)",
                   (r"ladeeffekt \(max", r"^maks\w* ladeeffekt",
                    r"^(?!.*(trådløs|min\.|minimum)).*(ladeeffekt|hurtiglading \(w|ladehastighet)"),
                   "higher", d.BATTERY, "Høyeste effekt den tåler med kabel – mer gir raskere lading.", aggregate="max")
# seen: "Ladeenhet inkludert: Nei" (phone), "Ja" (laptop)
CHARGER = rule("charger", "Lader følger med", (r"^ladeenhet inkludert", r"lader (inkludert|medfølger)", r"inkludert lader"),
               "yes", d.FEATURES, "Uten lader må du regne med å kjøpe en i tillegg.")
# seen: "Vekt (kg): 1.4"
WEIGHT = rule("weight", "Vekt (kg)", (r"^vekt \(kg\)", r"^vekt$", r"^vekt \(g\)"), "lower", d.PORTABILITY,
              "Lettere er enklere å ta med seg.")
WIFI = rule("wifi", "Wi-Fi", (r"^wi-?fi$", r"^wi-?fi", r"trådløst nettverk"), "yes", d.CONNECTIVITY,
            "Styring og oppdateringer via app/nett.")
BLUETOOTH = rule("bluetooth", "Bluetooth", r"^bluetooth", "yes", d.CONNECTIVITY,
                 "Trådløs tilkobling til mobil og andre enheter.")
UPDATES = rule("updates", "Programvareoppdateringer (år)",
               (r"programvareoppdatering", r"sikkerhetsoppdatering", r"os-oppdatering", r"os-versjonoppdatering", r"^oppdateringer"),
               "higher", d.LIFESPAN, "Flere års oppdateringer = tryggere og lengre levetid.")
# seen: "IP-klassifisering: IP68"
IP_RATING = rule("ip", "Vann-/støvtetthet", (r"^ip-?klass", r"vanntett", r"^vannresist", r"\bip\d"),
                 "rank", d.DURABILITY, "Tåler vann og støv – viktig for uhell og utebruk.",
                 ("ip68", "ip67", "ipx7", "ip65", "ipx5", "ip54", "ipx4"))
TOUCH = rule("touch", "Berøringsskjerm", (r"^touch-?skjerm", r"berøringsskjerm"), "yes", d.FEATURES,
             "Kan styres med fingrene.")
ATMOS = rule("atmos", "Dolby Atmos", r"dolby atmos", "yes", d.SOUND, "Gir lyd fra flere retninger, også ovenfra.")
PROGRAMS = rule("programs", "Antall programmer", (r"^antall (programmer|funksjoner)",), "higher", d.FEATURES,
                "Flere programmer gir mer fleksibilitet, men de fleste bruker 2–3.")
POWER = rule("power_w", "Effekt (W)", (r"^effekt( \(w(att)?\))?$", r"^motorkraft", r"^motoreffekt", r"^maks(imal)? effekt",
                                      r"^total effekt", r"^watt"),
             "higher", d.PERFORMANCE, "Mer effekt gir raskere og kraftigere resultat.")
DISHWASHER_SAFE = rule("dishwasher_safe", "Tåler oppvaskmaskin", (r"oppvaskmaskin(sikker|trygg)", r"tåler oppvaskmaskin"),
                       "yes", d.FEATURES, "Enklere rengjøring.")
# seen: "Grafikkløsning (Modell): GeForce RTX 5070" (desktop), "Arkitektur grafikkort: Delt" (laptop, integrated)
GPU = rule("gpu", "Grafikkort",
           (r"^grafikkløsning", r"^grafikkort$", r"^grafikkortmodell", r"^gpu-?modell", r"^grafikkprosessor",
            r"^arkitektur grafikkort", r"^hovedmerke \(gpu\)"),
           "gpu", d.PERFORMANCE,
           "Viktigst for spill og video. Rangert etter omtrentlig spillytelse – samme modell fra ulike merker yter likt.")
# seen: "Dedikert videominne: 12"
VRAM = rule("vram", "Grafikkminne (GB)", (r"^dedikert videominne", r"^grafikkminne", r"vram", r"grafikk.*minne"),
            "higher", d.PERFORMANCE, "8 GB er minimum for nye spill, 12 GB+ anbefales.")
CORES = rule("cores", "Prosessorkjerner", r"^antall prosessorkjerner", "higher", d.PERFORMANCE,
             "Flere kjerner hjelper ved tunge oppgaver som video og mange programmer samtidig.")
RAM_MAX = rule("ram_max", "Maks RAM etter oppgradering (GB)", r"^maksimalt støttet minne", "higher", d.LIFESPAN,
               "Hvor mye RAM PC-en kan oppgraderes til senere.")
# seen: "Forbruk, kWh/år: 194" (dryer)
ENERGY_YEAR = rule("energy_year", "Strømforbruk (kWh/år)",
                   (r"kwh/år", r"kwh per år", r"årlig energiforbruk", r"energiforbruk.*\(kwh/år\)"),
                   "lower", d.ENERGY, "Lavere årlig forbruk gir lavere strømregning.")

# --------------------------------------------------- more shared rules (v9)
# seen on Samsung Bespoke Jet: "Brukertid, minimumskapasitet (min): 60" and "…makskapasitet (min): 3"
# – the longest runtime (lowest power) is the one buyers compare, so max.
RUNTIME = rule("runtime", "Brukstid per lading (min)", (r"^brukertid", r"^brukstid", r"^driftstid", r"^batteritid(?!.*stand ?by)"),
               "higher", d.BATTERY, "Lengste brukstid på laveste effekt – på full effekt er den mye kortere.", aggregate="max")
# seen: "Ladetid i timer: 3.5", "Ladetid i minutter: 60", "Ladetid (timer): 3.5"
CHARGE_TIME = rule("charge_time", "Ladetid", r"^ladetid", "lower", d.BATTERY, "Kortere ladetid betyr mindre venting.")
# seen: "Antall hastigheter: 3", "Antall velgbare hastigheter: 3", "Vifteinnstillinger: 3", "Antall instillinger: 4"
SPEEDS = rule("speeds", "Hastighetstrinn", (r"^antall (velgbare )?hastigheter", r"^vifteinnstillinger", r"^hastighet\w*innstillinger",
                                            r"^antall in?stillinger", r"^hastighetstrinn"),
              "higher", d.FEATURES, "Flere trinn gir bedre kontroll.")
# seen: "Anbefalt romstørrelse (maks kvm): 40"
ROOM_SIZE = rule("room_size", "Anbefalt romstørrelse (m²)", (r"^anbefalt romstørrelse", r"romstørrelse"), "higher", d.CAPACITY,
                 "Bør være minst like stort som rommet den skal stå i.")
# seen: "Lydnivå, Lav (dB): 26", "Lydnivå, Høy (dB): 49"
NOISE_LOW = rule("noise_low", "Støy på laveste trinn (dB)", r"lydnivå, lav", "lower", d.NOISE,
                 "Det du hører om natten eller når den står og går i bakgrunnen.")
NOISE_HIGH = rule("noise_high", "Støy på høyeste trinn (dB)", r"lydnivå, høy", "lower", d.NOISE,
                  "Støy når den jobber for fullt.")
# seen: "Tilgjengelig app: Nei" (air purifier). "Navn på tilgjengelig app" is left out on purpose:
# Elkjøp lists it also for toothbrushes without Bluetooth.
APP = rule("app", "App-styring", (r"^tilgjengelig app$", r"^app-?styring", r"^app$", r"^appstyrt", r"^bluetooth$"),
           "yes", d.CONNECTIVITY, "Styr og følg med fra mobilen.")
# seen: "Tidskontroll: Ja"
TIMER = rule("timer", "Timer", (r"^tidskontroll", r"^timer", r"tidsur"), "yes", d.FEATURES, "Slår seg av eller sier fra av seg selv.")
SCREEN_YES = rule("display", "Display", (r"^skjerm$", r"^display$", r"berøringsskjerm", r"^touch"), "yes", d.FEATURES,
                  "Viser innstillinger og status tydelig.")
TRAVEL_CASE = rule("travel_case", "Reiseetui", r"^reiseetui", "yes", d.PORTABILITY, "Enklere å ta med på reise.")
WIFI_STD = rule("wifi_std", "Wi-Fi-standard", (r"^wifi-standard", r"^wi-fi-standard"), "rank", d.CONNECTIVITY,
                "Nyere Wi-Fi gir raskere og mer stabilt nett.", ("wi-fi 7", "wi-fi 6e", "wi-fi 6", "wi-fi 5"))
ACCESSORIES = rule("accessories", "Antall tilbehør", (r"^antall medfølgende tilbehør", r"^antall tilbehør"), "higher", d.FEATURES,
                   "Mer tilbehør gir flere bruksområder.")
THERMOSTAT = rule("thermostat", "Justerbar temperatur", (r"justerbar temperatur", r"^termostat$", r"temperaturkontroll",
                                                         r"temperaturinnstilling"),
                  "yes", d.FEATURES, "Riktig temperatur til ulike formål.")
AUTO_OFF = rule("auto_off", "Auto-av", (r"^auto-?av", r"automatisk avslåing", r"skrur seg automatisk av"), "yes", d.FEATURES,
                "Tryggere og sparer strøm.")
CORDLESS = rule("cordless", "Trådløs", (r"^trådløs$", r"^ledningsfri"), "yes", d.PORTABILITY, "Ingen ledning i veien.")
MAX_LOAD = rule("max_load", "Maks belastning (kg)", (r"^maks.*(last|brukervekt|belastning)", r"^maks(imal)? vekt", r"^veiekapasitet"),
                "higher", d.CAPACITY, "Hvor tungt den tåler.")
SOUND_W = rule("sound_w", "Lydeffekt (W)", (r"^lydeffekt", r"utgangseffekt", r"høyttalereffekt", r"^total effekt \(rms",
                                             r"^effekt \(rms"),
               "higher", d.SOUND, "Mer effekt gir høyere lyd uten forvrengning – men kvalitet betyr mer enn watt.")
FUSE = rule("fuse", "Sikring", (r"^sikring", r"ampere"), "info", d.FEATURES, "Sjekk at sikringen hjemme passer (f.eks. 16A vs 2x16A).")
INSTALL = rule("install", "Plassering", (r"^plassering$", r"^installasjon", r"^monteringstype", r"^installasjonstype"), "info",
               d.FEATURES, "Frittstående eller integrert – må passe kjøkkenet.")

# ------------------------------------------------------------------ categories
# One category per subgroup in Elkjøp's own product tree (MDA, SDA, Computing,
# Gaming, mobile, TV/audio). Each lists what a buyer actually compares, most
# important first. Which tab a category belongs to: src/categories/groups.py.
CATEGORIES: tuple[Category, ...] = (
    # ================================================================ MOBIL
    # seen on Google Pixel 9: "Type prosessor: Tensor G4", "Garanterte OS-versjonoppdateringer til minst: 7 years"
    Category("mobile", "Mobiltelefoner", ("mobiltelefon", "smarttelefon", "iphone", "mobil"),
             always_ask=(d.CAMERA,), name_generations=True, rules=(
        PROCESSOR, RAM, STORAGE,
        rule("battery_mah", "Batterikapasitet (mAh)", (r"^batterikapasitet", r"mah"), "higher", d.BATTERY,
             "Større batteri gir som regel lengre batteritid, men prosessor og skjerm påvirker også forbruket."),
        FAST_CHARGE,
        rule("wireless_charge", "Trådløs lading", r"^trådløs lading$", "yes", d.BATTERY, "Praktisk – legg den på laderen."),
        BATTERY_LIFE, BATTERY_CYCLES,
        DISPLAY_TYPE, SCREEN_SIZE, REFRESH, BRIGHTNESS,
        rule("camera_count", "Antall kameraer", r"^antall kameraer", "higher", d.CAMERA,
             "Flere kameraer gir flere valg: vidvinkel, zoom og ultravidvinkel."),
        rule("camera", "Hovedkamera (MP)", (r"^bakkamera 1.*(mp|oppløsning|megapiksel)", r"^hovedkamera", r"^bakre kamera"),
             "info", d.CAMERA, "Megapiksler sier lite alene – se på sensor, blender og zoom."),
        rule("ois", "Optisk bildestabilisering", (r"^bakkamera 1.*stabilis", r"optisk bildestabilis", r"\bois\b"), "yes", d.CAMERA,
             "Skarpere bilder i dårlig lys og roligere video."),
        rule("aperture", "Blenderåpning (hovedkamera)", (r"^bakkamera 1.*blender", r"^blender"), "lower", d.CAMERA,
             "Lavere tall (f/1.8 eller under) slipper inn mer lys – bedre bilder om kvelden."),
        rule("optical_zoom", "Optisk zoom (x)", r"optisk zoom", "higher", d.CAMERA,
             "Ekte zoom uten tap av kvalitet – nyttig for portretter og avstand."),
        rule("video", "Video", (r"^opptaksoppløsning", r"^videooppløsning", r"^videoopptak"), "info", d.CAMERA,
             "4K 60 fps gir skarp og jevn video."),
        UPDATES, IP_RATING,
        rule("5g", "5G", r"^5g", "yes", d.FEATURES, "Raskere mobilnett der det er dekning."),
        rule("esim", "eSIM", r"esim", "yes", d.FEATURES, "Bytt abonnement uten fysisk SIM-kort."),
        rule("nfc", "NFC (mobilbetaling)", r"\bnfc\b", "yes", d.FEATURES, "Betal med telefonen."),
        CHARGER,
    )),
    Category("watch", "Smartklokker og aktivitetsarmbånd",
             ("smartklokke", "aktivitetsarmbånd", "smartwatch", "apple watch", "treningsklokke", "pulsklokke"),
             name_generations=True, rules=(
        rule("compatibility", "Kompatibilitet", (r"kompatib", r"operativsystem"), "info", d.CONNECTIVITY,
             "Sjekk at klokka fungerer med telefonen kunden har."),
        BATTERY_LIFE, SCREEN_SIZE, DISPLAY_TYPE,
        rule("ecg", "EKG", (r"\bekg\b", r"\becg\b"), "yes", d.FEATURES, "Kan oppdage uregelmessig hjerterytme."),
        rule("spo2", "Blodoksygen (SpO2)", (r"spo2", r"oksygen"), "yes", d.FEATURES, "Måler oksygennivå i blodet."),
        rule("sleep", "Søvnmåling", r"søvn", "yes", d.FEATURES, "Følger med på søvnkvalitet."),
        rule("gps", "GPS", (r"\bgps\b", r"^posisjoneringssystem"), "yes", d.FEATURES, "Måler tur og løp uten mobilen."),
        rule("lte", "LTE/eSIM", (r"\blte\b", r"esim", r"^mobilnett"), "yes", d.CONNECTIVITY, "Ring og bruk data uten mobilen."),
        rule("water_resist", "Vanntetthet", (r"vanntett", r"\batm\b", r"vannmotstand", r"vannavvis", r"^ip-?klass"), "rank", d.DURABILITY,
             "5 ATM eller mer for svømming.", ("10 atm", "5 atm", "ip68", "3 atm")),
        rule("payment", "Betaling med klokka", (r"\bnfc\b", r"betaling", r"\bpay\b"), "yes", d.FEATURES, "Betal uten mobil og kort."),
        WEIGHT,
    )),
    # ============================================================ TV OG LYD
    # seen on LG 65" B5: Panelteknologi, Bildepanelfrekvens (Hz), HDMI-standard, VRR, ALLM, Elkjøp's panel scores.
    Category("tv", "TV", ("tv", "oled-tv", "fjernsyn", "qled"), rules=(
        rule("panel", "Skjermteknologi",
             (r"^panelteknologi", r"^skjermteknologi", r"^paneltype", r"^displayteknologi", r"^display$"), "rank",
             d.DISPLAY, "OLED gir perfekt svart; Mini LED/QLED er lysere for lyse rom.",
             ("oled", "mini led", "neo qled", "qned", "qled", "led")),
        rule("panel_score", "Elkjøps panelscore (0–10)", r"^panelscore", "higher", d.DISPLAY,
             "Elkjøps samlede vurdering av bildet."),
        rule("contrast_score", "Kontrast (score)", r"^kontrast ?score", "higher", d.DISPLAY, "Høy score = dyp svart, viktig i mørkt rom."),
        rule("brightness_score", "Lysstyrke (score)", r"^lysstyrke ?score", "higher", d.DISPLAY, "Høy score = godt bilde i lyse rom."),
        rule("color_score", "Fargegjengivelse (score)", r"^fargegjengivelse", "higher", d.DISPLAY, "Naturlige og riktige farger."),
        SCREEN_SIZE, RESOLUTION, REFRESH,
        rule("hdr_formats", "HDR-formater", (r"high dynamic range \(hdr\) standard", r"^hdr-standard", r"^hdr-format"), "info",
             d.DISPLAY, "Dolby Vision og HDR10+ gir best HDR fra strømmetjenester."),
        rule("dolby_vision", "Dolby Vision", r"dolby vision", "yes", d.DISPLAY, "Bedre HDR på Netflix, Disney+ osv."),
        rule("hdmi_count", "Antall HDMI-innganger", r"^antall hdmi", "higher", d.CONNECTIVITY, "Plass til konsoll, lydplanke og dekoder."),
        rule("hdmi_standard", "HDMI-standard", r"^hdmi-standard", "rank", d.CONNECTIVITY, "HDMI 2.1 trengs for PS5/Xbox i 4K 120 Hz.",
             ("2.1", "2.0", "1.4")),
        rule("vrr", "VRR", (r"\bvrr\b", r"variabel oppdatering"), "yes", d.FEATURES, "Jevnere bilde i spill."),
        rule("allm", "Automatisk spillmodus (ALLM)", (r"\ballm\b", r"auto low latency"), "yes", d.FEATURES,
             "TV-en bytter selv til lav forsinkelse når konsollen starter."),
        rule("platform", "Smart-TV-plattform", (r"^smart-?\s?tv-plattform", r"^operativsystem", r"^plattform"), "info",
             d.FEATURES, "Google TV, Tizen eller webOS – bestemmer apper og brukervennlighet."),
        SOUND_W, ATMOS, ENERGY, ENERGY_YEAR,
    )),
    Category("soundbar", "Lydplanker", ("lydplanke", "soundbar"), rules=(
        rule("channels", "Kanaler", (r"^kanaler", r"kanalkonfig", r"^antall kanaler"), "info", d.SOUND,
             "Flere kanaler gir mer surround; «.2» på slutten = lyd ovenfra."),
        SOUND_W, ATMOS,
        rule("dtsx", "DTS:X", r"dts:?x", "yes", d.SOUND, "Alternativ surroundformat."),
        rule("subwoofer", "Subwoofer", (r"subwoofer", r"basselement"), "info", d.SOUND, "Egen subwoofer gir mye mer bass."),
        rule("earc", "HDMI eARC", (r"earc", r"hdmi arc"), "yes", d.CONNECTIVITY, "Den beste og enkleste koblingen til TV-en."),
        WIFI, BLUETOOTH,
        rule("airplay", "AirPlay", r"airplay", "yes", d.CONNECTIVITY, "Strøm lyd fra Apple-enheter."),
        rule("chromecast", "Chromecast", r"chromecast", "yes", d.CONNECTIVITY, "Strøm lyd fra Android/apper."),
    )),
    Category("speaker", "Høyttalere", ("høyttaler", "hoyttaler", "bluetooth-høyttaler", "smarthøyttaler", "partyhøyttaler"), rules=(
        SOUND_W, BATTERY_LIFE, IP_RATING, BLUETOOTH, WIFI,
        rule("airplay", "AirPlay", r"airplay", "yes", d.CONNECTIVITY, "Strøm lyd fra Apple-enheter."),
        rule("chromecast", "Chromecast", r"chromecast", "yes", d.CONNECTIVITY, "Strøm lyd fra Android/apper."),
        rule("stereo_pair", "Kan pares (stereo/party)", (r"stereopar", r"party ?modus", r"pare", r"multiroom"), "yes", d.SOUND,
             "Koble to eller flere sammen for større lyd."),
        rule("voice", "Stemmestyring", (r"stemmestyring", r"talekontroll", r"alexa", r"google assistant", r"siri"), "yes",
             d.FEATURES, "Styr musikken med stemmen."),
        rule("mic", "Mikrofon/høyttalertelefon", r"^mikrofon", "yes", d.FEATURES, "Kan brukes til samtaler."),
        WEIGHT,
    )),
    Category("headphones", "Hodetelefoner og øreplugger",
             ("hodetelefon", "øreplugg", "airpods", "earbuds", "øretelefon", "headset", "gaming-headset"), name_generations=True, rules=(
        rule("type", "Type", (r"^hodetelefontype", r"^bæremåte", r"^formfaktor", r"^type hodetelefon"), "info", d.FEATURES,
             "In-ear, on-ear eller over-ear – handler om komfort og bruk."),
        # seen on Sony WH-1000XM6: "Aktiv støykansellering", "Musikkavspillingstid med ANC på (timer)"
        rule("anc", "Aktiv støydemping (ANC)", (r"aktiv støy(demping|kansellering)", r"støydemping", r"støykansellering",
                                                r"\banc\b", r"støyreduksjon"), "yes", d.SOUND,
             "Demper fly-, buss- og kontorstøy."),
        rule("battery_anc", "Batteritid med ANC", r"avspillingstid med anc", "higher", d.BATTERY,
             "Den reelle batteritiden når støydempingen er på."),
        BATTERY_LIFE,
        rule("hires", "Lydkvalitet", r"^audio-støtte", "info", d.SOUND, "Hi-Res Audio gir mer detaljer med riktig telefon og kodek."),
        rule("codec", "Kodek", (r"kodek", r"codec"), "info", d.SOUND,
             "Bestemmer lydkvaliteten over Bluetooth – avhenger av hvilken telefon kunden har."),
        rule("multipoint", "Multipoint", (r"multipoint", r"flerpunkt"), "yes", d.CONNECTIVITY,
             "Koblet til PC og mobil samtidig."),
        rule("mic", "Mikrofon", r"^mikrofon", "yes", d.FEATURES, "For samtaler og møter."),
        IP_RATING, WEIGHT,
    )),
    Category("projector", "Projektorer", ("projektor", "prosjektor", "projector"), rules=(
        BRIGHTNESS, RESOLUTION,
        rule("light_source", "Lyskilde", (r"^lyskilde", r"^lampetype", r"^projektorteknologi"), "rank", d.DISPLAY,
             "Laser lyser lengst og sterkest, LED er stillere, lampe må byttes.", ("laser", "led", "lampe")),
        rule("contrast", "Kontrast", (r"^kontrast(forhold)?$", r"^kontrastforhold"), "info", d.DISPLAY, "Høyere kontrast gir dypere svart."),
        rule("throw", "Kastavstand", (r"kastavstand", r"kortkast", r"short throw", r"projeksjonsforhold"), "info", d.CAPACITY,
             "Kortkast kan stå rett under lerretet."),
        rule("hdr", "HDR", (r"^hdr", r"hdr10"), "info", d.DISPLAY, "Bedre lys og farger i støttede filmer."),
        rule("platform", "Smart-plattform", (r"^smart-?\s?tv-plattform", r"^operativsystem", r"^plattform"), "info", d.FEATURES,
             "Innebygde apper slipper ekstra boks."),
        SOUND_W, NOISE, WIFI,
    )),
    # ============================================================ COMPUTING
    Category("laptop", "Bærbare PC-er", ("bærbar", "barbar", "laptop", "macbook", "chromebook", "gaming laptop"), rules=(
        PROCESSOR, GPU, CORES, RAM, RAM_MAX, STORAGE, VRAM, SCREEN_SIZE, RESOLUTION, DISPLAY_TYPE, REFRESH, BRIGHTNESS, TOUCH,
        BATTERY_LIFE, FAST_CHARGE, CHARGER, WEIGHT,
        rule("hdmi", "HDMI", (r"^hdmi-tilkobling", r"^hdmi$"), "yes", d.CONNECTIVITY, "Kobles rett til TV eller skjerm."),
        rule("thunderbolt", "Thunderbolt", r"^thunderbolt$", "yes", d.CONNECTIVITY, "Rask tilkobling til dokking og skjermer."),
        rule("usbc_pd", "USB-C-lading", r"^usb-c power delivery", "yes", d.CONNECTIVITY, "Lad med vanlig USB-C-lader."),
        rule("card_reader", "Minnekortleser", r"^minnekortspor", "yes", d.CONNECTIVITY, "Praktisk for kamera-bilder."),
        rule("backlit", "Bakgrunnsbelyst tastatur", r"bakgrunnsbelyst tastatur", "yes", d.FEATURES, "Lett å skrive i mørket."),
        rule("fingerprint", "Fingeravtrykksleser", r"fingeravtrykk", "yes", d.FEATURES, "Rask og trygg innlogging."),
        rule("os", "Operativsystem", (r"^operativsystem versjon", r"^type operativsystem", r"^operativsystem$"), "info",
             d.FEATURES, "Windows, macOS eller ChromeOS."),
    )),
    Category("tablet", "Nettbrett", ("nettbrett", "ipad", "tablet"), name_generations=True, rules=(
        PROCESSOR, RAM, STORAGE, SCREEN_SIZE, RESOLUTION, DISPLAY_TYPE, REFRESH,
        rule("memory_card", "Minnekortleser", (r"^minnekort", r"microsd"), "yes", d.CAPACITY, "Utvid lagringen billig."),
        rule("pen", "Pennstøtte", (r"penn", r"stylus"), "yes", d.FEATURES, "Notater og tegning med penn."),
        rule("cellular", "Mobilnett (4G/5G)", (r"^mobilnett", r"^5g", r"^4g", r"\blte\b"), "yes", d.CONNECTIVITY,
             "Internett uten Wi-Fi – på hytta og på farten."),
        BATTERY_LIFE, FAST_CHARGE, WEIGHT, UPDATES,
    )),
    # seen on PCSpecialist Prime 400 and Lenovo Legion Tower 5: GPU first – it decides gaming performance.
    Category("desktop", "Stasjonære PC-er", ("stasjonær", "stasjonar", "gaming-pc", "desktop", "gamingpc"), rules=(
        GPU, VRAM, PROCESSOR, CORES, RAM, RAM_MAX, STORAGE,
        rule("psu", "Strømforsyning (W)", (r"^strømforsyning( \(watt\))?$", r"^strømforsyning", r"\bpsu\b"), "higher",
             d.LIFESPAN, "Mer effekt gir rom for et kraftigere grafikkort senere."),
        rule("cooling", "Kjøling", (r"^type avkjøling", r"kjøling"), "info", d.NOISE,
             "Vannkjøling er ofte stillere under full belastning; god luftkjøling holder for de fleste."),
        WIFI_STD,
        rule("os", "Operativsystem", (r"^operativsystem versjon", r"^type operativsystem"), "info", d.FEATURES,
             "Windows Home holder for de fleste."),
    )),
    Category("monitor", "Skjermer", ("pc-skjerm", "dataskjerm", "gamingskjerm", "monitor", "skjerm"), rules=(
        SCREEN_SIZE, RESOLUTION,
        rule("panel", "Paneltype", (r"^paneltype", r"^panelteknologi", r"^displayteknologi", r"^skjermteknologi$", r"^display$"),
             "rank", d.DISPLAY, "OLED best bilde, IPS gode farger, VA god kontrast, TN utdatert.", ("oled", "ips", "va", "tn")),
        REFRESH,
        rule("response", "Responstid (ms)", r"responstid", "lower", d.DISPLAY, "1 ms er ideelt for gaming."),
        BRIGHTNESS,
        rule("contrast", "Kontrast", (r"^kontrast(forhold)?$", r"^kontrastforhold"), "info", d.DISPLAY,
             "Høyere kontrast gir dypere svart – OLED og VA er best."),
        rule("hdr", "HDR", (r"^hdr \(", r"^hdr$", r"^hdr-standard"), "info", d.DISPLAY, "Gir bedre lys og farger i støttede spill og filmer."),
        rule("adaptive_sync", "G-Sync/FreeSync", (r"freesync", r"g-?sync", r"adaptive ?sync"), "info", d.DISPLAY,
             "Fjerner hakking og «tearing» i spill."),
        rule("curved", "Buet skjerm", (r"^buet", r"krumning", r"curved"), "info", d.DISPLAY, "Buet gir mer innlevelse på brede skjermer."),
        rule("displayport", "DisplayPort", r"displayport", "yes", d.CONNECTIVITY, "Best for høy Hz på PC."),
        rule("usbc_pd", "USB-C med lading", (r"usb-c power delivery", r"power delivery", r"^usb-c"), "yes", d.CONNECTIVITY,
             "Én kabel til laptopen – bilde og strøm."),
        rule("height_adjust", "Høydejustering", r"høydejuster", "yes", d.FEATURES, "Bedre ergonomi."),
    )),
    Category("printer", "Skrivere", ("skriver", "printer", "blekkskriver", "laserskriver", "multifunksjonsskriver"), rules=(
        rule("type", "Skrivertype", (r"^skrivertype", r"^utskriftsteknologi", r"^type skriver"), "info", d.FEATURES,
             "Blekk for bilder, laser for mye tekst."),
        rule("color_print", "Fargeutskrift", (r"^fargeutskrift", r"^farge(skriver)?$", r"utskriftsfarge"), "yes", d.FEATURES,
             "Trengs for bilder og skolearbeid i farger."),
        rule("print_speed", "Utskriftshastighet (sider/min)", (r"utskriftshastighet", r"sider per minutt", r"\bppm\b"), "higher",
             d.PERFORMANCE, "Viktig hvis det skrives ut mye på en gang."),
        rule("ink_tank", "Blekktank", (r"blekktank", r"ecotank"), "yes", d.ENERGY, "Mye lavere kostnad per side."),
        rule("page_cost", "Kostnad per side (kr)", (r"kostnad per side", r"sidepris"), "lower", d.ENERGY,
             "Driftskostnaden er ofte viktigere enn innkjøpsprisen."),
        rule("duplex", "Tosidig utskrift", (r"tosidig", r"dupleks"), "yes", d.FEATURES, "Sparer papir."),
        rule("scan", "Skanner", r"skann", "yes", d.FEATURES, "Skann og kopier."),
        rule("adf", "Automatisk dokumentmater", (r"dokumentmater", r"\badf\b"), "yes", d.FEATURES, "Skann mange ark uten å legge inn ett og ett."),
        rule("mobile_print", "Utskrift fra mobil", (r"airprint", r"mopria", r"mobilutskrift"), "yes", d.CONNECTIVITY,
             "Skriv ut rett fra telefonen."),
        WIFI,
    )),
    # seen on Samsung T7: "Total lagringskapasitet (GB): 1000", "Type: Bærbar ekstern SSD", "Tilkoblinger: USB-C"
    Category("storage", "Lagring", ("ekstern ssd", "ekstern harddisk", "harddisk", "minnepenn", "minnekort", "ssd", "nas"), rules=(
        STORAGE,
        rule("storage_type", "Type", (r"^type$", r"^lagringstype", r"^type lagring"), "info", d.FEATURES,
             "SSD er mye raskere og tåler støt bedre enn harddisk."),
        rule("read_speed", "Lesehastighet (MB/s)", (r"lesehastighet", r"overføringshastighet", r"maks.*les"), "higher", d.PERFORMANCE,
             "Hvor raskt filer kopieres fra disken."),
        rule("write_speed", "Skrivehastighet (MB/s)", (r"skrivehastighet", r"maks.*skriv"), "higher", d.PERFORMANCE,
             "Hvor raskt filer kopieres til disken."),
        rule("interface", "Tilkobling", (r"^tilkoblinger", r"^grensesnitt", r"^tilkobling$"), "info", d.CONNECTIVITY,
             "USB-C/USB 3.2 eller Thunderbolt for full fart."),
        rule("encryption", "Kryptering", r"kryptering", "yes", d.FEATURES, "Beskytter filene om disken blir borte."),
        IP_RATING, WEIGHT,
    )),
    # seen on Logitech G305: DPI (dots per inch), Polling rate (Hz), Antall museknapper, Tilkobling, Programmerbare taster
    Category("mouse", "Mus", ("mus", "gamingmus", "datamus"), rules=(
        rule("dpi", "Sensor (DPI)", r"\bdpi\b", "higher", d.PERFORMANCE, "Høyere DPI gir mer presis peker – 12 000+ holder for alle."),
        rule("polling", "Polling rate (Hz)", r"polling ?rate", "higher", d.PERFORMANCE, "1000 Hz eller mer gir lavest forsinkelse."),
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$"), "info", d.CONNECTIVITY,
             "Kablet har lavest forsinkelse; god trådløs er nesten like rask."),
        WEIGHT,
        rule("buttons", "Antall knapper", r"^antall museknapper", "higher", d.FEATURES, "Flere knapper til snarveier i spill og jobb."),
        rule("programmable", "Programmerbare knapper", r"programmerbare taster", "yes", d.FEATURES, "Tilpass knappene selv."),
        BATTERY_LIFE,
        rule("hand", "Høyre/venstre", r"høyre/venstre", "info", d.FEATURES, "Sjekk at den passer hånden."),
    )),
    Category("keyboard", "Tastatur", ("tastatur", "gamingtastatur"), rules=(
        rule("switch", "Brytertype", (r"^brytertype", r"switch", r"^tastemekanisme"), "info", d.FEATURES,
             "Mekanisk gir best følelse; lineær er stille, «clicky» høres godt."),
        rule("layout", "Tastaturoppsett", (r"tastaturoppsett", r"^layout", r"^språk"), "info", d.FEATURES, "Nordisk oppsett har æ, ø og å."),
        rule("size", "Størrelse", (r"^formfaktor", r"^tastaturstørrelse"), "info", d.CAPACITY, "Full, TKL (uten numpad) eller 60 %."),
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$"), "info", d.CONNECTIVITY,
             "Kablet har lavest forsinkelse; god trådløs er nesten like rask."),
        rule("polling", "Polling rate (Hz)", r"polling ?rate", "higher", d.PERFORMANCE, "1000 Hz eller mer gir lavest forsinkelse."),
        rule("backlight", "Bakgrunnsbelysning", (r"bakgrunnsbelys", r"rgb"), "yes", d.FEATURES, "Lett å se tastene i mørket."),
        rule("hotswap", "Byttbare brytere", r"hot-?swap", "yes", d.LIFESPAN, "Bytt brytere uten lodding."),
        BATTERY_LIFE,
    )),
    # seen on Huawei WiFi Mesh 3: WiFi-standard, Hastighet trådløst (Mbps), Frekvensbåndteknologi, Antall noder
    Category("router", "Rutere og nettverk", ("ruter", "router", "mesh", "wi-fi-system", "wifi-system", "tilgangspunkt", "aksesspunkt"), rules=(
        WIFI_STD,
        rule("wireless_speed", "Trådløs hastighet (Mbps)", (r"hastighet trådløst", r"trådløs hastighet", r"^maks.*hastighet"), "higher",
             d.PERFORMANCE, "Samlet kapasitet – mer betyr plass til flere enheter samtidig."),
        rule("bands", "Frekvensbånd", r"frekvensbånd", "rank", d.PERFORMANCE, "Tri-band gir et eget bånd mellom mesh-enhetene.",
             ("quad-band", "tri-band", "dual-band")),
        rule("nodes", "Antall enheter i pakken", r"^antall noder", "higher", d.CAPACITY, "Flere enheter dekker større bolig."),
        rule("mesh", "Mesh-støtte", r"mesh kompatibel", "yes", d.FEATURES, "Kan utvides med flere enheter senere."),
        rule("mu_mimo", "MU-MIMO", (r"mu-mimo", r"flere datastrømmer"), "yes", d.PERFORMANCE, "Bedre fart når mange bruker nettet."),
        rule("backhaul", "Dedikert backhaul", r"backhaul", "yes", d.PERFORMANCE, "Mesh-enhetene snakker sammen uten å stjele fart."),
        rule("lan_ports", "LAN-porter", r"^antall lan-porter", "info", d.CONNECTIVITY, "Kablet til TV, PC og konsoll."),
        rule("wired_speed", "Kablet hastighet", r"hastighet med kabel", "info", d.CONNECTIVITY, "1000 Mbps (gigabit) er standard."),
    )),
    Category("pc_speaker", "PC-høyttalere", ("pc-høyttaler", "pc-hoyttaler", "datahøyttaler", "pc høyttaler"), rules=(
        SOUND_W,
        rule("channels", "Kanaler", (r"^kanaler", r"kanalkonfig", r"^antall kanaler"), "info", d.SOUND, "2.1 betyr egen subwoofer."),
        rule("subwoofer", "Subwoofer", (r"subwoofer", r"basselement"), "info", d.SOUND, "Egen subwoofer gir mye mer bass."),
        BLUETOOTH,
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$", r"^tilkoblinger"), "info", d.CONNECTIVITY,
             "USB, 3,5 mm eller optisk."),
        rule("rgb", "RGB-lys", r"rgb", "yes", d.FEATURES, "Lys som kan matche resten av oppsettet."),
    )),
    Category("camera", "Kameraer", ("kamera", "speilrefleks", "systemkamera", "kompaktkamera", "actionkamera"), name_generations=True, rules=(
        rule("sensor", "Sensorstørrelse", (r"^sensorstørrelse", r"^sensortype", r"^bildebrikke"), "rank", d.CAMERA,
             "Større sensor gir bedre bilder i dårlig lys.",
             ("fullformat", "full frame", "aps-c", "micro four thirds", "1\"")),
        rule("megapixels", "Megapiksler (MP)", (r"megapiksel", r"effektive piksler"), "info", d.CAMERA, "24–33 MP holder for de fleste."),
        rule("autofocus", "Autofokus", r"^autofokus", "info", d.CAMERA, "Øye-/motivfølging gjør det lettere å treffe."),
        rule("video_res", "Video", (r"^opptaksoppløsning", r"^videooppløsning", r"^video"), "rank", d.CAMERA,
             "4K 60 fps og 10-bit for seriøs video.", ("8k", "6k", "5.7k", "4k", "full hd", "1080")),
        rule("ibis", "Bildestabilisering", (r"stabilisering", r"\bibis\b"), "yes", d.CAMERA, "Skarpere bilder på håndholdt."),
        rule("shots", "Bilder per lading", (r"bilder per (lading|batteri)", r"^batterikapasitet.*bilder", r"^antall bilder"),
             "higher", d.BATTERY, "Flere bilder før du må lade eller bytte batteri."),
        rule("weather_sealed", "Værbestandig", (r"værbestandig", r"værtett", r"vær- og støv"), "yes", d.DURABILITY,
             "Tåler regn og støv på tur."),
        WIFI, WEIGHT,
    )),
    # =============================================================== GAMING
    # seen on PlayStation 5 Pro: "Harddiskkapasitet (GB): 2000", "Konsollnavn" – thin pages, so generation from the name matters.
    Category("console", "Spillkonsoller", ("spillkonsoll", "konsoll", "playstation 5", "ps5", "xbox series", "nintendo switch",
                                           "steam deck", "håndholdt konsoll"), name_generations=True, rules=(
        STORAGE,
        rule("edition", "Utgave", (r"^utgave", r"^diskstasjon", r"^optisk stasjon"), "info", d.FEATURES,
             "Disk-utgave kan bruke brukte spill; digital er billigere i innkjøp."),
        rule("max_res", "Maks oppløsning", (r"^maks(imal)? oppløsning", r"^oppløsning"), "info", d.DISPLAY, "4K krever en 4K-TV."),
        rule("controllers", "Kontrollere inkludert", r"^antall (kontroller|håndkontroller)", "higher", d.FEATURES,
             "Flere kontrollere i esken = klar for flerspiller."),
        rule("portable", "Kan spilles på farten", (r"håndholdt", r"bærbar"), "yes", d.PORTABILITY, "Kan tas med og spilles uten TV."),
        BATTERY_LIFE, WIFI_STD,
    )),
    Category("controller", "Spillkontrollere", ("kontroller", "spillkontroller", "håndkontroll", "dualsense", "gamepad"), rules=(
        rule("platform", "Plattform", (r"^plattform", r"kompatib", r"passer til"), "info", d.CONNECTIVITY,
             "Sjekk at den passer konsollen eller PC-en."),
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$"), "info", d.CONNECTIVITY, "Trådløs eller kablet."),
        BATTERY_LIFE,
        rule("paddles", "Bakknapper", (r"bakknapp", r"paddles", r"ekstra knapper"), "yes", d.FEATURES, "Ekstra knapper bak – nyttig i skytespill."),
        rule("hall_effect", "Hall effect-spaker", r"hall ?effect", "yes", d.LIFESPAN, "Spakene «drifter» ikke over tid."),
        rule("haptics", "Vibrasjon/haptikk", (r"vibrasjon", r"haptisk", r"force feedback"), "yes", d.FEATURES, "Kjenn spillet i hendene."),
    )),
    Category("racing", "Ratt og joysticks", ("ratt", "rattsett", "racingratt", "pedaler", "joystick", "flightstick"), rules=(
        rule("force_feedback", "Force feedback", (r"force ?feedback", r"kraftrespons"), "yes", d.PERFORMANCE,
             "Rattet gir motstand og kjennes som en ekte bil."),
        rule("direct_drive", "Direct drive", r"direct ?drive", "yes", d.PERFORMANCE, "Kraftigst og mest presis følelse."),
        rule("torque", "Dreiemoment (Nm)", r"dreiemoment", "higher", d.PERFORMANCE, "Mer Nm gir kraftigere og mer detaljert respons."),
        rule("rotation", "Rotasjon (grader)", (r"rotasjon", r"grader"), "higher", d.FEATURES, "900°+ gir realistisk ratt."),
        rule("pedals", "Pedaler", r"pedal", "info", d.FEATURES, "Tre pedaler gir clutch."),
        rule("shifter", "Girspak", r"girspak", "yes", d.FEATURES, "Manuelt gir for ekstra innlevelse."),
        rule("platform", "Plattform", (r"^plattform", r"kompatib", r"passer til"), "info", d.CONNECTIVITY,
             "Sjekk at den passer konsollen eller PC-en."),
    )),
    Category("streaming_gear", "Strømming og opptak", ("mikrofon", "webkamera", "webcam", "capture card", "opptakskort",
                                                         "strømmeutstyr", "ringlys", "stream deck"), rules=(
        rule("type", "Type", (r"^type", r"^produkttype"), "info", d.FEATURES, "Mikrofon, webkamera eller opptakskort."),
        RESOLUTION,
        rule("fps", "Bilder per sekund", (r"bilder per sekund", r"\bfps\b", r"bildefrekvens"), "higher", d.CAMERA,
             "60 fps gir jevnere bilde."),
        rule("polar", "Opptaksmønster", (r"polarmønster", r"opptaksmønster", r"karakteristikk"), "info", d.SOUND,
             "Nyre (cardioid) tar opp stemmen din og demper resten av rommet."),
        rule("bit_depth", "Lydkvalitet (bit/kHz)", (r"bitdybde", r"samplingsfrekvens", r"bit-?rate"), "info", d.SOUND,
             "24-bit/48 kHz er studiokvalitet."),
        rule("webcam_af", "Autofokus", r"autofokus", "yes", d.CAMERA, "Holder bildet skarpt når du beveger deg."),
        rule("mute", "Mute-knapp", (r"mute", r"demp(e)?knapp", r"lydløs"), "yes", d.FEATURES, "Slå av mikrofonen raskt."),
        rule("cam_light", "Innebygd lys", (r"ringlys", r"innebygd lys", r"led-lys"), "yes", d.CAMERA, "Bedre bilde i mørke rom."),
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$", r"^tilkoblinger"), "info", d.CONNECTIVITY,
             "USB er enklest; XLR krever lydkort."),
    )),
    Category("component", "PC-komponenter", ("grafikkort", "hovedkort", "pc-komponent", "minnebrikke", "kabinett",
                                             "prosessorkjøler", "pc-strømforsyning"), rules=(
        GPU, VRAM, PROCESSOR, CORES, RAM, STORAGE,
        rule("read_speed", "Lesehastighet (MB/s)", (r"lesehastighet", r"overføringshastighet", r"maks.*les"), "higher", d.PERFORMANCE,
             "Hvor raskt filer kopieres fra disken."),
        rule("psu", "Strømforsyning (W)", (r"^strømforsyning( \(watt\))?$", r"^strømforsyning", r"\bpsu\b", r"^effekt"), "higher",
             d.LIFESPAN, "Mer effekt gir rom for kraftigere komponenter."),
        rule("recommended_psu", "Anbefalt strømforsyning (W)", r"anbefalt strøm", "info", d.ENERGY,
             "Sjekk at PC-ens strømforsyning er stor nok."),
    )),
    # ================================================================== MDA
    # seen on LG GSJC41EPPE: "Nettovolum kjøledel (I)", "Nettovolum frysedel (I)", "NoFrost", "Lydklasse", "Dispenser"
    Category("fridge", "Kjøleskap og frysere", ("kjøleskap", "kjoleskap", "fryser", "kombiskap", "fryseboks", "fryseskap"), rules=(
        rule("volume", "Totalvolum (liter)", (r"^totalvolum", r"^nettovolum(?!.*(kjøl|frys))", r"^volum", r"^kapasitet.*liter"),
             "higher", d.CAPACITY, "Kjøl: 50–100 L per person. Frys: ca. 50 L + 30 L per ekstra person."),
        rule("fridge_volume", "Kjølevolum (liter)", (r"kjøl.*volum", r"volum.*kjøl"), "higher", d.CAPACITY, "Plass til ferskvarer."),
        rule("freezer_volume", "Frysevolum (liter)", (r"frys.*volum", r"volum.*frys"), "higher", d.CAPACITY, "Plass til frysevarer."),
        ENERGY, ENERGY_YEAR, NOISE,
        rule("nofrost", "NoFrost", (r"no ?frost", r"frostfri"), "yes", d.FEATURES, "Slipper å avrime fryseren."),
        rule("zero_zone", "Nullsone", (r"nullsone", r"0 ?°c", r"fresh ?zone", r"vitafresh"), "yes", d.FEATURES,
             "Kjøtt og fisk holder seg lenger."),
        rule("fast_cool", "Hurtigkjøling", (r"rask nedkjøling", r"hurtigkjøl", r"superkjøl"), "yes", d.FEATURES,
             "Kjøler ned nye varer raskt etter handletur."),
        rule("fast_freeze", "Hurtigfrys", (r"hurtigfrys", r"superfrys"), "yes", d.FEATURES, "Fryser ned raskt og bevarer kvaliteten."),
        rule("height", "Høyde (cm)", r"^høyde \(cm\)", "info", d.CAPACITY, "Sjekk at den passer plassen."),
        INSTALL,
        rule("door", "Omhengslbar dør", (r"omhengsl", r"reversibel", r"dørhengsel", r"dørhengsling"), "info", d.FEATURES,
             "Døren må kunne åpnes fra den siden som passer kjøkkenet."),
        WIFI,
    )),
    Category("american_fridge", "Amerikanerskap og side-by-side",
             ("side-by-side", "side by side", "amerikanerskap", "amerikansk kjøleskap", "multidoor", "french door"), rules=(
        rule("fridge_volume", "Kjølevolum (liter)", (r"kjøl.*volum", r"volum.*kjøl"), "higher", d.CAPACITY, "Plass til ferskvarer."),
        rule("freezer_volume", "Frysevolum (liter)", (r"frys.*volum", r"volum.*frys"), "higher", d.CAPACITY, "Plass til frysevarer."),
        rule("dispenser", "Vann-/isdispenser", r"^dispenser", "info", d.FEATURES, "Kaldt vann og is rett fra døra."),
        rule("ice_maker", "Ismaskin", (r"ismaskin", r"isbitmaskin", r"isterning"), "yes", d.FEATURES, "Lager is automatisk."),
        rule("water_inlet", "Vanntilkobling", r"^vanninntak", "info", d.FEATURES,
             "Fast vanntilkobling krever rørlegger; vannbeholder fylles for hånd."),
        ENERGY, ENERGY_YEAR, NOISE,
        rule("nofrost", "NoFrost", (r"no ?frost", r"frostfri"), "yes", d.FEATURES, "Slipper å avrime fryseren."),
        rule("door_in_door", "Door-in-Door / bar", (r"door-?in-?door", r"instaview", r"showcase"), "yes", d.ENERGY,
             "Hent det du bruker mest uten å åpne hele skapet."),
        rule("doors", "Antall dører", r"^antall dører", "info", d.FEATURES, "Side-by-side, French door eller multidoor."),
        rule("width", "Bredde (cm)", r"^bredde \(cm\)", "info", d.CAPACITY, "Ofte ca. 90 cm – mål plassen og døråpningene hjemme."),
        rule("fast_freeze", "Hurtigfrys", (r"hurtigfrys", r"superfrys"), "yes", d.FEATURES, "Fryser ned raskt og bevarer kvaliteten."),
        WIFI,
    )),
    Category("wine_fridge", "Vinskap", ("vinskap", "vinkjøleskap", "vinkjoleskap", "vinkjøler", "vinkjoler", "drikkekjøler"), rules=(
        rule("bottles", "Antall flasker", (r"antall flasker", r"flaskekapasitet", r"kapasitet.*flask"), "higher", d.CAPACITY,
             "Basert på standard Bordeaux-flasker – større flasker tar mer plass."),
        rule("wine_zones", "Temperatursoner", (r"antall (temperatur)?soner", r"temperatursoner", r"^soner"), "higher", d.FEATURES,
             "To soner lar deg ha rødvin og hvitvin på hver sin temperatur."),
        rule("temp_range", "Temperaturområde", (r"temperaturområde", r"temperaturintervall"), "info", d.FEATURES,
             "Ca. 5–18 °C dekker både musserende og rødvin."),
        rule("uv_glass", "UV-beskyttet glass", (r"uv", r"tonet glass"), "yes", d.DURABILITY, "Lys skader vinen over tid."),
        NOISE, ENERGY, INSTALL,
        rule("wood_shelves", "Trehyller", (r"trehyll", r"hyllemateriale"), "info", d.FEATURES, "Treshyller demper vibrasjoner."),
    )),
    # seen on Electrolux EOP721NV: "Volum (Itr): 71", "Pyrolyse (selvrensende): Ja", "Dampfunksjon", "Steketermometer", "Mikro"
    Category("oven", "Stekeovner og komfyrer", ("stekeovn", "komfyr", "ovn", "dampovn"), rules=(
        rule("oven_volume", "Ovnsvolum (liter)", (r"^ovnsvolum", r"^volum", r"^kapasitet.*liter"), "higher", d.CAPACITY,
             "Ca. 70 L+ er standard; mer gir plass til flere brett."),
        rule("pyrolysis", "Pyrolyse (selvrens)", r"^pyrolyse", "yes", d.FEATURES, "Brenner bort fett – den enkleste ovnen å holde ren."),
        rule("cleaning", "Rengjøring", (r"^selvrens", r"^rengjøring", r"rensefunksjon"), "rank", d.FEATURES,
             "Pyrolyse > katalyse > damp-rens.", ("pyrolyse", "katalyse", "damp")),
        rule("hot_air", "Varmluft", r"^varmluft", "yes", d.FEATURES, "Jevn varme på flere brett."),
        rule("steam", "Dampfunksjon", r"damp", "yes", d.FEATURES, "Bedre brød og saftigere kjøtt."),
        rule("probe", "Steketermometer", (r"steketermometer", r"kjernetemperatur"), "yes", d.FEATURES,
             "Perfekt stek uten gjetting."),
        rule("micro_combo", "Mikrobølgefunksjon", r"^mikro$", "yes", d.FEATURES, "Ovn og mikro i ett."),
        rule("auto_programs", "Automatiske programmer", r"^autoprogram", "yes", d.FEATURES, "Ovnen velger varme og tid selv."),
        ENERGY,
        rule("oven_count", "Antall ovnsrom", r"^antall ovnsrom", "higher", d.CAPACITY, "To ovnsrom gir to temperaturer samtidig."),
        rule("hob_type", "Platetopp (komfyr)", (r"^type oppvarming av platetopp", r"^platetopptype", r"^koketopptype",
                                                 r"^type (plate|koke)topp"), "rank",
             d.PERFORMANCE, "Induksjon er raskest og mest effektiv.", ("induksjon", "keramisk", "støpejern")),
        rule("child_lock", "Barnesikring", r"barnesikring", "yes", d.FEATURES, "Viktig med små barn i huset."),
        WIFI, INSTALL, FUSE,
    )),
    # seen on Electrolux HOX750MF: "Type oppvarming av platetopp: Induksjon", "Total effekt (watt): 7350",
    # "Antall Booster: 2", "Kjeleregistrering", "Stekesensor", "Kontroller: Berøring"
    Category("hob", "Platetopper", ("platetopp", "induksjonstopp", "koketopp", "keramisk topp"), rules=(
        rule("hob_type", "Type", (r"^type oppvarming av platetopp", r"^platetopptype", r"^koketopptype", r"^type (plate|koke)topp",
                                  r"^varmeteknologi"), "rank",
             d.PERFORMANCE, "Induksjon er raskest og mest effektiv.", ("induksjon", "keramisk", "støpejern")),
        rule("zones", "Antall kokesoner", (r"^antall (kokesoner|soner|kokeplater)",), "higher", d.CAPACITY, "Flere gryter samtidig."),
        rule("total_power", "Total effekt (W)", r"^total effekt", "higher", d.PERFORMANCE, "Mer effekt totalt = flere soner på full guffe samtidig."),
        rule("boosters", "Antall boostere", r"^antall booster", "higher", d.PERFORMANCE, "Koker opp vann ekstra raskt."),
        rule("flex", "Fleksible soner", (r"flexi", r"bridge", r"fleksib"), "yes", d.FEATURES, "Plass til store panner og grillplater."),
        rule("pan_detect", "Kjelegjenkjenning", (r"kjeleregistrering", r"kjelegjenkjenn"), "yes", d.FEATURES,
             "Sonen tilpasser seg størrelsen på kjelen."),
        rule("fry_sensor", "Stekesensor", r"stekesensor", "yes", d.FEATURES, "Holder riktig temperatur i panna."),
        rule("hob2hood", "Styrer viften (Hob2Hood)", (r"hob2hood", r"hood ?link", r"kobling til vifte"), "yes", d.FEATURES,
             "Kjøkkenviften slår seg på av seg selv."),
        rule("vented", "Innebygd ventilator", (r"med ventilator", r"innebygd ventilasjon", r"integrert vifte"), "yes", d.FEATURES,
             "Trenger ingen kjøkkenvifte over."),
        TIMER,
        rule("width", "Bredde (cm)", r"^bredde \(cm\)", "info", d.CAPACITY, "Må passe utsparingen i benken."),
        rule("controls", "Betjening", r"^kontroller", "info", d.FEATURES, "Glidebryter er raskest å justere."),
        FUSE,
    )),
    # seen on Electrolux LMS2173NB: "Mikrobølgeeffekt: 700 W", "Volum (Itr): 17", "Grill", "Varmluft", "Plassering: Integrert"
    Category("microwave", "Mikrobølgeovner", ("mikrobølgeovn", "mikrobolgeovn", "mikro"), rules=(
        rule("mw_power", "Mikrobølgeeffekt (W)", (r"^mikrobølgeeffekt", r"^effekt( \(w(att)?\))?$"), "higher", d.PERFORMANCE,
             "800–1000 W varmer raskt; 700 W tar litt lengre tid."),
        rule("mw_volume", "Volum (liter)", (r"^volum", r"^kapasitet.*liter"), "higher", d.CAPACITY, "20–25 L passer de fleste tallerkener."),
        rule("grill", "Grill", r"^grill$", "yes", d.FEATURES, "Gir sprø overflate."),
        rule("hot_air", "Varmluft", r"^varmluft", "yes", d.FEATURES, "Kan også steke og bake som en liten ovn."),
        rule("auto_programs", "Automatiske programmer", r"^autoprogram", "yes", d.FEATURES, "Velg mat og vekt – mikroen gjør resten."),
        rule("turntable", "Roterende tallerken", r"roterende tallerken", "info", d.FEATURES, "Flat bunn gir mer plass og er enklere å vaske."),
        INSTALL, TIMER, WIFI,
    )),
    # seen on Electrolux EFF60560OW: "Kapasitet (m3/h): 603", "Lydnivå, Lav/Høy (dB)", "Fettfiltreringseffektivitetsklasse: D"
    Category("hood", "Kjøkkenvifter", ("kjøkkenvifte", "kjokkenvifte", "ventilator", "avtrekksvifte", "kjøkkenventilator"), rules=(
        rule("airflow", "Sugeevne (m³/t)", (r"^kapasitet \(m3", r"luftkapasitet", r"sugeevne", r"m3/h", r"m³/t"), "higher",
             d.PERFORMANCE, "Bør være ca. 10 × kjøkkenets volum (m³)."),
        NOISE_LOW, NOISE_HIGH, ENERGY, ENERGY_YEAR,
        rule("grease_class", "Fettfiltrering (klasse)", r"^fettfiltreringseffektivitetsklasse", "energy", d.DURABILITY,
             "Bedre klasse fanger mer fett – renere skap og vegger."),
        rule("hood_type", "Type", (r"^type ventilator", r"^installasjonstype", r"^type kjøkkenvifte"), "info", d.FEATURES,
             "Vegghengt, underbygd, integrert eller øy."),
        rule("mode", "Avtrekk eller kullfilter", (r"utsugning", r"resirkul", r"kullfilter"), "info", d.FEATURES,
             "Avtrekk ut er mest effektivt; kullfilter når det ikke finnes kanal."),
        rule("width", "Bredde (cm)", (r"^installasjonsbredde", r"^bredde \(cm\)"), "info", d.CAPACITY, "Bør være minst like bred som platetoppen."),
        SPEEDS,
        rule("hob2hood", "Styres av platetoppen (Hob2Hood)", (r"hob2hood", r"hood ?link", r"kobling til platetopp"), "yes",
             d.FEATURES, "Starter av seg selv når du lager mat."),
        rule("light", "Belysning", r"^lystype", "info", d.FEATURES, "LED lyser godt og bruker lite strøm."),
        WIFI,
    )),
    Category("dishwasher", "Oppvaskmaskiner", ("oppvaskmaskin",), rules=(
        rule("place_settings", "Antall kuverter", r"kuvert", "higher", d.CAPACITY, "13–15 er standard for 60 cm."),
        NOISE, ENERGY,
        rule("cutlery", "Bestikkplassering", r"^bestikk", "rank", d.FEATURES, "Bestikkskuff øverst frigjør plass i kurvene.",
             ("skuff", "kurv")),
        rule("basket_adjust", "Høydejusterbar overkurv", (r"høydejustering på øvre", r"justerbar (over|øvre)"), "yes", d.FEATURES,
             "Plass til høye glass og store kjeler."),
        rule("water", "Vannforbruk (liter per vask)", (r"vannforbruk",), "lower", d.ENERGY, "Lavere forbruk sparer vann og strøm."),
        rule("auto_open", "Automatisk døråpning", (r"automatisk åpning", r"autoopen", r"zeolit"), "yes", d.PERFORMANCE,
             "Gir mye bedre tørkeresultat."),
        rule("install", "Installasjonstype", (r"^type oppvaskmaskin", r"^installasjon", r"^plassering$"), "info", d.FEATURES,
             "Helintegrert, semi-integrert, underbygd eller frittstående."),
        rule("width", "Bredde (cm)", r"^bredde \(cm\)", "info", d.CAPACITY, "45 eller 60 cm – må passe hullet."),
        PROGRAMS, WIFI,
    )),
    # seen on ASKO W3096RW: "Sentrifugehastighet (o/min)", "Kapasitet vaskesyklus (kg)", "Vektet vannforbruk …".
    # The customer asked for spin speed instead of dB, so noise is left out for washers.
    Category("washer", "Vaskemaskiner", ("vaskemaskin", "toppmatet", "slimline"), rules=(
        rule("capacity_kg", "Kapasitet (kg)", (r"^kapasitet vaskesyklus", r"^vaskekapasitet", r"^kapasitet.*kg", r"^maks.*(last|fylling)"),
             "higher", d.CAPACITY, "Familie på fire: 8–9 kg. Mindre husstand: 6–7 kg."),
        rule("spin", "Sentrifuge (o/min)", (r"^sentrifugehastighet", r"sentrifug(?!eklasse)", r"o/min", r"^turtall"), "higher",
             d.PERFORMANCE, "1400 o/min er vanlig, 1600 gir tørrere klær og kortere tørketid."),
        ENERGY,
        rule("energy_100", "Strømforbruk (kWh/100 vask)", r"kwh/100", "lower", d.ENERGY, "Lavere forbruk gir lavere strømregning."),
        rule("water", "Vannforbruk (liter per vask)", (r"vannforbruk vaskesyklus", r"vannforbruk"), "lower", d.ENERGY,
             "Lavere forbruk sparer vann og strøm."),
        rule("auto_dose", "Automatisk dosering", (r"dosering", r"autodos"), "yes", d.FEATURES, "Sparer vaskemiddel."),
        rule("steam", "Dampprogram", r"damp", "yes", d.FEATURES, "Mindre krøll og lukt."),
        rule("weight_sensor", "Vektsensor", r"vektsensor", "yes", d.ENERGY, "Tilpasser vann og tid til mengden tøy."),
        rule("delay_start", "Utsatt start", r"utsatt (oppstart|start)", "yes", d.FEATURES, "Vask når strømmen er billigst."),
        PROGRAMS, WIFI, INSTALL,
    )),
    # seen on Electrolux EW7WB764T4: "Kapasitet vaskesyklus (kg): 7", "Kapasitet vaske- og tørkesyklus (kg): 4"
    Category("washer_dryer", "Kombinert vaskemaskin og tørketrommel",
             ("vaskemaskin med tørketrommel", "kombinert vaskemaskin", "vaskemaskin og tørketrommel", "vasketørker",
              "vask/tørk", "vasketørk"), rules=(
        rule("capacity_kg", "Vaskekapasitet (kg)", (r"^kapasitet vaskesyklus", r"^vaskekapasitet"), "higher", d.CAPACITY,
             "Hvor mye som kan vaskes på én gang."),
        rule("dry_capacity", "Tørkekapasitet (kg)", (r"kapasitet vaske- og tørkesyklus", r"tørkekapasitet"), "higher", d.CAPACITY,
             "Hvor mye som kan vaskes og tørkes i ett program – ofte bare halvparten av vaskekapasiteten."),
        rule("spin", "Sentrifuge (o/min)", (r"^sentrifugehastighet", r"sentrifug(?!eklasse)", r"o/min"), "higher", d.PERFORMANCE,
             "1400 o/min er vanlig, 1600 gir tørrere klær og kortere tørketid."),
        ENERGY,
        rule("energy_100", "Strømforbruk (kWh/100 vask+tørk)", (r"energiforbruk full syklus", r"kwh/100"), "lower", d.ENERGY,
             "Strøm for vask og tørk sammen."),
        rule("water", "Vannforbruk (liter per vask+tørk)", (r"vannforbruk full syklus", r"vannforbruk"), "lower", d.ENERGY,
             "Kombimaskiner bruker vann også når de tørker."),
        rule("cycle_time", "Tid vask + tørk", r"syklusvarighet full", "info", d.FEATURES, "Hvor lang tid et fullt vask-og-tørk-program tar."),
        rule("steam", "Dampprogram", r"damp", "yes", d.FEATURES, "Mindre krøll og lukt."),
        rule("auto_dose", "Automatisk dosering", (r"dosering", r"autodos"), "yes", d.FEATURES, "Sparer vaskemiddel."),
        PROGRAMS, WIFI, INSTALL,
    )),
    # seen on LG RV9DN902B: "Type tørketrommel: Kondens" + "Varmepumpeteknologi: Ja".
    Category("dryer", "Tørketromler og tørkeskap", ("tørketrommel", "torketrommel", "tørketromler", "tørkeskap", "torkeskap"), rules=(
        rule("heat_pump", "Varmepumpe", (r"^varmepumpe",), "yes", d.ENERGY,
             "Varmepumpe bruker opptil halvparten så mye strøm og er skånsom mot klærne."),
        rule("capacity_kg", "Kapasitet (kg)", (r"^tørkekapasitet", r"^kapasitet.*kg"), "higher", d.CAPACITY,
             "Bør være minst like stor som vaskemaskinen."),
        ENERGY, ENERGY_YEAR,
        rule("tech", "Type", (r"^type tørketrommel", r"^tørketeknologi", r"^tørkemetode"), "info", d.FEATURES,
             "Kondens eller ventilasjon – varmepumpe er alltid kondens."),
        rule("moisture", "Fuktsensor", (r"fuktsensor", r"fuktighetssensor", r"^tørkesystem", r"sensortørk"), "yes", d.FEATURES,
             "Stopper automatisk når tøyet er tørt."),
        rule("drain", "Kan kobles til avløp", (r"kobles til avløp", r"avløp", r"tømmeslange", r"drenering"), "yes", d.FEATURES,
             "Slipper å tømme vanntanken."),
        rule("steam", "Dampfunksjon", r"^damp", "yes", d.FEATURES, "Mindre krøll – kan erstatte stryking."),
        NOISE, WIFI,
    )),
    # ================================================================== SDA
    Category("kitchen_machine", "Kjøkkenmaskiner", ("kjøkkenmaskin", "kjokkenmaskin", "stand mixer"), rules=(
        rule("motor_power", "Motorkraft (W)", (r"^motorkraft", r"^motoreffekt", r"^effekt( \(w(att)?\))?$"), "higher",
             d.PERFORMANCE, "Mer effekt hjelper i tung deig – men girkasse og konstruksjon betyr også mye."),
        rule("bowl_volume", "Bollevolum (liter)", (r"^bollevolum", r"^bollestørrelse", r"^volum"), "higher", d.CAPACITY,
             "Større bolle gir plass til større porsjoner."),
        rule("dough_capacity", "Deigkapasitet (kg)", r"^kapasitet \(kg\)", "higher", d.CAPACITY,
             "Hvor mye deig maskinen er laget for å elte på én gang."),
        rule("bowls", "Antall boller", r"^antall boller", "higher", d.CAPACITY,
             "To boller lar deg bytte oppskrift uten å vaske imellom."),
        SPEEDS,
        rule("pulse", "Puls-/turboknapp", r"turbo-?/?pulsknapp", "yes", d.FEATURES, "Korte, kraftige støt ved behov."),
        rule("outlets", "Uttak for tilbehør", r"^antall uttak for tilbehør", "higher", d.FEATURES,
             "Flere uttak gir flere muligheter med ekstrautstyr (kjøttkvern, pasta …)."),
        rule("scale", "Integrert vekt", (r"integrert vekt", r"innebygd vekt", r"^vekt inkludert"), "yes", d.FEATURES,
             "Vei ingrediensene rett i bollen – mindre søl og oppvask."),
        rule("auto_programs", "Automatiske programmer", (r"automatiske programmer", r"^sensor"), "yes", d.FEATURES,
             "Maskinen stopper selv når konsistensen er riktig."),
        rule("timer", "Timer", r"^timer", "yes", d.FEATURES, "Slipper å følge med på klokka."),
        rule("display", "Display/berøringsskjerm", (r"berøringsskjerm", r"^display", r"^touch"), "yes", d.FEATURES,
             "Enklere å velge programmer og se tid/vekt."),
        rule("material", "Bollemateriale", (r"^materiale",), "info", d.DURABILITY, "Rustfritt stål tåler mest."),
        DISHWASHER_SAFE,
    )),
    Category("blender", "Blendere og juicere", ("blender", "smoothie", "juicer", "saftpresse", "juicepresse", "smoothiemaker"), rules=(
        POWER,
        rule("jug_volume", "Kannevolum (liter)", (r"^(kanne|beger|mugge)\w*volum", r"^kapasitet( \(l(iter)?\))?$", r"^volum"),
             "higher", d.CAPACITY, "Større kanne gir flere porsjoner på én gang."),
        rule("ice_crush", "Knuser is", r"isknus", "yes", d.FEATURES, "Til smoothies og frosne drinker."),
        SPEEDS, PROGRAMS,
        rule("to_go", "To go-flaske", (r"to ?go", r"drikkeflaske", r"på farten"), "yes", d.PORTABILITY, "Blend rett i flaska og ta med."),
        rule("jug_material", "Kannemateriale", (r"^(kanne|beger)\w*materiale", r"^materiale"), "info", d.DURABILITY,
             "Glass er tyngre men riper mindre enn plast."),
        DISHWASHER_SAFE,
    )),
    Category("stick_mixer", "Stavmiksere og håndmiksere", ("stavmikser", "håndmikser", "handmikser", "stavblender"), rules=(
        POWER, SPEEDS,
        rule("turbo", "Turbofunksjon", r"turbo", "yes", d.PERFORMANCE, "Ekstra kraft ved behov."),
        ACCESSORIES,
        rule("chopper", "Hakkebolle", (r"hakkebolle", r"kutter", r"minihakker"), "yes", d.FEATURES, "Hakk løk, nøtter og urter."),
        rule("whisk", "Visp", r"visp", "yes", d.FEATURES, "Pisk krem og eggehviter."),
        CORDLESS,
        rule("material", "Materiale (stav)", (r"^materiale",), "info", d.DURABILITY, "Metallstav tåler varm suppe."),
        DISHWASHER_SAFE,
    )),
    Category("airfryer", "Airfryere og frityrkokere", ("airfryer", "air fryer", "varmluftsfriteres", "frityrkoker"), rules=(
        rule("capacity_l", "Kapasitet (liter)", (r"^kapasitet( \(l(iter)?\))?$", r"^kurvvolum", r"^volum", r"^kapasitet.*liter"),
             "higher", d.CAPACITY, "Ca. 1 liter per person er en grei tommelfingerregel."),
        rule("baskets", "Antall kurver/skuffer", (r"^antall (kurver|skuffer|kammer)",), "higher", d.CAPACITY,
             "To kurver lager to retter samtidig."),
        POWER, PROGRAMS,
        rule("window", "Vindu", (r"vindu", r"innsyn"), "yes", d.FEATURES, "Følg med uten å åpne."),
        THERMOSTAT, TIMER, DISHWASHER_SAFE, APP,
    )),
    Category("sandwich", "Sandwich-, vaffel- og kontaktgriller",
             ("sandwichgrill", "sandwichjern", "sandwichmaker", "vaffeljern", "toastjern", "kontaktgrill", "bordgrill", "panini"), rules=(
        POWER,
        rule("servings", "Antall porsjoner", (r"^antall (vafler|skiver|plater|porsjoner|sandwicher)",), "higher", d.CAPACITY,
             "Flere porsjoner på én gang."),
        rule("removable_plates", "Avtakbare plater", (r"avtakbare plater", r"utskiftbare plater", r"løse plater"), "yes", d.FEATURES,
             "Platene kan vaskes for seg – mye enklere rengjøring."),
        rule("nonstick", "Slippbelegg", (r"non-?stick", r"slippbelegg", r"teflon", r"keramisk belegg"), "yes", d.FEATURES,
             "Maten løsner lett."),
        THERMOSTAT,
        rule("plate_types", "Platetyper", (r"platetyper", r"medfølgende plater"), "info", d.FEATURES, "Flere plater = flere bruksområder."),
        DISHWASHER_SAFE,
    )),
    Category("soda", "Kullsyremaskiner", ("kullsyremaskin", "sodastream", "brusmaskin", "kullsyreapparat"), rules=(
        rule("co2_type", "Kullsyresylinder", (r"sylinder", r"kullsyre(patron|beholder)"), "info", d.ENERGY,
             "Quick Connect (rosa) er enklest å bytte."),
        rule("bottles", "Antall flasker inkludert", (r"antall flasker", r"medfølgende flasker"), "higher", d.CAPACITY,
             "Flere flasker i esken."),
        rule("carbonation_levels", "Kullsyrenivåer", (r"kullsyrenivå", r"antall nivåer"), "higher", d.FEATURES,
             "Velg hvor mye bobler du vil ha."),
        rule("electric", "Elektrisk", (r"elektrisk", r"strømdrevet"), "yes", d.FEATURES, "Ett knappetrykk gir alltid samme nivå."),
        rule("glass_bottle", "Glassflaske", r"glass", "yes", d.DURABILITY, "Glass tåler oppvaskmaskin og blir ikke matt."),
        DISHWASHER_SAFE,
    )),
    Category("kitchen", "Andre kjøkkenapparater", ("kjøkkenapparat", "kjokkenapparat", "foodprocessor", "vannkoker", "brødrister",
                                                   "kjøkkenvekt", "riskoker", "slowcooker", "sous vide", "multicooker"), rules=(
        POWER,
        rule("capacity_l", "Kapasitet (liter)", (r"^kapasitet( \(l(iter)?\))?$", r"^volum", r"^kapasitet.*liter"), "higher",
             d.CAPACITY, "Større kapasitet lager mer på én gang."),
        THERMOSTAT,
        rule("keep_warm", "Holde varm", (r"hold(e)? varm", r"varmholding"), "yes", d.FEATURES, "Holder maten eller vannet varmt."),
        rule("slots", "Antall skiver/spor", (r"^antall (skiver|spor|brødskiver)",), "higher", d.CAPACITY, "Flere skiver samtidig."),
        PROGRAMS, AUTO_OFF, DISHWASHER_SAFE,
    )),
    Category("coffee", "Kaffemaskiner og espressomaskiner", ("kaffemaskin", "espressomaskin", "helautomat", "espresso"), rules=(
        rule("type", "Type", (r"^type kaffemaskin", r"^kaffemaskintype", r"^betjening"), "info", d.FEATURES,
             "Helautomat eller manuell espressomaskin."),
        rule("grinder", "Innebygd kvern", (r"integrert kaffekvern", r"^kvern", r"kaffekvern"), "yes", d.FEATURES,
             "Ferskmalt kaffe smaker mest."),
        rule("grind_levels", "Kvernegrader", r"^antall kvernegrader", "higher", d.FEATURES, "Flere trinn gir finere justering av smaken."),
        rule("milk", "Automatisk melkesystem", (r"automatisk melkefunksjon", r"auto.?cappuccinatore", r"^melkesystem"),
             "yes", d.FEATURES, "Lager cappuccino og latte med ett trykk."),
        rule("frother", "Melkeskummer", (r"skumgenerator", r"melkeskummer", r"dampdyse", r"dampstav"), "yes", d.FEATURES,
             "Kan lage melkeskum – manuelt eller automatisk."),
        rule("pressure", "Pumpetrykk (bar)", (r"^pumpetrykk", r"^trykk", r"\bbar\b"), "higher", d.PERFORMANCE,
             "15 bar er standard (9 bar i bryggeenheten er det som teller)."),
        rule("water_tank", "Vanntank", (r"^vannbeholder", r"vanntank"), "higher", d.CAPACITY, "Sjeldnere påfylling."),
        rule("brew_group", "Avtakbar bryggeenhet", r"bryggeenhet", "yes", d.FEATURES, "Enklere rengjøring."),
        rule("rinse", "Rengjøringsprogram", (r"rengjøringsprogram", r"automatisk (skylling|rengjøring)", r"avkalk"), "yes",
             d.FEATURES, "Mindre vedlikehold."),
        rule("descale_alert", "Kalkindikator", r"kalkindikator", "yes", d.FEATURES, "Sier fra når maskinen må avkalkes."),
        rule("double_cup", "To kopper samtidig", r"enkel eller dobbel", "info", d.CAPACITY, "Dobbel trakter lager to kopper på en gang."),
        WIFI,
    )),
    # seen on Nespresso Vertuo Pop (De'Longhi ENV90): "Produktserie: Nespresso Vertuo", "Vannbeholder (I): 0.56", "Auto-av"
    Category("capsule", "Kapselmaskiner", ("kapselmaskin", "nespresso", "dolce gusto", "tassimo"), rules=(
        rule("system", "Kapselsystem", (r"^produktserie", r"kapselsystem", r"^kapseltype"), "info", d.ENERGY,
             "Bestemmer hvilke kapsler (og priser) kunden er låst til."),
        rule("milk", "Automatisk melkesystem", (r"automatisk melkefunksjon", r"^melkesystem"), "yes", d.FEATURES,
             "Lager cappuccino og latte med ett trykk."),
        rule("frother", "Melkeskummer", (r"skumgenerator", r"melkeskummer", r"aeroccino", r"dampdyse"), "yes", d.FEATURES,
             "Kan lage melkeskum."),
        rule("water_tank", "Vanntank", (r"^vannbeholder", r"vanntank"), "higher", d.CAPACITY, "Sjeldnere påfylling."),
        rule("pressure", "Pumpetrykk (bar)", (r"^pumpetrykk", r"^trykk", r"\bbar\b"), "higher", d.PERFORMANCE,
             "19 bar er vanlig for Nespresso Original; Vertuo bruker sentrifuge i stedet."),
        rule("cup_sizes", "Koppstørrelser", (r"koppstørrelse", r"antall drikker", r"programmerbare"), "higher", d.FEATURES,
             "Fra espresso til stor kopp."),
        AUTO_OFF, POWER, WIFI,
        rule("descale_alert", "Kalkindikator", r"kalkindikator", "yes", d.FEATURES, "Sier fra når maskinen må avkalkes."),
    )),
    Category("filter_coffee", "Kaffetraktere", ("kaffetrakter", "trakter", "filterkaffe", "kaffebrygger"), rules=(
        rule("cups", "Antall kopper", (r"antall kopper", r"kapasitet \(kopper\)", r"^kopper"), "higher", d.CAPACITY,
             "Hvor mye kaffe den lager på én gang."),
        rule("capacity_l", "Kapasitet (liter)", (r"^kapasitet( \(l(iter)?\))?$", r"^volum", r"^kapasitet.*liter"), "higher",
             d.CAPACITY, "Hvor mye kaffe den lager på én gang."),
        rule("thermos", "Termokanne", r"^termos", "yes", d.FEATURES, "Holder kaffen varm uten varmeplate – smaker bedre lenger."),
        rule("certified", "Godkjent (ECBC/SCA)", (r"ecbc", r"\bsca\b", r"godkjent av"), "yes", d.PERFORMANCE,
             "Uavhengig godkjent for riktig temperatur og traktetid."),
        rule("grinder", "Innebygd kvern", (r"integrert kaffekvern", r"^kvern", r"kaffekvern"), "yes", d.FEATURES,
             "Ferskmalt kaffe smaker mest."),
        TIMER,
        rule("keep_warm", "Holde varm", (r"hold(e)? varm", r"varmholding", r"varmeplate"), "yes", d.FEATURES, "Holder kaffen varm."),
        POWER, AUTO_OFF,
    )),
    Category("grinder", "Kaffekverner", ("kaffekvern", "kvern"), rules=(
        rule("burr", "Kvernetype", (r"^type kvern", r"^kvernmekanisme", r"^kverntype", r"^kvernsteiner"), "rank", d.PERFORMANCE,
             "Kvernsteiner gir jevn malegrad; knivkvern gir ujevn kaffe.", ("konisk", "flat", "stein", "kniv")),
        rule("grind_levels", "Kvernegrader", r"^antall kvernegrader", "higher", d.FEATURES, "Flere trinn gir finere justering."),
        rule("hopper", "Bønnebeholder (g)", (r"bønnebeholder", r"kapasitet bønne"), "higher", d.CAPACITY, "Sjeldnere påfylling."),
        POWER,
        rule("dosing", "Dosering/timer", (r"dosering", r"^timer", r"tidsur"), "yes", d.FEATURES, "Maler riktig mengde hver gang."),
    )),
    # seen on Oral-B iO3 and Philips Sonicare 3100/7100: "Trykkontrollsystem", "Tidskontroll", "Antall hastigheter" (= modes),
    # "Pussebevegelse pr. min.", "Reiseetui", "Skjerm", "Brukstid når fulladet (minutter)", "Ladetid i minutter".
    # Model features Elkjøp leaves out (app, smart sensor, charging case …) come from comparison/model_facts.py.
    Category("toothbrush", "Elektriske tannbørster", ("tannbørste", "tannborste", "munndusj", "sonicare", "oral-b io"), rules=(
        rule("brush_modes", "Pussemoduser", (r"^antall (pusse)?moduser", r"^pussemoduser", r"^rengjøringsmoduser", r"^antall hastigheter"),
             "higher", d.FEATURES, "Egne moduser for sensitive tenner, tannkjøtt og bleking."),
        rule("pressure_sensor", "Trykksensor", (r"trykkontroll", r"trykksensor"), "yes", d.FEATURES,
             "Sier fra når du presser for hardt – beskytter tannkjøttet."),
        rule("smart_sensor", "Smart trykksensor med lys", (r"smart trykksensor", r"lysring"), "yes", d.FEATURES,
             "Lyser rødt ved for hardt trykk og grønt ved riktig trykk."),
        rule("intensity", "Intensitetsnivåer", r"intensitet", "higher", d.FEATURES, "Juster styrken etter tennene."),
        TIMER,
        rule("app", "App med pussehjelp", (r"^app-?styring", r"^appstyrt", r"^bluetooth$"), "yes", d.CONNECTIVITY,
             "Viser hvor du har pusset og hva du har glemt."),
        rule("ai_tracking", "AI-/3D-sporing", (r"ai-?sporing", r"3d-?sporing", r"posisjonsgjenkjenning"), "yes", d.FEATURES,
             "Følger med på hvilke tenner som er pusset."),
        rule("display", "Display", (r"^skjerm$", r"^display$"), "yes", d.FEATURES, "Viser modus, tid og tilbakemelding på børsten."),
        rule("brush_reminder", "Påminnelse om børstebytte", (r"brushsync", r"børstebytte", r"påminnelse"), "yes", d.FEATURES,
             "Sier fra når børstehodet bør byttes."),
        BATTERY_LIFE, CHARGE_TIME, TRAVEL_CASE,
        rule("charging_case", "Ladende reiseetui", r"ladende reiseetui", "yes", d.PORTABILITY, "Lad børsten i etuiet – ingen lader med."),
        rule("fast_charger", "Hurtiglader", (r"hurtiglad", r"magnetisk lader"), "yes", d.BATTERY, "Full lading på kort tid."),
        rule("strokes", "Pussebevegelser per minutt", r"pussebevegelse", "info", d.PERFORMANCE,
             "Sonisk (Philips) og roterende (Oral-B) teller ulikt – kan ikke sammenlignes direkte."),
        rule("heads_included", "Børstehoder inkludert", r"medfølgende børster", "yes", d.FEATURES, "Ekstra børstehoder i esken."),
    )),
    # seen on Philips Series 7000 S7887/55: "Rense- og ladestasjon", "Vanntett", "Fleksibelt skjærehode", "Trimmer", "Brukstid".
    Category("shaver", "Barbermaskiner og trimmere", ("barbermaskin", "trimmer", "skjeggtrimmer", "oneblade", "hårklipper",
                                                      "hårtrimmer", "kroppstrimmer"), name_generations=False, rules=(
        rule("shaver_type", "Type", (r"^skjæresystem", r"^type barbermaskin", r"^skjæreteknologi"), "info", d.FEATURES,
             "Folie barberer tettest på kinnene; roterende følger kjeven bedre."),
        rule("wet_dry", "Våt og tørr", (r"^vanntett", r"^våt", r"kan brukes i dusj", r"wet"), "yes", d.FEATURES, "Kan brukes i dusjen og med skum."),
        BATTERY_LIFE, CHARGE_TIME,
        rule("clean_station", "Rense- og ladestasjon", (r"rense- og ladestasjon", r"rensestasjon", r"cleaning pod"), "yes",
             d.FEATURES, "Rengjør og lader automatisk."),
        rule("flex_head", "Fleksibelt skjærehode", r"fleksibelt skjærehode", "yes", d.PERFORMANCE, "Følger ansiktet bedre."),
        rule("trimmer", "Trimmer for kinnskjegg/bart", r"^trimmer", "yes", d.FEATURES, "Rett kanter og kinnskjegg."),
        rule("sensitive", "For sensitiv hud", r"følsom", "yes", d.FEATURES, "Mindre irritasjon."),
        rule("lengths", "Lengdeinnstillinger", (r"lengdeinnstilling", r"antall lengder", r"trinnlengder"), "higher", d.FEATURES,
             "Flere lengder for skjeggtrimming."),
        rule("display", "Display", (r"^skjerm$", r"^display$"), "yes", d.FEATURES, "Viser batteri og påminnelser."),
        TRAVEL_CASE, ACCESSORIES,
    )),
    # seen on Dyson Supersonic HD07: "Effekt (Watt): 1600", "Vifteinnstillinger: 3", "Temperaturinnstillinger: 4",
    # "Ionisk teknologi", "Kaldluft", "Spreder inkludert"
    Category("hair", "Hårfønere og hårstyling", ("hårføner", "harfoner", "føner", "foner", "glattetang", "krølltang",
                                                 "hårstyler", "airwrap", "varmebørste", "multistyler"), rules=(
        POWER,
        rule("temps", "Temperaturinnstillinger", r"^temperatur(innstillinger)?", "higher", d.FEATURES, "Flere valg gir skånsommere styling."),
        SPEEDS,
        rule("ionic", "Ioneteknologi", (r"^ione", r"\bionisk"), "yes", d.FEATURES, "Mindre krus og statisk hår."),
        rule("cold_shot", "Kaldluft", r"^kaldluft", "yes", d.FEATURES, "Låser frisyren på slutten."),
        rule("diffuser", "Diffusor inkludert", (r"spreder inkludert", r"diffus"), "yes", d.FEATURES, "Til krøller og bølger."),
        rule("heat_up", "Oppvarmingstid", r"oppvarmingstid", "lower", d.PERFORMANCE, "Klar til bruk raskere."),
        rule("plates", "Plater", (r"platemateriale", r"^plater"), "info", d.DURABILITY, "Keramikk/titan fordeler varmen jevnt."),
        rule("cord", "Ledningslengde (cm)", r"ledningslengde", "higher", d.PORTABILITY, "Lengre ledning gir mer bevegelsesfrihet."),
        ACCESSORIES, WEIGHT, AUTO_OFF,
    )),
    # seen on Braun Silk-expert Pro 5: "Hudsensor (gjenkjenner hudtype)", "Kan brukes i ansiktet", "Antall hastigheter: 3"
    Category("ipl", "IPL og epilatorer", ("ipl", "hårfjern", "harfjern", "epilator", "lysbasert"), rules=(
        rule("flashes", "Antall lysblink", (r"antall (lys)?blink", r"lysblink", r"blinkkapasitet"), "higher", d.LIFESPAN,
             "Hvor mange behandlinger lampen holder til."),
        rule("skin_sensor", "Hudsensor", r"hudsensor", "yes", d.FEATURES, "Tilpasser styrken til hudtonen – tryggere."),
        rule("face", "Kan brukes i ansiktet", r"i ansiktet", "yes", d.FEATURES, "Egnet for overleppe og hake."),
        rule("sensitive_areas", "Sensitive områder", r"sensitive områder", "yes", d.FEATURES, "Armhuler og bikinilinje."),
        rule("intensity", "Intensitetsnivåer", (r"intensitet", r"^antall hastigheter", r"^energinivå"), "higher", d.FEATURES,
             "Flere nivåer gir bedre tilpasning."),
        rule("tweezers", "Antall pinsetter", r"pinsett", "higher", d.PERFORMANCE, "Flere pinsetter tar flere hår per drag."),
        rule("wet_dry", "Våt og tørr", (r"^vanntett", r"^våt", r"wet"), "yes", d.FEATURES, "Kan brukes i dusjen."),
        CORDLESS, ACCESSORIES, TRAVEL_CASE,
    )),
    Category("scale", "Badevekter", ("badevekt", "personvekt", "kroppsanalysevekt", "smartvekt"), rules=(
        rule("body_analysis", "Kroppsanalyse", (r"kroppsanalyse", r"kroppsfett", r"muskelmasse", r"\bbmi\b"), "yes", d.FEATURES,
             "Måler mer enn vekt – fett, muskler og vann."),
        rule("users", "Antall brukere", r"antall brukere", "higher", d.CAPACITY, "Hele familien kan bruke den."),
        MAX_LOAD, APP, WIFI,
        rule("precision", "Nøyaktighet", (r"nøyaktighet", r"inndeling", r"presisjon"), "info", d.PERFORMANCE, "100 g er vanlig."),
    )),
    # seen on Samsung Bespoke Jet: "Brukertid, minimumskapasitet (min)", "Ladetid i timer", "Maks effekt (watt)",
    # "Filtreringssystem: Poseløs", "Optimalisert for dyrehår", "Regjøringsbredde (mm)" (sic), "Lydnivå (dB)"
    Category("vacuum", "Støvsugere", ("støvsuger", "stovsuger", "stangstøvsuger", "skaftstøvsuger", "håndstøvsuger",
                                      "trådløs støvsuger", "stick", "våtsuger", "våt-/tørrsuger"), rules=(
        rule("type", "Type", (r"^støvsugertype", r"^type støvsuger", r"^produkttype"), "info", d.FEATURES,
             "Ledningsfri, med ledning, med pose eller uten."),
        rule("suction", "Sugeeffekt", (r"sugeeffekt", r"sugekraft", r"sugestyrke", r"air ?watt", r"vakuumtrykk", r"\(pa\)"),
             "higher", d.PERFORMANCE, "Ledningsfri oppgis ofte i AW – høyere trekker opp mer fra tepper."),
        POWER, RUNTIME, CHARGE_TIME,
        rule("removable_battery", "Utskiftbart batteri", (r"avtagbart batteri", r"utskiftbart batteri", r"byttbart batteri"), "yes",
             d.LIFESPAN, "Batteriet kan byttes når det blir dårlig – eller ha et ekstra."),
        rule("bagless", "Pose eller beholder", (r"^filtreringssystem", r"^posetype", r"poseløs"), "info", d.ENERGY,
             "Poseløs sparer poser; pose er bedre for allergikere ved tømming."),
        rule("dust", "Støvbeholder", (r"kapasitet støvbeholder", r"^støvbeholder", r"^beholdervolum", r"^støvkapasitet"),
             "higher", d.CAPACITY, "Sjeldnere tømming."),
        rule("hepa", "HEPA-filter", r"hepa", "yes", d.FEATURES, "Viktig for allergikere."),
        rule("pet", "Laget for dyrehår", (r"dyrehår", r"pet"), "yes", d.FEATURES, "Egen børste som ikke floker seg."),
        rule("dust_sensor", "Støvsensor", (r"støvsensor", r"piezo", r"partikkelsensor"), "yes", d.FEATURES,
             "Øker kraften automatisk der det er skittent."),
        rule("standalone", "Står av seg selv", r"selvstående", "yes", d.FEATURES, "Kan settes fra seg uten å falle."),
        rule("clean_width", "Rengjøringsbredde (mm)", (r"re?n?gjøringsbredde",), "higher", d.PERFORMANCE, "Bredere munnstykke = raskere ferdig."),
        rule("washable_filter", "Vaskbart filter", r"vaskbart filter", "yes", d.ENERGY, "Slipper å kjøpe nye filtre."),
        NOISE, WEIGHT,
    )),
    # seen on Roborock Saros 20 Sonic and Dreame X60 Pro Ultra.
    Category("robot_vacuum", "Robotstøvsugere", ("robotstøvsuger", "robotstovsuger", "rengjøringsrobot", "robot"), rules=(
        rule("suction", "Sugeeffekt", (r"vakuumtrykk", r"sugeeffekt", r"sugekraft", r"sugestyrke", r"\(pa\)", r"air ?watt"),
             "higher", d.PERFORMANCE, "Oppgis i Pa – høyere trekker opp mer fra tepper og sprekker."),
        BATTERY_LIFE,
        rule("navigation", "Navigasjon", r"navigasjon", "rank", d.PERFORMANCE, "LiDAR navigerer best.",
             ("lidar", "laser", "kamera", "gyro")),
        rule("mop_type", "Moppesystem", r"^type moppesystem", "info", d.FEATURES,
             "Roterende eller vibrerende mopper skrubber bedre enn en klut som bare dras over gulvet."),
        rule("mop", "Moppefunksjon", (r"moppefunksjon", r"^mopp", r"våtvask"), "yes", d.FEATURES, "Vasker gulvet i samme runde."),
        rule("water_tank", "Vanntank", (r"kapasitet vannbeholder", r"vanntank", r"vannbeholder"), "higher", d.CAPACITY,
             "Større vanntank vasker større areal før påfylling."),
        rule("auto_empty", "Tømmestasjon", (r"automatisk tømme", r"tømmestasjon", r"selvtømm", r"auto.?tøm"), "yes", d.FEATURES,
             "Tømmer seg selv i flere uker. «Med tilbehør» betyr at stasjonen må kjøpes i tillegg."),
        rule("obstacle", "Hindringsgjenkjenning", (r"hindring", r"objektgjenkjenning"), "yes", d.FEATURES,
             "Unngår ledninger, sokker og dyrebæsj."),
        rule("hepa", "HEPA-filter", r"hepa", "yes", d.FEATURES, "Viktig for allergikere."),
        # info, not higher: Elkjøp mixes the robot's own bin (0,31 l) with the dock's bag (2,5 l).
        rule("robot_dust", "Støvbeholder", (r"kapasitet støvbeholder", r"^støvbeholder", r"^beholdervolum", r"^støvkapasitet"),
             "info", d.CAPACITY, "Kan være robotens egen beholder eller posen i stasjonen – sjekk hva som menes."),
        NOISE, APP,
    )),
    # seen on Electrolux Flow A3: "Anbefalt romstørrelse (maks kvm)", "CADR Røyk", "HEPA filter (…)", "Lydnivå, Lav/Høy (dB)"
    Category("air_purifier", "Luftrensere", ("luftrenser", "luftrensere", "air purifier"), rules=(
        ROOM_SIZE,
        rule("cadr", "Rensekapasitet CADR (m³/t)", (r"^cadr røyk", r"^cadr"), "higher", d.PERFORMANCE,
             "Hvor mye ren luft den leverer – høyere renser rommet raskere."),
        rule("hepa", "HEPA-filter", r"hepa", "yes", d.FEATURES, "Fanger pollen, støv og dyrehår – viktig for allergikere."),
        rule("carbon", "Aktivt kullfilter", (r"karbonfilter", r"kullfilter"), "yes", d.FEATURES, "Fjerner lukt og gasser."),
        rule("aq_sensor", "Luftkvalitetssensor", (r"måler luftkvalitet", r"luftkvalitetssensor", r"pm2"), "yes", d.FEATURES,
             "Justerer seg selv etter luften i rommet."),
        NOISE_LOW, NOISE_HIGH,
        rule("power_use", "Strømforbruk (kWh/time)", r"strømforbruk \(kwh", "lower", d.ENERGY, "Går ofte døgnet rundt – lavt forbruk teller."),
        rule("filter_alert", "Filterbytte-varsel", r"filterbytte", "yes", d.FEATURES, "Sier fra når filteret må byttes."),
        rule("night_mode", "Nattmodus", r"nattmodus", "yes", d.NOISE, "Stille og uten lys om natten."),
        APP, SPEEDS,
    )),
    # seen on Apt avfukter: "Avfukter (liter per døgn): 12", "Vanntank (I): 2", "Lavest mulige romtemperatur: 5"
    Category("dehumidifier", "Avfuktere", ("avfukter", "luftavfukter"), rules=(
        rule("dehum_capacity", "Avfukting (liter per døgn)", (r"liter per døgn", r"avfuktingskapasitet", r"^avfukter \("), "higher",
             d.PERFORMANCE, "Hvor mye fukt den trekker ut per døgn."),
        ROOM_SIZE,
        rule("water_tank", "Vanntank", (r"^vanntank", r"beholder avløpsvann", r"vannbeholder"), "higher", d.CAPACITY, "Sjeldnere tømming."),
        rule("drain", "Kontinuerlig drenering", (r"avløp-?/?utluftsslange", r"kontinuerlig drenering", r"slangetilkobling"), "yes",
             d.FEATURES, "Koble til sluk – slipper å tømme tanken."),
        rule("min_temp", "Laveste driftstemperatur (°C)", r"lavest mulige romtemperatur", "lower", d.PERFORMANCE,
             "Lavt tall betyr at den virker i kalde rom som kjeller og hytte."),
        rule("tech", "Teknologi", (r"^teknologi", r"tørkerotor", r"kompressor", r"adsorpsjon"), "info", d.FEATURES,
             "Kompressor er best i varme rom; tørkerotor er best i kalde."),
        rule("humidistat", "Hygrostat", (r"hygrostat", r"fuktighetsmåler", r"ønsket fuktighet"), "yes", d.FEATURES,
             "Holder fuktigheten på nivået du velger."),
        NOISE_HIGH,
        rule("auto_stop", "Stopper når tanken er full", r"skrur seg automatisk av ved full", "yes", d.FEATURES, "Ingen søl."),
        WIFI,
    )),
    Category("fan", "Vifter", ("vifte", "bordvifte", "gulvvifte", "tårnvifte", "takvifte"), rules=(
        POWER, SPEEDS,
        rule("oscillation", "Svingfunksjon", (r"^svingfunksjon", r"^oscillerende", r"oscillering"), "yes", d.FEATURES,
             "Sprer luften i hele rommet."),
        NOISE,
        rule("remote", "Fjernkontroll", r"^fjernkontroll", "yes", d.FEATURES, "Styr den fra sofaen eller senga."),
        TIMER,
        rule("heater_combo", "Varmefunksjon", (r"varmefunksjon", r"varmeelement"), "yes", d.FEATURES, "Kan også varme om vinteren."),
        rule("diameter", "Diameter/høyde", (r"diameter", r"^høyde \(cm\)"), "info", d.CAPACITY, "Større vifte flytter mer luft."),
        APP,
    )),
    # seen on Adax Neo Basic: "Effekt (watt): 1000", "Termostat: Digital", "Anbefalt romstørrelse (maks kvm): 16"
    Category("heater", "Panelovner og varmeovner", ("panelovn", "varmeovn", "oljeovn", "varmevifte", "terrassevarmer",
                                                    "konvektor", "oljefylt radiator"), rules=(
        POWER, ROOM_SIZE,
        rule("thermostat_type", "Termostat", r"^termostat", "rank", d.ENERGY, "Digital termostat holder jevnere temperatur og sparer strøm.",
             ("digital", "elektronisk", "mekanisk")),
        rule("energy_saving", "Sparefunksjon", (r"spareplugg", r"ukeprogram", r"nattsenking", r"sparefunksjon"), "yes", d.ENERGY,
             "Senker temperaturen automatisk om natten eller når du er borte."),
        APP, WIFI,
        rule("wet_room", "Kan brukes i våtrom", r"våtrom", "yes", d.DURABILITY, "Trygg på bad og vaskerom."),
        IP_RATING,
        rule("child_lock", "Barnesikring", r"barnesikring", "yes", d.FEATURES, "Låser innstillingene."),
        rule("tip_over", "Veltesikring", (r"fallsikkerhet", r"veltesikring", r"tippesikring"), "yes", d.DURABILITY,
             "Slår seg av hvis den velter."),
    )),
    Category("air_conditioner", "Aircondition og portable varmepumper",
             ("aircondition", "air condition", "klimaanlegg", "portabel varmepumpe", "mobil aircondition", "luftkjøler"), rules=(
        rule("cool_power", "Kjøleeffekt", (r"kjøleeffekt", r"kjølekapasitet", r"\bbtu\b"), "higher", d.PERFORMANCE,
             "Høyere effekt kjøler større rom."),
        rule("heating", "Varmeeffekt", (r"varmeeffekt", r"varmekapasitet"), "higher", d.PERFORMANCE, "Kan også varme om vinteren."),
        ROOM_SIZE, ENERGY, NOISE,
        rule("dehum_mode", "Avfuktingsfunksjon", r"avfukt", "yes", d.FEATURES, "Tørker luften på fuktige dager."),
        rule("hose", "Avtrekksslange", (r"avløp-?/?utluftsslange", r"utblåsningsslange", r"slange"), "info", d.FEATURES,
             "Slangen må ut av et vindu."),
        APP, WIFI, TIMER,
    )),
    Category("emobility", "Elsparkesykler og elsykler", ("sparkesykkel", "elsykkel", "el-sparkesykkel", "elsparkesykkel"), rules=(
        rule("range", "Rekkevidde (km)", r"rekkevidde", "higher", d.BATTERY, "Reell rekkevidde er ofte 60–70 % av oppgitt."),
        rule("motor", "Motoreffekt (W)", (r"^motoreffekt", r"^motor"), "higher", d.PERFORMANCE, "Mer effekt tar bakker bedre."),
        rule("speed", "Toppfart", (r"toppfart", r"^maks.*hastighet"), "info", d.PERFORMANCE,
             "Lovlig maks i Norge: 20 km/t (sparkesykkel), 25 km/t (elsykkel)."),
        WEIGHT, MAX_LOAD,
        rule("tyres", "Dekk", r"^dekk", "info", d.DURABILITY, "Luftfylte dekk gir mer komfort."),
        rule("suspension", "Demping", (r"demping", r"fjæring"), "yes", d.FEATURES, "Mykere tur på dårlig vei."),
        rule("brakes", "Bremser", r"brems", "info", d.DURABILITY, "Skivebremser er best."),
        IP_RATING,
    )),
)

BY_ID = {category.id: category for category in CATEGORIES}

# ------------------------------------------------------------------ families
# Categories customers often weigh against each other. Products in the same
# family are compared on the specs they share (with a note). Products from
# unrelated categories are not compared at all – the app offers a
# side-by-side overview without winners instead. A category may sit in
# several families. Checked by validation.py.
FAMILIES: tuple[tuple[str, ...], ...] = (
    ("laptop", "tablet", "desktop"),
    ("mobile", "tablet"),
    ("tv", "monitor", "projector"),
    ("soundbar", "speaker", "pc_speaker"),
    ("oven", "microwave", "airfryer"),
    ("oven", "hob"),
    ("kitchen_machine", "blender", "stick_mixer", "kitchen"),
    ("airfryer", "kitchen", "sandwich"),
    ("washer", "washer_dryer", "dryer"),
    ("fridge", "american_fridge", "wine_fridge"),
    ("coffee", "capsule", "filter_coffee"),
    ("coffee", "grinder"),
    ("vacuum", "robot_vacuum"),
    ("air_purifier", "dehumidifier", "fan", "air_conditioner"),
    ("heater", "air_conditioner", "fan"),
    ("shaver", "ipl"),
    ("controller", "racing"),
    ("mouse", "keyboard"),
)
