"""Constants for Vehicle Manager integration."""

DOMAIN = "vehicle_manager"

# ─── Config keys – basic car info ───────────────────────────────────────────
CONF_CAR_NAME = "car_name"
CONF_MAKE = "make"
CONF_MODEL = "model"
CONF_YEAR = "year"
CONF_PLATE = "plate"
CONF_COUNTRY = "country"
CONF_LANGUAGE = "language"

# ─── Config keys – document expiry dates ────────────────────────────────────
CONF_INSURANCE_EXPIRY = "insurance_expiry"
CONF_CASCO_EXPIRY = "casco_expiry"
CONF_INSPECTION_EXPIRY = "inspection_expiry"
CONF_ROAD_TAX_EXPIRY = "road_tax_expiry"
CONF_VIGNETTE_EXPIRY = "vignette_expiry"
CONF_FIRE_EXTINGUISHER_EXPIRY = "fire_extinguisher_expiry"
CONF_FIRST_AID_KIT_EXPIRY = "first_aid_kit_expiry"

# ─── Config keys – service history ──────────────────────────────────────────
CONF_ODOMETER = "odometer"
CONF_OIL_CHANGE_DATE = "oil_change_date"
CONF_OIL_CHANGE_KM = "oil_change_km"
CONF_OIL_CHANGE_INTERVAL = "oil_change_interval_km"
CONF_AIR_FILTER_DATE = "air_filter_date"
CONF_AIR_FILTER_KM = "air_filter_km"
CONF_AIR_FILTER_INTERVAL = "air_filter_interval_km"
CONF_CABIN_FILTER_DATE = "cabin_filter_date"
CONF_CABIN_FILTER_KM = "cabin_filter_km"
CONF_CABIN_FILTER_INTERVAL = "cabin_filter_interval_km"
CONF_TIMING_BELT_DATE = "timing_belt_date"
CONF_TIMING_BELT_KM = "timing_belt_km"
CONF_TIMING_BELT_INTERVAL = "timing_belt_interval_km"
CONF_BRAKES_DATE = "brakes_date"
CONF_BRAKES_KM = "brakes_km"
CONF_BRAKES_INTERVAL = "brakes_interval_km"
CONF_BATTERY_DATE = "battery_date"
CONF_TIRES_DATE = "tires_date"
CONF_AC_SERVICE_DATE = "ac_service_date"
CONF_GENERAL_SERVICE_DATE = "general_service_date"
CONF_GENERAL_SERVICE_KM = "general_service_km"
CONF_GENERAL_SERVICE_INTERVAL = "general_service_interval_km"
CONF_NOTES = "notes"

# ─── Sensor type keys ────────────────────────────────────────────────────────
SENSOR_INSURANCE = "insurance"
SENSOR_CASCO = "casco"
SENSOR_INSPECTION = "inspection"
SENSOR_ROAD_TAX = "road_tax"
SENSOR_VIGNETTE = "vignette"
SENSOR_FIRE_EXTINGUISHER = "fire_extinguisher"
SENSOR_FIRST_AID_KIT = "first_aid_kit"
SENSOR_ODOMETER = "odometer"
SENSOR_OIL_CHANGE = "oil_change"
SENSOR_AIR_FILTER = "air_filter"
SENSOR_CABIN_FILTER = "cabin_filter"
SENSOR_TIMING_BELT = "timing_belt"
SENSOR_BRAKES = "brakes"
SENSOR_BATTERY = "battery"
SENSOR_TIRES = "tires"
SENSOR_AC_SERVICE = "ac_service"
SENSOR_GENERAL_SERVICE = "general_service"

# ─── Countries ───────────────────────────────────────────────────────────────
COUNTRIES = {
    "RO": "România 🇷🇴",
    "DE": "Deutschland 🇩🇪",
    "FR": "France 🇫🇷",
    "IT": "Italia 🇮🇹",
    "AT": "Österreich 🇦🇹",
    "ES": "España 🇪🇸",
    "PL": "Polska 🇵🇱",
    "NL": "Nederland 🇳🇱",
    "HU": "Magyarország 🇭🇺",
    "CZ": "Česká republika 🇨🇿",
}

COUNTRY_FLAGS = {
    "RO": "🇷🇴", "DE": "🇩🇪", "FR": "🇫🇷", "IT": "🇮🇹", "AT": "🇦🇹",
    "ES": "🇪🇸", "PL": "🇵🇱", "NL": "🇳🇱", "HU": "🇭🇺", "CZ": "🇨🇿",
}

# ─── Languages ───────────────────────────────────────────────────────────────
LANGUAGES = {
    "en": "English",
    "ro": "Română",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "es": "Español",
    "pl": "Polski",
    "hu": "Magyar",
}

# ─── Country-specific field names ────────────────────────────────────────────
COUNTRY_INSPECTION_NAME = {
    "RO": "ITP",
    "DE": "TÜV / HU",
    "FR": "Contrôle Technique (CT)",
    "IT": "Revisione",
    "AT": "§57a Pickerl",
    "ES": "ITV",
    "PL": "Przegląd techniczny",
    "NL": "APK",
    "HU": "Műszaki vizsga",
    "CZ": "STK",
}

COUNTRY_ROAD_TAX_NAME = {
    "RO": "Impozit auto",
    "DE": "KFZ-Steuer",
    "FR": "Taxe à l'essieu / TVS",
    "IT": "Bollo auto",
    "AT": "KFZ-Steuer",
    "ES": "IVTM",
    "PL": "Podatek drogowy",
    "NL": "Wegenbelasting (MRB)",
    "HU": "Gépjárműadó",
    "CZ": "Silniční daň",
}

COUNTRY_INSURANCE_NAME = {
    "RO": "RCA",
    "DE": "KFZ-Haftpflicht",
    "FR": "Assurance RC",
    "IT": "RCA",
    "AT": "KFZ-Haftpflicht",
    "ES": "Seguro obligatorio",
    "PL": "OC",
    "NL": "WA-verzekering",
    "HU": "Kötelező biztosítás (KGFB)",
    "CZ": "Povinné ručení",
}

# Countries that have a vignette/rovinieta system
COUNTRY_VIGNETTE_NAME = {
    "RO": "Rovinieta",
    "AT": "Autobahnvignette",
    "PL": "e-TOLL / myViaTOLL",
    "HU": "Autópálya-matrica",
    "CZ": "Dálniční známka",
}

# ─── Status thresholds ───────────────────────────────────────────────────────
DAYS_CRITICAL = 7
DAYS_WARNING = 30
KM_CRITICAL = 500
KM_WARNING = 3000

# ─── Default service intervals (km) ─────────────────────────────────────────
DEFAULT_OIL_INTERVAL = 10000
DEFAULT_AIR_FILTER_INTERVAL = 30000
DEFAULT_CABIN_FILTER_INTERVAL = 15000
DEFAULT_TIMING_BELT_INTERVAL = 120000
DEFAULT_BRAKES_INTERVAL = 50000
DEFAULT_GENERAL_SERVICE_INTERVAL = 15000
