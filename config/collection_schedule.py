"""
Configuration for scheduled fare collection.
"""

# ----------------------------------------------------------
# Daily collection time slots (24-hour format)
# ----------------------------------------------------------

TIME_SLOTS = [
    "00:00",
    "09:00",
    "12:00",
    "15:00",
    "18:00",
    "21:00",
]

# ----------------------------------------------------------
# Maximum number of routes to collect in one execution.
# ----------------------------------------------------------

MAX_ROUTES_PER_SLOT = 100

# ----------------------------------------------------------
# CSV containing today's routed trips.
# ----------------------------------------------------------

ROUTES_CSV = (
    "data/processed/routes/routes.csv"
)

# ----------------------------------------------------------
# Uber fare dataset.
# ----------------------------------------------------------

UBER_FARES_CSV = (
    "data/raw/fares/uber_fares.csv"
)

# ----------------------------------------------------------
# Timezone used throughout the project.
# ----------------------------------------------------------

TIMEZONE = "Asia/Kolkata"

# ----------------------------------------------------------
# Browser delay (milliseconds)
#
# Used between consecutive route collections to avoid
# looking like a bot.
# ----------------------------------------------------------

COLLECTION_DELAY_MS = 2000