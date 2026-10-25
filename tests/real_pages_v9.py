"""Real Elkjøp label sets for the product types added in v9 (fetched Oct 25, 2026).

Labels and values are copied from elkjop.no (packaging sizes, EAN and
supplier numbers left out). "expect" is the category id the app should pick.
Prices are rounded examples – only the specs matter here.
"""

PIXEL9 = {
    "expect": "mobile",
    "name": "Google Pixel 9 5G smarttelefon 12/128 GB (obsidian)",
    "url": "https://www.elkjop.no/product/mobil-nettbrett-og-smartklokker/mobiltelefon/google-pixel-9-5g-smarttelefon-12128-gb-obsidian/797329",
    "price": 7990, "rating": None, "reviews": None,
    "specs": {
        "5G": "Ja", "Antall kameraer": "3", "Display": "OLED", "Oppdateringsfrekvens": "120", "Størrelse (tommer)": "6.3",
        "IP-klassifisering": "IP68", "Internminne/RAM (GB)": "12", "Intern lagring (GB)": "128", "Type prosessor": "Tensor G4",
        "Produkttype": "Smarttelefon", "eSIM": "Ja", "NFC (Near Field Communication)": "Ja", "WiFi-standard": "Wi-Fi 7 (802.11be)",
        "Opptaksoppløsning": "4K (2160p)", "Bakkamera 1 - Bildeoppløsning (megapiksler)": "50", "Bakkamera 1 - Største blender": "1.68",
        "Bakkamera 1 - Optisk bildestabilisator": "Ja", "Trådløs lading": "Ja", "Energiklasse": "A",
        "Batteriets holdbarhet per syklus i timer og minutter per full batterilading": "49",
        "Batteriets holdbarhet i sykluser": "1000", "Batterikapasitet (mAh)": "4700", "Lader": "Nei",
        "Garanterte OS-versjonoppdateringer til minst": "7 years", "Vekt (g)": "198",
    },
    "description": "Google Tensor G4-chipsettet gir deg sømløs og kraftig ytelse.",
}

# Same phone without the processor label – Pixel pages are not always complete.
PIXEL9_NO_CHIP = dict(PIXEL9, specs={k: v for k, v in PIXEL9["specs"].items() if k != "Type prosessor"}, description="")

SONICARE_3100 = {
    "expect": "toothbrush",
    "name": "Philips Sonicare 3100 elektrisk tannbørste HX3671/14",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/munn-og-tannpleie/elektrisk-tannborste/philips-sonicare-3100-elektrisk-tannborste-hx367114/335666",
    "price": 499, "rating": None, "reviews": None,
    "specs": {
        "Oppladbar": "Ja", "Pussebevegelse pr. min.": "31000", "Trykkontrollsystem": "Ja", "Produkttype": "Elektrisk tannbørste",
        "Produktserie": "Sonicare 3100", "Tidskontroll": "Ja", "Målgruppe": "Voksne", "Lader medfølger": "Ja",
        "Navn på tilgjengelig app": "Sonicare", "Vekt (g)": "294",
    },
    "description": "Trykksensor. BrushSync minner deg på å bytte børstehode. QuadPacer og SmarTimer.",
}

SONICARE_7100 = {
    "expect": "toothbrush",
    "name": "Philips Sonicare Series 7100 elektrisk tannbørste HX7423/08 (navy blue)",
    "url": "https://www.elkjop.no/product/outlet/philips-sonicare-series-7100-elektrisk-tannborste-hx742308-navy-blue/944627",
    "price": 1490, "rating": None, "reviews": None,
    "specs": {
        "Oppladbar": "Ja", "Brukstid når fulladet (minutter)": "30240", "Pussebevegelse pr. min.": "62000",
        "Trykkontrollsystem": "Ja", "Produkttype": "Elektrisk tannbørste", "Produktserie": "Series 7100", "Tidskontroll": "Ja",
        "Ladestasjon": "Ja", "Medfølgende børster": "Ja", "Lader medfølger": "Ja", "Reiseetui": "Ja", "Skjerm": "Nei",
        "Antall hastigheter": "3", "Navn på tilgjengelig app": "Sonicare App",
    },
    "description": "Visuell trykkvarsling, timer og app.",
}

