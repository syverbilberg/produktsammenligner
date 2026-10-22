"""Spec labels copied from real Elkjøp product pages (October 2026).

Labels and values are as shown on elkjop.no. The descriptions are short
paraphrases of the page text (not verbatim), keeping the facts the app
reads from them. When Elkjøp changes a label, update it here and the tests
show exactly which rules stop matching.
"""

S26 = {
    "name": "Samsung Galaxy S26 5G smarttelefon 12/256GB (sort)",
    "url": "https://www.elkjop.no/product/mobil-nettbrett-og-smartklokker/mobiltelefon/"
           "samsung-galaxy-s26-5g-smarttelefon-12256gb-sort/1039743",
    "price": 13490, "rating": 4.8, "reviews": 3165,
    "specs": {
        "Ladeenhet inkludert": "Nei",
        "Påkrevd ladeeffekt (min. i W)": "10",
        "Påkrevd ladeeffekt (max. i W)": "25",
        "USB-strømforsyning (USB PD)": "Ja",
        "Trådløs lading": "Ja",
        "Avtagbart batteri": "Nei",
        "Batterikapasitet (mAh)": "4300",
        "Batteritype": "Litium-ion",
        "Batteriets holdbarhet per syklus i timer og minutter per full batterilading": "51",
        "Batteriets holdbarhet i sykluser": "2700",
        "Energiklasse": "A",
        "Intern lagring (GB)": "256",
        "Antall kameraer": "3",
        "Nattmodus": "Ja",
        "Videoopptak": "Ja",
        "Opptaksoppløsning": "8K UHD (4320p)",
        "Display": "OLED",
        "Oppdateringsfrekvens": "120",
        "Størrelse (tommer)": "6.3",
        "Skjermoppløsning (i piksler)": "2340 x 1080",
        "Touch-skjerm": "Ja",
        "IP-klassifisering": "IP68",
        "Produkttype": "Mobiltelefon",
    },
    "description": "Galaxy S26 drives av en Exynos 2600-prosessor. Prosessoren er ledsaget av 12 GB RAM, "
                   "og det er 256 GB lagringsplass. 6,3-tommers 120 Hz AMOLED-skjerm.",
}

S25 = {
    "name": "Samsung Galaxy S25 5G smarttelefon 12/256GB (Blueblack)",
    "url": "https://www.elkjop.no/product/mobil-nettbrett-og-smartklokker/mobiltelefon/"
           "samsung-galaxy-s25-5g-smarttelefon-12256gb-blueblack/938012",
    "price": 12290, "rating": 4.7, "reviews": 2100,
    "specs": {**S26["specs"], "Batterikapasitet (mAh)": "4000"},
    "description": "Snapdragon 8 Elite for Galaxy og 12 GB RAM.",
}

HP_LAPTOP = {
    "name": 'HP Laptop 14-ep1830no Core5-120U/16/512 14" bærbar PC',
    "url": "https://www.elkjop.no/product/pc-datautstyr-og-kontor/pc/barbar-pc/"
           "hp-laptop-14-ep1830no-core5-120u16512-14-barbar-pc/1019075",
    "price": 6990, "rating": None, "reviews": None,
    "specs": {
        "Internminne/RAM (GB)": "16", "Total lagringskapasitet (GB)": "512", "WiFi-standard": "Wi-Fi 6 (802.11ax)",
        "Størrelse (tommer)": "14", "Nummer": "120U", "Operativsystem versjon": "Windows 11 Home",
        "Produsentmerke (GPU)": "Intel", "Vekt (kg)": "1.4",
        "Produsent CPU": "Intel", "Prosessortype": "Intel Core 5", "Antall prosessorkjerner": "10",
        "Maksimal hastighet (GHz)": "5", "RAM-type": "DDR4", "Maksimalt støttet minne (GB)": "16",
        "Minnehastighet i MT/s": "3200", "Antall RAM-spor": "1", "Type lagring": "M.2 PCIe NVMe SSD",
        "Lagringskapasitet SSD (GB)": "512", "Display": "SVA", "Touch-skjerm": "Nei",
        "Oppløsningsstandard": "Full HD (1080p)", "Maks oppløsning": "1920x1080", "Oppdateringsfrekvens": "60",
        "Displayteknologi": "SVA", "Nit": "250", "Arkitektur grafikkort": "Delt", "Hovedmerke (GPU)": "Intel",
        "Batteri": "4h 35m", "Leverandørens oppgitte batterilevetid opptil (timer)": "7.5",
        "Ladeenhet inkludert": "Ja", "Påkrevd ladeeffekt (min. i W)": "45", "Påkrevd ladeeffekt (max. i W)": "100",
        "Maks belastning (Watt per time/Wh)": "25.9", "Wi-Fi": "Ja", "Bluetooth": "Bluetooth 5.2",
        "USB-C Power Delivery": "Ja", "NFC (Near Field Communication)": "Nei", "HDMI-tilkobling": "Ja",
        "Thunderbolt": "Nei", "Minnekortspor": "Nei", "Tilkobling": "Wi-Fi", "Type operativsystem": "Windows",
        "Bakgrunnsbelyst tastatur": "Nei", "Biometrisk innlogging (fingeravtrykksleser)": "Nei",
        "Hurtiglading": "Ja", "Produkttype": "Bærbar PC", "Lanseringsår": "2025",
    },
    "description": "",
}

