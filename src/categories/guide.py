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
                r"^lagringskapasitet ssd", r"^lagring( \(gb\))?$"),
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
BRIGHTNESS = rule("brightness", "Lysstyrke (nits)", (r"^nits?$", r"^lysstyrke(?!.*score)", r"cd/m"),
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
               (r"programvareoppdatering", r"sikkerhetsoppdatering", r"os-oppdatering", r"^oppdateringer"),
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
POWER = rule("power_w", "Effekt (W)", (r"^effekt( \(w(att)?\))?$", r"^motorkraft", r"^motoreffekt", r"^watt"),
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

# ------------------------------------------------------------------ categories
CATEGORIES: tuple[Category, ...] = (
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
        # seen: "Opptaksoppløsning: 8K UHD (4320p)" and "Videoopptak: Ja" (the Ja is skipped by fit())
        rule("video", "Video", (r"^opptaksoppløsning", r"^videooppløsning", r"^videoopptak"), "info", d.CAMERA,
             "4K 60 fps gir skarp og jevn video."),
        UPDATES, IP_RATING,
        rule("5g", "5G", r"^5g", "yes", d.FEATURES, "Raskere mobilnett der det er dekning."),
        rule("esim", "eSIM", r"esim", "yes", d.FEATURES, "Bytt abonnement uten fysisk SIM-kort."),
        rule("nfc", "NFC (mobilbetaling)", r"\bnfc\b", "yes", d.FEATURES, "Betal med telefonen."),
        CHARGER,
    )),
    Category("tablet", "Nettbrett", ("nettbrett", "ipad", "tablet"), name_generations=True, rules=(
        PROCESSOR, RAM, STORAGE, SCREEN_SIZE, RESOLUTION, DISPLAY_TYPE, REFRESH,
        rule("memory_card", "Minnekortleser", (r"^minnekort", r"microsd"), "yes", d.CAPACITY, "Utvid lagringen billig."),
        rule("pen", "Pennstøtte", (r"penn", r"stylus"), "yes", d.FEATURES, "Notater og tegning med penn."),
        rule("cellular", "Mobilnett (4G/5G)", (r"^mobilnett", r"^5g", r"^4g", r"\blte\b"), "yes", d.CONNECTIVITY,
             "Internett uten Wi-Fi – på hytta og på farten."),
        BATTERY_LIFE, FAST_CHARGE, WEIGHT, UPDATES,
    )),
    Category("watch", "Smartklokker og aktivitetsarmbånd",
             ("smartklokke", "aktivitetsarmbånd", "smartwatch", "apple watch", "treningsklokke", "pulsklokke"),
             name_generations=True, rules=(
        rule("compatibility", "Kompatibilitet", (r"kompatib", r"operativsystem"), "info", d.CONNECTIVITY,
             "Sjekk at klokka fungerer med telefonen kunden har."),
        BATTERY_LIFE,
        rule("ecg", "EKG", (r"\bekg\b", r"\becg\b"), "yes", d.FEATURES, "Kan oppdage uregelmessig hjerterytme."),
        rule("spo2", "Blodoksygen (SpO2)", (r"spo2", r"oksygen"), "yes", d.FEATURES, "Måler oksygennivå i blodet."),
        rule("sleep", "Søvnmåling", r"søvn", "yes", d.FEATURES, "Følger med på søvnkvalitet."),
        rule("gps", "GPS", r"\bgps\b", "yes", d.FEATURES, "Måler tur og løp uten mobilen."),
        rule("lte", "LTE/eSIM", (r"\blte\b", r"esim", r"^mobilnett"), "yes", d.CONNECTIVITY, "Ring og bruk data uten mobilen."),
        rule("water_resist", "Vanntetthet", (r"vanntett", r"\batm\b", r"vannmotstand", r"vannavvis", r"^ip-?klass"), "rank", d.DURABILITY,
             "5 ATM eller mer for svømming.", ("10 atm", "5 atm", "ip68", "3 atm")),
    )),
    Category("headphones", "Hodetelefoner og øreplugger",
             ("hodetelefon", "øreplugg", "airpods", "earbuds", "øretelefon"), name_generations=True, rules=(
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
    Category("laptop", "Bærbare PC-er", ("bærbar", "barbar", "laptop", "macbook", "chromebook"), rules=(
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
    # seen on PCSpecialist Prime 400 and Lenovo Legion Tower 5: GPU first – it decides gaming performance.
    Category("desktop", "Stasjonære PC-er", ("stasjonær", "stasjonar", "gaming-pc", "desktop", "gamingpc"), rules=(
        GPU, VRAM, PROCESSOR, CORES, RAM, RAM_MAX, STORAGE,
        rule("psu", "Strømforsyning (W)", (r"^strømforsyning( \(watt\))?$", r"^strømforsyning", r"\bpsu\b"), "higher",
             d.LIFESPAN, "Mer effekt gir rom for et kraftigere grafikkort senere."),
        rule("cooling", "Kjøling", (r"^type avkjøling", r"kjøling"), "info", d.NOISE,
             "Vannkjøling er ofte stillere under full belastning; god luftkjøling holder for de fleste."),
        rule("wifi_std", "Wi-Fi-standard", r"^wifi-standard", "rank", d.CONNECTIVITY, "Nyere Wi-Fi gir raskere og mer stabilt nett.",
             ("wi-fi 7", "wi-fi 6e", "wi-fi 6", "wi-fi 5")),
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
        rule("displayport", "DisplayPort", r"displayport", "yes", d.CONNECTIVITY, "Best for høy Hz på PC."),
        rule("usbc_pd", "USB-C med lading", (r"usb-c power delivery", r"power delivery", r"^usb-c"), "yes", d.CONNECTIVITY,
             "Én kabel til laptopen – bilde og strøm."),
        rule("height_adjust", "Høydejustering", r"høydejuster", "yes", d.FEATURES, "Bedre ergonomi."),
    )),
    Category("printer", "Skrivere", ("skriver", "printer", "blekk"), rules=(
        rule("type", "Skrivertype", (r"^skrivertype", r"^utskriftsteknologi"), "info", d.FEATURES,
             "Blekk for bilder, laser for mye tekst."),
        rule("ink_tank", "Blekktank", (r"blekktank", r"ecotank"), "yes", d.ENERGY, "Mye lavere kostnad per side."),
        rule("page_cost", "Kostnad per side (kr)", (r"kostnad per side", r"sidepris"), "lower", d.ENERGY,
             "Driftskostnaden er ofte viktigere enn innkjøpsprisen."),
        rule("duplex", "Tosidig utskrift", (r"tosidig", r"dupleks"), "yes", d.FEATURES, "Sparer papir."),
        rule("scan", "Skanner", r"skann", "yes", d.FEATURES, "Skann og kopier."),
        WIFI,
    )),
    # seen on LG 65" B5: Panelteknologi, Størrelse (tommer), Oppløsning, Bildepanelfrekvens (Hz),
    # "High Dynamic Range (HDR) standard: Dolby Vision", Antall HDMI-innganger, HDMI-standard,
    # Variable Refresh Rate (VRR), Smart-TV-plattform, Lydeffekt (watt), Elkjøp's own panel scores.
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
        rule("sound_w", "Lydeffekt (W)", (r"^lydeffekt", r"utgangseffekt", r"høyttalereffekt"), "higher", d.SOUND,
             "De fleste TV-er har nytte av en lydplanke uansett."),
        ATMOS, ENERGY, ENERGY_YEAR,
    )),
    Category("soundbar", "Lydplanker og høyttalere", ("lydplanke", "soundbar", "høyttaler", "hoyttaler"), rules=(
        rule("channels", "Kanaler", (r"^kanaler", r"kanalkonfig"), "info", d.SOUND, "Flere kanaler gir mer surround; «.2» = lyd ovenfra."),
        ATMOS,
        rule("dtsx", "DTS:X", r"dts:?x", "yes", d.SOUND, "Alternativ surroundformat."),
        rule("subwoofer", "Subwoofer", (r"subwoofer", r"basselement"), "info", d.SOUND, "Egen subwoofer gir mye mer bass."),
        rule("earc", "HDMI eARC", (r"earc", r"hdmi arc"), "yes", d.CONNECTIVITY, "Den beste og enkleste koblingen til TV-en."),
        WIFI, BLUETOOTH,
        rule("airplay", "AirPlay", r"airplay", "yes", d.CONNECTIVITY, "Strøm lyd fra Apple-enheter."),
        rule("chromecast", "Chromecast", r"chromecast", "yes", d.CONNECTIVITY, "Strøm lyd fra Android/apper."),
        BATTERY_LIFE, IP_RATING,
    )),
    Category("gaming", "Gaming", ("spillkonsoll", "konsoll", "playstation", "xbox", "nintendo", "gamingmus",
                                  "gamingtastatur", "gaming-headset", "spill"), name_generations=True, rules=(
        rule("edition", "Utgave", (r"^utgave", r"^diskstasjon"), "info", d.FEATURES, "Disk eller digital utgave."),
        STORAGE,
        rule("dpi", "Sensor (DPI)", r"\bdpi\b", "higher", d.PERFORMANCE, "Høyere DPI gir mer presis mus."),
        rule("connection", "Tilkobling", (r"^tilkoblingstype", r"^tilkobling$"), "info", d.CONNECTIVITY,
             "Kablet har lavest forsinkelse; god trådløs er nesten like rask."),
        rule("switch", "Brytertype", (r"^brytertype", r"switch"), "info", d.FEATURES, "Påvirker følelse og lyd i tastaturet."),
        WEIGHT,
        rule("platform", "Plattform", (r"^plattform", r"kompatib"), "info", d.CONNECTIVITY, "Sjekk at det passer din konsoll/PC."),
    )),
    Category("camera", "Kameraer", ("kamera", "speilrefleks", "systemkamera", "kompaktkamera"), name_generations=True, rules=(
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
    Category("fridge", "Kjøleskap og frysere", ("kjøleskap", "kjoleskap", "fryser", "kombiskap", "fryseboks"), rules=(
        rule("volume", "Totalvolum (liter)", (r"^totalvolum", r"^nettovolum(?!.*(kjøl|frys))", r"^volum", r"^kapasitet.*liter"),
             "higher", d.CAPACITY, "Kjøl: 50–100 L per person. Frys: ca. 50 L + 30 L per ekstra person."),
        rule("fridge_volume", "Kjølevolum (liter)", (r"kjøl.*volum", r"volum.*kjøl"), "higher", d.CAPACITY, "Plass til ferskvarer."),
        rule("freezer_volume", "Frysevolum (liter)", (r"frys.*volum", r"volum.*frys"), "higher", d.CAPACITY, "Plass til frysevarer."),
        ENERGY, ENERGY_YEAR, NOISE,
        rule("zero_zone", "Nullsone", (r"nullsone", r"0 ?°c", r"fresh ?zone", r"vitafresh"), "yes", d.FEATURES,
             "Kjøtt og fisk holder seg lenger."),
        rule("nofrost", "NoFrost", (r"no ?frost", r"frostfri"), "yes", d.FEATURES, "Slipper å avrime fryseren."),
        rule("height", "Høyde (cm)", r"^høyde \(cm\)", "info", d.CAPACITY, "Sjekk at den passer plassen."),
        rule("install", "Installasjon", (r"^installasjon", r"^monteringstype", r"^type kjøleskap"), "info", d.FEATURES,
             "Frittstående eller integrert."),
        rule("door", "Omhengslbar dør", (r"omhengsl", r"reversibel", r"dørhengsel"), "yes", d.FEATURES,
             "Døren kan åpnes fra den siden som passer kjøkkenet."),
    )),
    Category("oven", "Stekeovner og platetopper", ("stekeovn", "platetopp", "induksjon", "komfyr", "koketopp"), rules=(
        rule("oven_volume", "Ovnsvolum (liter)", (r"^ovnsvolum", r"^volum", r"^kapasitet.*liter"), "higher", d.CAPACITY,
             "Ca. 70 L+ er standard; mer gir plass til flere brett."),
        rule("cleaning", "Selvrens", (r"^selvrens", r"^rengjøring", r"rensefunksjon"), "rank", d.FEATURES,
             "Pyrolyse brenner bort fett – enklest å holde ren.", ("pyrolyse", "katalyse", "damp")),
        rule("hot_air", "Varmluft", r"varmluft", "yes", d.FEATURES, "Jevn varme på flere brett."),
        rule("steam", "Damp", r"damp", "yes", d.FEATURES, "Bedre brød og saftigere kjøtt."),
        rule("probe", "Steketermometer", (r"steketermometer", r"kjernetemperatur"), "yes", d.FEATURES,
             "Perfekt stek uten gjetting."),
        ENERGY,
        rule("hob_type", "Platetopp-type", (r"^platetopptype", r"^koketopptype", r"^type (plate|koke)topp", r"^varmeteknologi"), "rank",
             d.PERFORMANCE, "Induksjon er raskest og mest effektiv.", ("induksjon", "keramisk")),
        rule("zones", "Antall kokesoner", (r"^antall (kokesoner|soner|kokeplater)",), "higher", d.CAPACITY, "Flere gryter samtidig."),
        rule("flex", "Fleksible soner", (r"flexi", r"bridge", r"fleksib"), "yes", d.FEATURES, "Plass til store panner og grillplater."),
        rule("booster", "Booster", (r"booster", r"powerboost"), "yes", d.PERFORMANCE, "Koker opp vann ekstra raskt."),
        rule("fuse", "Sikring", (r"^sikring", r"ampere"), "info", d.FEATURES, "Sjekk at sikringen hjemme passer (f.eks. 16A vs 2x16A)."),
    )),
    Category("washer", "Vaskemaskiner", ("vaskemaskin", "vaske-/tørkemaskin", "vasketørker"), rules=(
        # seen on ASKO W3096RW: "Kapasitet vaskesyklus (kg)", "Sentrifugehastighet (o/min)",
        # "Luftbåren akustisk lydutslipp sentrifugeringsfase (dB)", "Vektet vannforbruk vaskesyklus (liter/syklus)"
        rule("capacity_kg", "Kapasitet (kg)", (r"^kapasitet.*kg", r"^vaskekapasitet", r"^maks.*(last|fylling)"), "higher", d.CAPACITY,
             "Familie på fire: 8–9 kg. Mindre husstand: 6–7 kg."),
        rule("spin", "Sentrifuge (o/min)", (r"sentrifug", r"o/min", r"^turtall"), "higher", d.PERFORMANCE,
             "1400–1600 o/min gir tørrere klær og kortere tørketid."),
        ENERGY, NOISE,
        rule("water", "Vannforbruk (liter per vask)", (r"vannforbruk",), "lower", d.ENERGY, "Lavere forbruk sparer vann og strøm."),
        ENERGY_YEAR,
        rule("auto_dose", "Automatisk dosering", (r"dosering", r"autodos"), "yes", d.FEATURES, "Sparer vaskemiddel."),
        rule("steam", "Dampprogram", r"damp", "yes", d.FEATURES, "Mindre krøll og lukt."),
        PROGRAMS, WIFI,
    )),
    # seen on LG RV9DN902B: "Type tørketrommel: Kondens" + "Varmepumpeteknologi: Ja" – a heat pump dryer is
    # also a condenser dryer, so heat pump is its own yes-rule and the type is info.
    Category("dryer", "Tørketromler", ("tørketrommel", "torketrommel", "tørketromler"), rules=(
        rule("heat_pump", "Varmepumpe", (r"^varmepumpe",), "yes", d.ENERGY,
             "Varmepumpe bruker opptil halvparten så mye strøm og er skånsom mot klærne."),
        rule("tech", "Type", (r"^type tørketrommel", r"^tørketeknologi", r"^tørkemetode"), "info", d.FEATURES,
             "Kondens eller ventilasjon – varmepumpe er alltid kondens."),
        rule("capacity_kg", "Kapasitet (kg)", (r"^tørkekapasitet", r"^kapasitet.*kg"), "higher", d.CAPACITY,
             "Bør være minst like stor som vaskemaskinen."),
        ENERGY, ENERGY_YEAR, NOISE,
        rule("moisture", "Fuktsensor", (r"fuktsensor", r"fuktighetssensor", r"^tørkesystem", r"sensortørk"), "yes", d.FEATURES,
             "Stopper automatisk når tøyet er tørt."),
        rule("drain", "Kan kobles til avløp", (r"kobles til avløp", r"avløp", r"tømmeslange", r"drenering"), "yes", d.FEATURES,
             "Slipper å tømme vanntanken."),
        rule("steam", "Dampfunksjon", r"^damp", "yes", d.FEATURES, "Mindre krøll – kan erstatte stryking."),
        WIFI,
    )),
    Category("dishwasher", "Oppvaskmaskiner", ("oppvaskmaskin",), rules=(
        # seen on Asko DBI8557MIMXXLS: all labels below
        rule("place_settings", "Antall kuverter", r"kuvert", "higher", d.CAPACITY, "13–15 er standard for 60 cm."),
        rule("cutlery", "Bestikkplassering", r"^bestikk", "rank", d.FEATURES, "Bestikkskuff øverst frigjør plass i kurvene.",
             ("skuff", "kurv")),
        rule("basket_adjust", "Høydejusterbar overkurv", (r"høydejustering på øvre", r"justerbar (over|øvre)"), "yes", d.FEATURES,
             "Plass til høye glass og store kjeler."),
        NOISE, ENERGY,
        rule("water", "Vannforbruk (liter per vask)", (r"vannforbruk",), "lower", d.ENERGY, "Lavere forbruk sparer vann og strøm."),
        rule("install", "Installasjonstype", (r"^type oppvaskmaskin", r"^installasjon"), "info", d.FEATURES,
             "Helintegrert, semi-integrert, underbygd eller frittstående."),
        rule("width", "Bredde (cm)", r"^bredde \(cm\)", "info", d.CAPACITY, "45 eller 60 cm – må passe hullet."),
        rule("auto_open", "Automatisk døråpning", (r"automatisk åpning", r"autoopen", r"zeolit"), "yes", d.PERFORMANCE,
             "Gir mye bedre tørkeresultat."),
        PROGRAMS, WIFI,
    )),
    # seen on Roborock Saros 20 Sonic and Dreame X60 Pro Ultra: Maks vakuumtrykk (Pa),
    # Brukstid når fulladet (minutter), Kapasitet støvbeholder (l), Kapasitet vannbeholder (ml),
    # Type moppesystem, Navigasjonssystem, Automatisk tømmefunksjon ("Ja, med tilbehør"), Lydnivå (dB)
    Category("vacuum", "Støvsugere og robotstøvsugere",
             ("støvsuger", "stovsuger", "robotstøvsuger", "rengjøringsrobot"), rules=(
        rule("type", "Type", (r"^støvsugertype", r"^type støvsuger"), "info", d.FEATURES, "Ledningsfri, med pose/beholder eller robot."),
        rule("suction", "Sugeeffekt", (r"vakuumtrykk", r"sugeeffekt", r"sugekraft", r"sugestyrke", r"\(pa\)", r"air ?watt"),
             "higher", d.PERFORMANCE, "Robot: Pa. Ledningsfri: AW. Høyere trekker opp mer fra tepper og sprekker."),
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
        rule("dust", "Støvbeholder", (r"kapasitet støvbeholder", r"^støvbeholder", r"^beholdervolum", r"^støvkapasitet"),
             "info", d.CAPACITY, "Kan være robotens egen beholder eller posen i stasjonen – sjekk hva som menes."),
        NOISE,
    )),
    # seen on Melitta Caffeo Solo & Perfect Milk: "Betjening: Automatisk", "Pumpetrykk (Bar)", "Integrert kaffekvern",
    # "Antall kvernegrader", "Automatisk melkefunksjon", "Skumgenerator", "Vannbeholder (I)", "Rengjøringsprogram"
    Category("coffee", "Kaffemaskiner", ("kaffemaskin", "espressomaskin", "kaffetrakter", "kapselmaskin"), rules=(
        rule("type", "Type", (r"^type kaffemaskin", r"^kaffemaskintype", r"^betjening"), "info", d.FEATURES,
             "Helautomat, manuell espresso, kapsel eller filter."),
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
        WIFI,
    )),
    # seen on Bosch MUMS6ZS18 and Kenwood KVL85.004SI: Motorkraft (Watt), Bollevolum (Itr),
    # Kapasitet (kg), Antall boller, Hastighetinnstillinger, Turbo-/pulsknapp,
    # Antall uttak for tilbehør, Materiale. Scale/timer/display/programs are
    # only in the description → found by comparison/fallback_extractor.py.
    Category("kitchen_machine", "Kjøkkenmaskiner", ("kjøkkenmaskin", "kjokkenmaskin", "stand mixer"), rules=(
        rule("motor_power", "Motorkraft (W)", (r"^motorkraft", r"^motoreffekt", r"^effekt( \(w(att)?\))?$"), "higher",
             d.PERFORMANCE, "Mer effekt hjelper i tung deig – men girkasse og konstruksjon betyr også mye."),
        rule("bowl_volume", "Bollevolum (liter)", (r"^bollevolum", r"^bollestørrelse", r"^volum"), "higher", d.CAPACITY,
             "Større bolle gir plass til større porsjoner."),
        rule("dough_capacity", "Deigkapasitet (kg)", r"^kapasitet \(kg\)", "higher", d.CAPACITY,
             "Hvor mye deig maskinen er laget for å elte på én gang."),
        rule("bowls", "Antall boller", r"^antall boller", "higher", d.CAPACITY,
             "To boller lar deg bytte oppskrift uten å vaske imellom."),
        rule("speeds", "Hastighetstrinn", r"^hastighet\w*innstillinger", "higher", d.FEATURES,
             "Flere trinn gir bedre kontroll fra forsiktig blanding til hard pisking."),
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
    Category("airfryer", "Airfryere", ("airfryer", "air fryer", "varmluftsfriteres"), rules=(
        rule("capacity_l", "Kapasitet (liter)", (r"^kapasitet( \(l(iter)?\))?$", r"^kurvvolum", r"^volum", r"^kapasitet.*liter"),
             "higher", d.CAPACITY, "Ca. 1 liter per person er en grei tommelfingerregel."),
        rule("baskets", "Antall kurver/skuffer", (r"^antall (kurver|skuffer|kammer)",), "higher", d.CAPACITY,
             "To kurver lager to retter samtidig."),
        POWER, PROGRAMS,
        rule("window", "Vindu", (r"vindu", r"innsyn"), "yes", d.FEATURES, "Følg med uten å åpne."),
        DISHWASHER_SAFE,
    )),
    Category("blender", "Blendere", ("blender", "stavmikser", "smoothie"), rules=(
        POWER,
        rule("jug_volume", "Kannevolum (liter)", (r"^(kanne|beger|mugge)\w*volum", r"^kapasitet( \(l(iter)?\))?$", r"^volum"),
             "higher", d.CAPACITY, "Større kanne gir flere porsjoner på én gang."),
        rule("ice_crush", "Knuser is", r"isknus", "yes", d.FEATURES, "Til smoothies og frosne drinker."),
        PROGRAMS,
        rule("jug_material", "Kannemateriale", (r"^(kanne|beger)\w*materiale", r"^materiale"), "info", d.DURABILITY,
             "Glass er tyngre men riper mindre enn plast."),
    )),
    Category("kitchen", "Kjøkkenapparater", ("kjøkkenapparat", "kjokkenapparat", "foodprocessor", "vannkoker", "brødrister"), rules=(
        POWER,
        rule("capacity_l", "Kapasitet (liter)", (r"^kapasitet( \(l(iter)?\))?$", r"^volum", r"^kapasitet.*liter"), "higher",
             d.CAPACITY, "Større kapasitet lager mer på én gang."),
        PROGRAMS, DISHWASHER_SAFE,
    )),
    Category("personal", "Personlig pleie", ("barbermaskin", "trimmer", "hårføner", "harfoner", "føner", "tannbørste",
                                             "glattetang", "hårstyler", "krølltang"), rules=(
        rule("type", "Type", (r"^skjæresystem", r"^teknologi", r"^type"), "info", d.FEATURES, "Folie/roterende, sonisk/oscillerende osv."),
        rule("wet_dry", "Våt/tørr", (r"^våt", r"wet"), "yes", d.FEATURES, "Kan brukes i dusjen."),
        BATTERY_LIFE, POWER,
        rule("temps", "Temperaturinnstillinger", r"temperatur", "higher", d.FEATURES, "Flere valg gir skånsommere styling."),
        rule("ionic", "Ioneteknologi", (r"^ione", r"\bionisk"), "yes", d.FEATURES, "Mindre krus og statisk hår."),
        rule("pressure_sensor", "Trykksensor", r"trykksensor", "yes", d.FEATURES, "Beskytter tannkjøttet."),
        rule("modes", "Moduser", (r"^antall (moduser|programmer|innstillinger)", r"^moduser"), "higher", d.FEATURES,
             "Flere tilpasninger."),
    )),
    Category("emobility", "Elsparkesykler og elsykler", ("sparkesykkel", "elsykkel", "el-sparkesykkel", "elsparkesykkel"), rules=(
        rule("range", "Rekkevidde (km)", r"rekkevidde", "higher", d.BATTERY, "Reell rekkevidde er ofte 60–70 % av oppgitt."),
        rule("motor", "Motoreffekt (W)", (r"^motoreffekt", r"^motor"), "higher", d.PERFORMANCE, "Mer effekt tar bakker bedre."),
        rule("speed", "Toppfart", (r"toppfart", r"^maks.*hastighet"), "info", d.PERFORMANCE,
             "Lovlig maks i Norge: 20 km/t (sparkesykkel), 25 km/t (elsykkel)."),
        WEIGHT,
        rule("max_load", "Maks belastning (kg)", (r"^maks.*(last|brukervekt|belastning)",), "higher", d.CAPACITY,
             "Hvor tung fører den tåler."),
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
    ("tv", "monitor"),
    ("soundbar", "headphones"),
    ("oven", "airfryer", "kitchen"),
    ("kitchen_machine", "blender", "kitchen"),
    ("airfryer", "kitchen"),
    ("washer", "dryer"),
)