ORALB_IO3 = {
    "expect": "toothbrush",
    "name": "Oral-B iO3 elektrisk tannbørste 730898 (matt sort)",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/munn-og-tannpleie/elektrisk-tannborste/oral-b-io3-elektrisk-tannborste-730898-matt-sort/638344",
    "price": 999, "rating": None, "reviews": None,
    "specs": {
        "Oppladbar": "Ja", "Brukstid når fulladet (minutter)": "56", "Trykkontrollsystem": "Ja",
        "Produkttype": "Elektrisk tannbørste", "Produktserie": "iO3", "Tidskontroll": "Ja", "Ladestasjon": "Ja",
        "Ladetid i minutter": "960", "Medfølgende børster": "Nei", "Lader medfølger": "Ja", "Reiseetui": "Nei",
        "Skjerm": "Nei", "Antall hastigheter": "3",
    },
    "description": "Tre pussemoduser: daglig, sensitiv og bleking. Smart trykksensor. 2-minutters timer.",
}

# Not fetched: an iO9 page with the same label set as the iO3 page, to test the
# model overview for what Elkjøp's table leaves out (app, charging case …).
ORALB_IO9 = {
    "expect": "toothbrush",
    "name": "Oral-B iO9 elektrisk tannbørste (black onyx)",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/munn-og-tannpleie/elektrisk-tannborste/constructed-test-page/999999",
    "price": 3990, "rating": None, "reviews": None,
    "specs": {"Oppladbar": "Ja", "Trykkontrollsystem": "Ja", "Produkttype": "Elektrisk tannbørste", "Produktserie": "iO9",
              "Tidskontroll": "Ja"},
    "description": "",
}

HOB_HOX750 = {
    "expect": "hob",
    "name": "Electrolux induksjonstopp HOX750MF",
    "url": "https://www.elkjop.no/product/hvitevarer/komfyr-stekeovn/integrerte-platetopper/electrolux-induksjonstopp-hox750mf/HOX750MF",
    "price": 6990, "rating": None, "reviews": None,
    "specs": {
        "Bredde (cm)": "68", "Antall Booster": "2", "Kjeleregistrering": "Ja", "Stekesensor": "Nei",
        "Type oppvarming av platetopp": "Induksjon", "Total effekt (watt)": "7350", "Tidskontroll": "Ja",
        "Type barnesikring": "Barnesikring på funksjoner", "Auto-av": "Ja", "Produkttype": "Platetopp", "Kontroller": "Berøring",
    },
    "description": "",
}

MICRO_LMS2173 = {
    "expect": "microwave",
    "name": "Electrolux Serie 300 mikrobølgeovn LMS2173NB (sort)",
    "url": "https://www.elkjop.no/product/outlet/electrolux-serie-300-mikrobolgeovn-lms2173nb-sort/731346",
    "price": 3990, "rating": None, "reviews": None,
    "specs": {
        "Volum (Itr)": "17", "Total effekt (watt)": "1200", "Tidskontroll": "Ja", "Grill": "Nei", "Effekt (watt)": "700",
        "Grilleffekt (watt)": "0", "Produkttype": "Mikrobølgeovn", "Plassering": "Integrert", "Varmluft": "Nei",
        "Autoprogram": "Ja", "Roterende tallerken": "Ja", "Wi-Fi": "Nei",
    },
    "description": "Mikrobølgeeffekt: 700 W. Volum: 17 liter.",
}