BOSCH_MUMS6 = {
    "name": "Bosch Series 6 kjøkkenmaskin MUMS6ZS18 (sort)",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/kjokkenapparater/"
           "kjokkenmaskiner-og-matlaging/kjokkenmaskin/bosch-series-6-kjokkenmaskin-mums6zs18-sort/915196",
    "price": 4999, "rating": 4.9, "reviews": 27,
    "specs": {
        "Høyde (cm)": "33", "Bredde (cm)": "32", "Dybde (cm)": "38", "Vekt (kg)": "9.1",
        "Produkttype": "Kjøkkenmaskin", "Materiale": "Rustfritt stål", "Hastighetinnstillinger": "7",
        "Turbo-/pulsknapp": "Nei", "Isknusingsfunksjon": "Ja", "Justerbar hastighet": "Ja",
        "Motorkraft (Watt)": "1600", "Kapasitet (kg)": "3.5", "Bollevolum (Itr)": "5.5",
        "Bolle inkludert": "Ja", "Hjulpisker inkludert": "Ja", "Eltekrok inkludert": "Ja",
        "Modellnavn": "Bosch MUMS6ZS18", "Produktserie": "Series 6", "Antall boller": "2", "Nutriblender": "Nei",
    },
    "description": "Sensorteknologi og sensordrevne automatiske programmer gir presise resultater. "
                   "Integrert vekt med 1 g presisjon, timer og berøringsskjerm. 1600 W-motor. "
                   "Pulsfunksjon og 7 hastighetstrinn. Tilbehøret kan maskinvaskes.",
}

KENWOOD_KVL85 = {
    "name": "Kenwood Titanium Chef Baker XL kjøkkenmaskin KVL85.004SI",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/kjokkenapparater/"
           "kjokkenmaskiner-og-matlaging/kjokkenmaskin/kenwood-titanium-chef-baker-xl-kjokkenmaskin-kvl85004si/351830",
    "price": 5299, "rating": 4.6, "reviews": 319,
    "specs": {
        "Høyde (cm)": "49.5", "Bredde (cm)": "53", "Dybde (cm)": "35", "Vekt (kg)": "14.91",
        "Produkttype": "Kjøkkenmaskin", "Motorkraft (Watt)": "1200", "Bollevolum (Itr)": "7",
        "Materiale": "Rustfritt stål", "Justerbar hastighet": "Ja",
        "Bolle inkludert": "Ja", "Hjulpisker inkludert": "Ja", "Eltekrok inkludert": "Ja",
        "Modellnavn": "Kenwood KVL85.004SI", "Produktserie": "Titanium Chef Baker",
        "Antall boller": "2", "Antall uttak for tilbehør": "2",
    },
    "description": "1200 W-motor for jevn ytelse. EasyWeight-vekten veier direkte i bollen. "
                   "DuoBowl-boller på 7 og 5 liter. Rustfrie verktøy som tåler oppvaskmaskin.",
}

