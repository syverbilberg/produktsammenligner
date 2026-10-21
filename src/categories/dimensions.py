"""The customer priorities ("Hva er viktigst for kunden?").

Every spec rule in the guide belongs to exactly one of these. The priority
step only asks about the dimensions the detected category actually uses.
"""

PRICE = "Pris"
PERFORMANCE = "Ytelse"
CAPACITY = "Størrelse og kapasitet"
BATTERY = "Batteri"
DISPLAY = "Skjerm og bilde"
CAMERA = "Kamera"
SOUND = "Lyd"
ENERGY = "Strøm og driftskostnad"
NOISE = "Lavt støynivå"
FEATURES = "Funksjoner"
LIFESPAN = "Levetid og oppdateringer"
DURABILITY = "Holdbarhet"
CONNECTIVITY = "Tilkobling"
PORTABILITY = "Vekt og portabilitet"

# Order the dimensions are shown in.
ALL = (
    PRICE, PERFORMANCE, CAPACITY, DISPLAY, CAMERA, SOUND, BATTERY, ENERGY,
    NOISE, FEATURES, LIFESPAN, DURABILITY, CONNECTIVITY, PORTABILITY,
)

# Priority levels shown as chips, and the weight each one gives.
LEVELS = {"Ikke viktig": 0, "Litt viktig": 1, "Nøytral": 2, "Viktig": 3, "Svært viktig": 4}
DEFAULT_LEVEL = "Nøytral"