OVEN_EOP721 = {
    "expect": "oven",
    "name": "Electrolux integrert stekeovn EOP721NV",
    "url": "https://www.elkjop.no/product/hvitevarer/komfyr-stekeovn/stekeovn/electrolux-integrert-stekeovn-eop721nv/EOP721NV",
    "price": 9990, "rating": None, "reviews": None,
    "specs": {
        "Type barnesikring": "Barnesikring på dør og funksjoner", "Dampfunksjon": "Ja", "Mikro": "Nei", "Varmluft": "Ja",
        "Steketermometer": "Ja", "Volum (Itr)": "71", "Skjerm": "Ja", "Wi-Fi": "Nei", "Antall ovnsrom": "1",
        "Produkttype": "Ovn", "Plassering": "Integrert", "Pyrolyse (selvrensende)": "Ja", "Pizzafunksjon": "Ja",
        "Autoprogram": "Ja", "Energiklasse": "A+",
    },
    "description": "Stor kapasitet: 71 liter. Pyrolyse selvrenseprogram.",
}

HOOD_EFF60560 = {
    "expect": "hood",
    "name": "Electrolux ventilator EFF60560OW (hvit)",
    "url": "https://www.elkjop.no/product/outlet/electrolux-ventilator-eff60560ow-hvit/615494",
    "price": 4990, "rating": None, "reviews": None,
    "specs": {
        "Lydnivå, Lav (dB)": "46", "Lydnivå, Høy (dB)": "57", "Kapasitet (m3/h)": "603", "Installasjonstype": "Vegghengt",
        "Wi-Fi": "Nei", "Energiklasse": "B", "Fettfiltreringseffektivitetsklasse": "D", "Forbruk, kWh/år": "56.4",
        "Antall instillinger": "4", "Produkttype": "Ventilator", "Type ventilator": "Kombinert (utsugning/filter)",
        "Installasjonsbredde (cm)": "60", "Lystype": "LED",
    },
    "description": "",
}

LG_SIDE_BY_SIDE = {
    "expect": "american_fridge",
    "name": "LG side-by-side GSJC41EPPE (svart)",
    "url": "https://www.elkjop.no/product/outlet/lg-side-by-side-gsjc41eppe-svart/838680",
    "price": 24990, "rating": None, "reviews": None,
    "specs": {
        "Bredde (cm)": "91.3", "Energiklasse": "E", "Nettovolum kjøledel (I)": "420", "Nettovolum frysedel (I)": "221",
        "Lydnivå (dB)": "36", "NoFrost": "Ja", "Wi-Fi": "Nei", "Produkttype": "Side-by-Side", "Plassering": "Frittstående",
        "Forbruk, kWh/år": "350", "Mulighet for rask nedkjøling": "Ja", "Hurtigfrys-funksjon": "Ja",
        "Vanninntak": "Vannbeholder", "Dispenser": "Kaldt vann", "Antall dører": "3 dører",
    },
    "description": "Door-in-Door™. Smart Inverter Compressor.",
}

WASHER_DRYER_EW7 = {
    "expect": "washer_dryer",
    "name": "Electrolux Serie 700 kombinert vaskemaskin/tørketrommel EW7WB764T4 (7/4kg)",
    "url": "https://www.elkjop.no/product/hvitevarer/vask-og-tork/kombinert-vaskemaskin-og-torketrommel/electrolux-serie-700-kombinert-vaskemaskintorketrommel-ew7wb764t4-74kg/695069",
    "price": 14990, "rating": None, "reviews": None,
    "specs": {
        "Energiklasse": "D", "Kapasitet vaske- og tørkesyklus (kg)": "4", "Kapasitet vaskesyklus (kg)": "7",
        "Luftbåren akustisk lydutslipp sentrifugeringsfase (dB)": "70", "Sentrifugehastighet (o/min)": "1600",
        "Dampfunksjon": "Ja", "Wi-Fi": "Nei", "Produkttype": "Vaskemaskin med tørketrommel", "Plassering": "Integrert",
        "Vektet energiforbruk full syklus (Kwh/100 sykluser)": "217", "Vektet vannforbruk full syklus (liter/syklus": "60",
        "Vektet vannforbruk vaskesyklus (liter/syklus)": "44", "Syklusvarighet full syklus (timer:minutter)": "5:40",
        "Sentrifugeklasse": "B", "Vektsensor": "Ja", "Utsatt oppstartsmulighet": "Ja",
    },
    "description": "SteamCare, SensiCare, DualCare.",
}