ASKO_DISHWASHER = {
    "name": "Asko oppvaskmaskin DBI8557MIMXXLS",
    "url": "https://www.elkjop.no/product/hvitevarer/oppvaskmaskin/asko-oppvaskmaskin-dbi8557mimxxls/457340",
    "price": 13757, "rating": None, "reviews": None,
    "specs": {
        "Bredde (cm)": "59.5", "Dybde (cm)": "55.4", "Høyde (cm)": "85.9", "Vekt (kg)": "46.5",
        "Type oppvaskmaskin": "Underbygd", "Bestikkplassering": "Bestikkurv", "Innvendig belysning": "Ja",
        "Energiklasse": "B", "Lydnivå (dB)": "41", "Kapasitet (antall kuverter)": "15",
        "Sikring på vanninntak (aquastop/PEX)": "Ja", "Antall programmer": "9", "Automatisk åpning": "Ja",
        "Wi-Fi": "Ja", "Produkttype": "Oppvaskmaskin", "Høydejustering på øvre kurv": "Ja",
        "Eco-program vannforbruk (EPWC) i liter pr. syklus": "9.6", "Lydklasse": "B",
        "Utsatt oppstartsmulighet": "Ja", "Halv last-program": "Nei", "Maksimal vasketemperatur": "70",
    },
    "description": "",
}

ROBOROCK_SAROS20S = {
    "name": "Roborock Saros 20 Sonic rengjøringsrobot S20S52-00 (sort)",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/stovsugere-og-rengjoring/robotstovsuger/"
           "roborock-saros-20-sonic-rengjoringsrobot-s20s52-00-sort/1079413",
    "price": 15990, "rating": 5.0, "reviews": 1,
    "specs": {
        "Høyde (cm)": "47", "Bredde (cm)": "41", "Dybde (cm)": "44", "Vekt (kg)": "16.68",
        "Navigasjonssystem": "Kamera, Laser", "Kart": "Ja", "Automatisk tømmefunksjon": "Ja, med tilbehør",
        "Lydnivå (dB)": "64", "Maks vakuumtrykk (Pa)": "36000", "Ladetid i timer": "2.5",
        "Brukstid når fulladet (minutter)": "190", "Kapasitet støvbeholder (l)": "2.5",
        "Produkttype": "Robotstøvsuger", "Produktserie": "Saros 20 Sonic",
        "Type moppesystem": "Vibrerende", "Automatisk selvlading": "Ja", "Sett opp rengjøringsplan": "Ja",
        "Indikatorlys når ferdig": "Ja", "Poseindikator": "Nei", "Filterindikator": "Ja",
        "Indikator ved full støvbeholder": "Ja", "Punktrengjøring": "Ja", "Forsterket tepperengjøring": "Ja",
        "Børsteløs støvsuging": "Nei", "Støtte for usynlig/virtuell avsperring": "Ja", "Kantrengjøring": "Ja",
        "Anti-floke funksjon": "Ja", "Fjernkontroll": "Nei", "Kapasitet vannbeholder (ml)": "4000",
        "Elektronisk justerbar effekt": "Ja", "Batteritype": "Litium-ion", "Batterikapasitet (mAh)": "6400",
    },
    "description": "VibraRise 5.0 gir mer effektiv mopping med justerbar vannmengde og vibrasjonsnivå i "
                   "Roborock-appen. Moppen løftes automatisk på tepper.",
}

DREAME_X60_PRO = {
    "name": "Dreame X60 Pro Ultra Komplett rengjøringsrobot DI2851 (Svart)",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/stovsugere-og-rengjoring/robotstovsuger/"
           "dreame-x60-pro-ultra-komplett-rengjoringsrobot-di2851-svart/1113442",
    "price": 13990, "rating": None, "reviews": None,
    "specs": {
        "Høyde (cm)": "49.9", "Bredde (cm)": "45.6", "Dybde (cm)": "39", "Vekt (kg)": "15.4",
        "Navigasjonssystem": "Laser", "Kart": "Ja", "Automatisk tømmefunksjon": "Ja",
        "Maks vakuumtrykk (Pa)": "42000", "Kapasitet støvbeholder (l)": "0.31", "Produkttype": "Robotstøvsuger",
        "Vaskbart filter": "Ja", "Automatisk selvlading": "Ja", "Sett opp rengjøringsplan": "Ja",
        "Indikatorlys når ferdig": "Ja", "Poseindikator": "Ja", "Filterindikator": "Ja",
        "Indikator ved full støvbeholder": "Ja", "Punktrengjøring": "Ja", "Forsterket tepperengjøring": "Ja",
        "Børsteløs støvsuging": "Ja", "Støtte for usynlig/virtuell avsperring": "Ja", "Kantrengjøring": "Ja",
        "Anti-floke funksjon": "Ja", "Fjernkontroll": "Ja", "Kapasitet vannbeholder (ml)": "4200",
        "Batteritype": "Litium-ion", "Batterikapasitet (mAh)": "5000",
    },
    "description": "Avansert mopping for dypere rengjøring: Thermal Deep Mop-systemet kombinerer oppvarmede mopper, "
                   "høyt nedadgående trykk og rask rotasjon. Passerer automatisk hindringer og nivåforskjeller.",
}

# ------------------------------------------------------------ added Oct 22
PCS_PRIME400 = {
    "name": "PCSpecialist Prime 400 i7-14F/16/1000/5070 stasjonær gaming-PC",
    "url": "https://www.elkjop.no/product/pc-datautstyr-og-kontor/pc/stasjonar-pc/"
           "pcspecialist-prime-400-i7-14f1610005070-stasjonar-gaming-pc/901749",
    "price": 17990, "rating": None, "reviews": None,
    "specs": {
        "Produsent CPU": "Intel", "Prosessortype": "Intel Core i7", "Nummer": "14700F", "Chipset": "b760",
        "Arkitektur grafikkort": "Dedikert", "Hovedmerke (GPU)": "NVIDIA", "Grafikkløsning (Modell)": "GeForce RTX 5070",
        "Grafikkort (serie)": "GeForce RTX 50 Series", "Dedikert videominne": "12", "RAM-type": "DDR5",
        "Internminne/RAM (GB)": "16", "Maksimalt støttet minne (GB)": "192", "Lagringskapasitet SSD (GB)": "1000",
        "Total lagringskapasitet (GB)": "1000", "Strømforsyning (watt)": "750", "Type avkjøling": "Vannkjøling",
        "Kjølekapasitet (W)": "250", "Type operativsystem": "Windows", "Operativsystem versjon": "Windows 11 Home",
        "Wi-Fi": "Ja", "WiFi-standard": "Wi-Fi 6E", "Bluetooth": "Ja", "Produkttype": "Stasjonær gaming-PC",
        "Lanseringsår": "2025", "Optimalisert for gaming": "Ja", "Vekt (kg)": "12.584",
    },
    "description": "",
}

LEGION_TOWER5 = {
    "name": "Lenovo Legion Tower 5 Gen 10 R7-7700X/16/1TB/5070 stasjonær gaming-PC",
    "url": "https://www.elkjop.no/product/pc-datautstyr-og-kontor/pc/stasjonar-pc/"
           "lenovo-legion-tower-5-gen-10-r7-7700x161tb5070-stasjonar-gaming-pc/913588",
    "price": 18990, "rating": None, "reviews": None,
    "specs": {
        "Internminne/RAM (GB)": "16", "Total lagringskapasitet (GB)": "1000", "Grafikkløsning (Modell)": "GeForce RTX 5070",
        "WiFi-standard": "Wi-Fi 6E (802.11ax)", "Nummer": "7700X", "Operativsystem versjon": "Windows 11 Home",
        "RAM-type": "DDR5", "Maksimalt støttet minne (GB)": "32", "Arkitektur grafikkort": "Dedikert",
        "Hovedmerke (GPU)": "NVIDIA", "Dedikert videominne": "12", "Produkttype": "Stasjonær gaming-PC",
        "Lanseringsår": "2025", "Wi-Fi": "Ja", "Bluetooth": "Ja", "Produsent CPU": "AMD",
        "Prosessortype": "AMD Ryzen 7", "Antall prosessorkjerner": "8", "Maksimal hastighet (GHz)": "5.4",
        "Type avkjøling": "CPU luftkjøling (vifte)", "Vekt (kg)": "15",
    },
    "description": "",
}

LG_B5_TV = {
    "name": 'LG 65" B5 4K OLED TV (2025)',
    "url": "https://www.elkjop.no/product/tv-lyd-og-smarte-hjem/tv-og-tilbehor/tv/lg-65-b5-4k-oled-tv-2025/912293",
    "price": 16990, "rating": None, "reviews": None,
    "specs": {
        "Smart-TV-plattform": "webOS", "Størrelse (tommer)": "65", "Lanseringsår": "2025", "Produkttype": "TV",
        "Panelteknologi": "OLED", "Oppløsning": "4K (2160p)", "Bildepanelfrekvens (Hz)": "120",
        "High Dynamic Range (HDR) standard": "Dolby Vision", "Fargegjengivelse (score)": "9", "Kontrast score": "10",
        "Panelscore": "8", "Lysstyrke score": "4.2", "Antall HDMI-innganger": "3", "HDMI-standard": "HDMI 2.1",
        "Variable Refresh Rate (VRR)": "Ja", "Auto Low Latency Mode (ALLM)": "Ja",
        "eArc (enhanced Audio Return Channel)": "Ja", "Lydeffekt (watt)": "20", "Energiklasse": "F",
    },
    "description": "Dolby Vision & Dolby Atmos.",
}