PURIFIER_FLOW_A3 = {
    "expect": "air_purifier",
    "name": "Electrolux Flow A3 luftrenser FA31-201GY",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/inneklima-og-varme/luftkvalitet/luftrenser/electrolux-flow-a3-luftrenser-fa31-201gy/139224",
    "price": 1990, "rating": None, "reviews": None,
    "specs": {
        "Lydnivå, Lav (dB)": "26", "Lydnivå, Høy (dB)": "49", "Anbefalt romstørrelse (maks kvm)": "40",
        "Sensor som måler luftkvalitet": "Ja", "Skjerm": "Ja", "Strømforbruk (kWh per 60 minutter)": "0.02",
        "CADR Røyk (Clean Air Delivery Rate)": "180", "CADR Pollen (Clean Air Delivery Rate)": "195", "Produkttype": "Luftrenser",
        "Aktivt karbonfilter": "Ja", "Indikator for filterbytte": "Ja",
        "HEPA filter (High Efficiency Particulate Air Filter)": "Ja", "Tilgjengelig app": "Nei",
        "Nattmodus (dimming)": "Ja", "Antall velgbare hastigheter": "3",
    },
    "description": "",
}

DEHUMIDIFIER_APT = {
    "expect": "dehumidifier",
    "name": "Apt avfukter 12 l/døgn (hvit)",
    "url": "https://www.elkjop.no/bedrift/product/outlet/apt-avfukter-12-ldogn-hvit/1012574",
    "price": 1990, "rating": None, "reviews": None,
    "specs": {
        "Tidskontroll": "Ja", "Avfukter (liter per døgn)": "12", "Lydnivå, Høy (dB)": "45", "Vanntank (I)": "2",
        "Anbefalt romstørrelse (maks kvm)": "25", "Lavest mulige romtemperatur": "5", "Produkttype": "Avfukter",
        "Skrur seg automatisk av ved full vannbeholder": "Ja", "Antall velgbare hastigheter": "1",
        "Avløp-/utluftsslange inkl.": "Ja",
    },
    "description": "",
}

ROUTER_HUAWEI_MESH3 = {
    "expect": "router",
    "name": "Huawei WiFi Mesh 3 AX3000 router (2-pakk)",
    "url": "https://www.elkjop.no/product/outlet/huawei-wifi-mesh-3-ax3000-router-2-pakk/531745",
    "price": 1490, "rating": None, "reviews": None,
    "specs": {
        "Produkttype": "Mesh Wi-Fi-system", "WiFi-standard": "Wi-Fi 6 (802.11ax)", "Antall LAN-porter": "1-3",
        "Frekvensbåndteknologi": "Dual-band", "Integrert backhaul": "Nei", "Hastighet trådløst (Mbps)": "2301-3000 Mbps",
        "Hastighet med kabel": "10/100/1000", "MESH kompatibel": "Ja", "Støtte for flere datastrømmer": "MU-MIMO",
        "Antall noder": "2",
    },
    "description": "",
}

NESPRESSO_VERTUO_POP = {
    "expect": "capsule",
    "name": "Nespresso Vertuo Pop kapselmaskin + melkeskummer fra De'Longhi ENV90BAE",
    "url": "https://www.elkjop.no/bedrift/product/hjem-rengjoring-og-kjokkenutstyr/kaffe-og-te/kapselmaskin/nespresso-vertuo-pop-kapselmaskin-melkeskummer-fra-delonghi-env90bae/633792",
    "price": 1490, "rating": None, "reviews": None,
    "specs": {
        "Betjening": "Automatisk", "Automatisk melkefunksjon": "Nei", "Vannbeholder (I)": "0.56", "Produkttype": "Kapselmaskin",
        "Produktserie": "Nespresso Vertuo", "Skumgenerator": "Nei", "Kalkindikator": "Nei", "Rengjøringsprogram": "Ja",
        "Auto-av": "Ja", "Wi-Fi": "Ja", "Effekt (Watt)": "1260",
    },
    "description": "",
}

PS5_PRO = {
    "expect": "console",
    "name": "PlayStation 5 Pro 2TB spillkonsoll",
    "url": "https://www.elkjop.no/product/gaming/spillkonsoller-og-tilbehor/playstation/ps5-playstation-5-spillkonsoll/playstation-5-pro-2tb-spillkonsoll/994805",
    "price": 8990, "rating": None, "reviews": None,
    "specs": {"Produkttype": "Spillkonsoll", "Konsollnavn": "Playstation 5 Pro", "Harddiskkapasitet (GB)": "2000", "Wi-Fi": "Ja"},
    "description": "",
}

LOGITECH_G305 = {
    "expect": "mouse",
    "name": "Logitech G305 trådløs gamingmus (sort)",
    "url": "https://www.elkjop.no/product/outlet/logitech-g305-tradlos-gamingmus-sort/71370",
    "price": 399, "rating": None, "reviews": None,
    "specs": {
        "Vekt (g)": "99", "Produkttype": "Mus", "Tilkobling": "RF trådløs + USB-mottaker", "DPI (dots per inch)": "12000",
        "Høyre/Venstre-hånds mus": "Høyre", "Programmerbare taster": "Ja", "Type sensor": "Optisk",
        "Polling rate (Hz)": "1000", "Responstid (ms)": "1", "Antall museknapper": "6",
    },
    "description": "",
}

SAMSUNG_T7 = {
    "expect": "storage",
    "name": "Samsung T7 ekstern SSD 1 TB (blå)",
    "url": "https://www.elkjop.no/product/pc-datautstyr-og-kontor/lagring/ekstern-ssd/samsung-t7-ekstern-ssd-1-tb-bla/184144",
    "price": 1290, "rating": None, "reviews": None,
    "specs": {"Total lagringskapasitet (GB)": "1000", "Produkttype": "Ekstern SSD", "Type": "Bærbar ekstern SSD",
              "Tilkoblinger": "USB-C", "Vekt (g)": "58"},
    "description": "Overføringshastigheter på opptil 1050 MB/s.",
}

BRAUN_IPL_PRO5 = {
    "expect": "ipl",
    "name": "Braun Silk-expert Pro 5 lysbasert hårfjerning PL5347",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/barbering-og-harfjerning/ipl-harfjerning/braun-silk-expert-pro-5-lysbasert-harfjerning-pl5347/523423",
    "price": 4990, "rating": None, "reviews": None,
    "specs": {
        "Oppladbar": "Nei", "Kan brukes på sensitive områder (armhuler/bikinilinje)": "Ja", "Kan brukes i ansiktet": "Ja",
        "Hudsensor (gjenkjenner hudtype)": "Ja", "Produkttype": "Hårfjerner (lys)", "Trådløs": "Nei", "Antall hastigheter": "3",
        "Antall medfølgende tilbehør": "3", "Reiseetui": "Ja",
    },
    "description": "",
}

PHILIPS_SHAVER_7000 = {
    "expect": "shaver",
    "name": "Philips Series 7000 barbermaskin S7887/55",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/barbering-og-harfjerning/barbermaskin/philips-series-7000-barbermaskin-s788755/610242",
    "price": 2490, "rating": None, "reviews": None,
    "specs": {
        "Oppladbar": "Ja", "Rense- og ladestasjon": "Ja", "Brukstid når fulladet (minutter)": "60", "Produkttype": "Barbermaskin",
        "Vanntett": "Ja", "Ekstra følsom og mild": "Ja", "Antall medfølgende tilbehør": "3", "Ladetid i minutter": "60",
        "Fleksibelt skjærehode": "Ja", "Trimmer": "Ja", "Reiseetui": "Ja", "Skjerm": "Ja", "Trådløs": "Ja",
    },
    "description": "",
}