ASKO_W3096 = {
    "name": "ASKO Vaskemaskin W3096RW (9kg)",
    "url": "https://www.elkjop.no/product/hvitevarer/vask-og-tork/vaskemaskin/asko-vaskemaskin-w3096rw-9kg/1020574",
    "price": 12990, "rating": None, "reviews": None,
    "specs": {
        "Sentrifuge": "1600 o/min", "Type vaskemaskin": "Frontmatet", "Energiklasse": "A",
        "Kapasitet vaskesyklus (kg)": "9", "Luftbåren akustisk lydutslipp sentrifugeringsfase (dB)": "70",
        "Luftbåren akustisk lydutslipp-klasse sentrifugeringsfase": "A", "Trommelvolum (I)": "60",
        "Sentrifugehastighet (o/min)": "1600", "Wi-Fi": "Ja", "Produkttype": "Vaskemaskin",
        "Vektet vannforbruk vaskesyklus (liter/syklus)": "35",
    },
    "description": "Auto Dose med to avtakbare tanker. Damprensprogram.",
}

SONY_XM6 = {
    "name": "Sony WH-1000XM6 trådløse around-ear hodetelefoner (sand pink)",
    "url": "https://www.elkjop.no/product/tv-lyd-og-smarte-hjem/hodetelefoner-og-tilbehor/hodetelefoner/"
           "sony-wh-1000xm6-tradlose-around-ear-hodetelefoner-sand-pink/1039377",
    "price": 4990, "rating": None, "reviews": None,
    "specs": {
        "Tilkobling": "Bluetooth", "Audio-støtte": "Hi-Res Audio", "Type hodetelefoner": "Around-ear",
        "Vannresistent": "Nei", "Mikrofon": "Ja", "Vekt (g)": "254", "Taletid (timer)": "28",
        "Musikkavspillingstid med ANC på (timer)": "30", "Musikkavspillingstid (timer)": "40",
        "Batteritid - stand by (timer)": "Up to 7 days", "Ladetid (timer)": "3.5", "Bluetooth-standard": "Bluetooth 5.3",
        "Bluetooth lydkodek": "SBC", "Produkttype": "Hodetelefoner", "Aktiv støykansellering": "Ja",
    },
    "description": "Multipoint Connection lar deg koble til to enheter samtidig.",
}

LG_DRYER = {
    "name": "LG tørketrommel RV9DN902B",
    "url": "https://www.elkjop.no/product/hvitevarer/vask-og-tork/torketrommel-og-torkeskap/torketrommel/lg-torketrommel-rv9dn902b/155021",
    "price": 9990, "rating": None, "reviews": None,
    "specs": {
        "Varmepumpeteknologi": "Ja", "Dampfunksjon": "Nei", "Wi-Fi": "Ja", "Energiklasse": "A+++",
        "Lydnivå tørk (dB)": "62", "Tørkekapasitet (kg)": "9", "Produkttype": "Tørketrommel",
        "Type tørketrommel": "Kondens", "Tørkesystem": "Sensor", "Kan kobles til avløp": "Ja", "Forbruk, kWh/år": "194",
    },
    "description": "",
}

MELITTA_SOLO = {
    "name": "Melitta Caffeo Solo & Perfect Milk kaffemaskin 20812",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/kaffe-og-te/kaffemaskin-og-espressomaskin/"
           "melitta-caffeo-solo-perfect-milk-kaffemaskin-20812/MEL20812",
    "price": 5490, "rating": None, "reviews": None,
    "specs": {
        "Skumgenerator": "Ja", "Renseindikator": "Ja", "Automatisk melkefunksjon": "Ja", "Vannbeholder (I)": "1.2",
        "Pumpetrykk (Bar)": "15", "Produkttype": "Kaffemaskin", "Betjening": "Automatisk",
        "Integrert kaffekvern": "Ja", "Antall kvernegrader": "5", "Kalkindikator": "Ja", "Rengjøringsprogram": "Ja",
        "Effekt (Watt)": "1400", "Wi-Fi": "Nei",
    },
    "description": "15 bar trykk, dobbelkopp-funksjon og Auto-Cappuccinatore.",
}