DYSON_SUPERSONIC = {
    "expect": "hair",
    "name": "Dyson Supersonic HD07 hårføner (nikkel/kobber)",
    "url": "https://www.elkjop.no/product/personlig-pleie-skjonnhet-og-velvare/har-og-styling/harfoner/dyson-supersonic-hd07-harfoner-nikkelkobber/492490",
    "price": 4990, "rating": None, "reviews": None,
    "specs": {
        "Vekt (kg)": "0.795", "Kaldluft": "Ja", "Turbofunksjon": "Nei", "Effekt (Watt)": "1600", "Spreder inkludert": "Ja",
        "Produkttype": "Hårføner", "Vifteinnstillinger": "3", "Temperaturinnstillinger": "4", "Ionisk teknologi": "Ja",
        "Auto-av": "Nei",
    },
    "description": "",
}

SAMSUNG_JET = {
    "expect": "vacuum",
    "name": "Samsung Bespoke Jet Complete skaftstøvsuger VS20A95843W",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/stovsugere-og-rengjoring/tradlos-stovsuger/samsung-bespoke-jet-complete-skaftstovsuger-vs20a95843w/454761",
    "price": 5990, "rating": None, "reviews": None,
    "specs": {
        "Vekt (kg)": "2.7", "Lydnivå (dB)": "86", "Ladetid i timer": "3.5", "Brukertid, minimumskapasitet (min)": "60",
        "Brukertid, makskapasitet (min)": "3", "Produkttype": "2-i-1 trådløs støvsuger", "Selvstående funksjon": "Nei",
        "Maks effekt (watt)": "210", "Batterikapasitet (mAh)": "2500", "Filtreringssystem": "Poseløs", "Vaskbart filter": "Ja",
        "Optimalisert for dyrehår": "Ja", "Regjøringsbredde (mm)": "250",
    },
    "description": "",
}

ADAX_NEO = {
    "expect": "heater",
    "name": "Adax Neo Basic panelovn NP10KDT (hvit)",
    "url": "https://www.elkjop.no/product/hjem-rengjoring-og-kjokkenutstyr/inneklima-og-varme/oppvarming/varmeovner-og-panelovner/panelovn/adax-neo-basic-panelovn-np10kdt-hvit/NP10KDTWHITE",
    "price": 2290, "rating": None, "reviews": None,
    "specs": {
        "Anbefalt romstørrelse (maks kvm)": "16", "Effekt (watt)": "1000", "Produkttype": "Panelovn", "Termostat": "Digital",
        "Kan brukes i våtrom": "Nei", "Fjernkontroll": "Nei", "Oljefylt": "Nei", "Integrert spareplugg": "Ja",
        "IP-klassifisering": "IP20", "Barnesikring": "Ja", "Fallsikkerhet": "Nei", "Wi-Fi": "Nei",
    },
    "description": "",
}

ALL_V9 = [PIXEL9, SONICARE_3100, SONICARE_7100, ORALB_IO3, ORALB_IO9, HOB_HOX750, MICRO_LMS2173, OVEN_EOP721, HOOD_EFF60560,
          LG_SIDE_BY_SIDE, WASHER_DRYER_EW7, PURIFIER_FLOW_A3, DEHUMIDIFIER_APT, ROUTER_HUAWEI_MESH3, NESPRESSO_VERTUO_POP,
          PS5_PRO, LOGITECH_G305, SAMSUNG_T7, BRAUN_IPL_PRO5, PHILIPS_SHAVER_7000, DYSON_SUPERSONIC, SAMSUNG_JET, ADAX_NEO]
