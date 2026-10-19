"""
Configuration for generating realistic Bangalore cab trips.

The weights represent the probability of generating a trip from a
pickup category to a drop category.

The weights for each pickup category should sum to 1.0.
"""

# Total number of trips to generate
TOTAL_TRIPS = 25_000

# Ensure pickup and drop are at least this far apart (approximate straight-line distance)
MIN_TRIP_DISTANCE_KM = 2.0

# Avoid generating extremely long trips within Bangalore
MAX_TRIP_DISTANCE_KM = 50.0

# Seed for reproducibility
RANDOM_SEED = 42



TRIP_PATTERNS = {

    # -------------------------
    # Residential Areas
    # -------------------------
    "residential_area": {
        "it_park": 0.28,
        "metro_station": 0.18,
        "college": 0.15,
        "mall": 0.10,
        "hospital": 0.10,
        "airport": 0.05,
        "railway_station": 0.05,
        "bus_terminal": 0.04,
        "tourist_attraction": 0.05,
    },

    # -------------------------
    # IT Parks
    # -------------------------
    "it_park": {
        "residential_area": 0.68,
        "airport": 0.10,
        "hotel": 0.10,
        "mall": 0.05,
        "metro_station": 0.05,
        "bus_terminal": 0.02,
    },

    # -------------------------
    # Colleges
    # -------------------------
    "college": {
        "residential_area": 0.68,
        "metro_station": 0.15,
        "mall": 0.10,
        "hospital": 0.05,
        "bus_terminal": 0.02,
    },

    # -------------------------
    # Metro Stations
    # -------------------------
    "metro_station": {
        "residential_area": 0.38,
        "it_park": 0.25,
        "college": 0.15,
        "mall": 0.10,
        "hospital": 0.08,
        "bus_terminal": 0.04,
    },

    # -------------------------
    # Railway Stations
    # -------------------------
    "railway_station": {
        "hotel": 0.28,
        "residential_area": 0.28,
        "airport": 0.15,
        "it_park": 0.10,
        "mall": 0.10,
        "hospital": 0.05,
        "bus_terminal": 0.04,
    },

    # -------------------------
    # Bus Terminals
    # -------------------------
    "bus_terminal": {
        "residential_area": 0.35,
        "railway_station": 0.20,
        "metro_station": 0.15,
        "mall": 0.10,
        "hospital": 0.08,
        "airport": 0.05,
        "hotel": 0.03,
        "college": 0.02,
        "it_park": 0.02,
    },

    # -------------------------
    # Airport
    # -------------------------
    "airport": {
        "hotel": 0.28,
        "residential_area": 0.28,
        "it_park": 0.20,
        "railway_station": 0.10,
        "mall": 0.08,
        "bus_terminal": 0.06,
    },

    # -------------------------
    # Hotels
    # -------------------------
    "hotel": {
        "airport": 0.25,
        "tourist_attraction": 0.33,
        "mall": 0.18,
        "railway_station": 0.10,
        "it_park": 0.10,
        "bus_terminal": 0.04,
    },

    # -------------------------
    # Malls
    # -------------------------
    "mall": {
        "residential_area": 0.48,
        "hotel": 0.15,
        "metro_station": 0.15,
        "it_park": 0.10,
        "hospital": 0.08,
        "bus_terminal": 0.04,
    },

    # -------------------------
    # Hospitals
    # -------------------------
    "hospital": {
        "residential_area": 0.48,
        "metro_station": 0.20,
        "railway_station": 0.10,
        "hotel": 0.10,
        "mall": 0.08,
        "bus_terminal": 0.04,
    },

    # -------------------------
    # Tourist Attractions
    # -------------------------
    "tourist_attraction": {
        "hotel": 0.38,
        "mall": 0.20,
        "metro_station": 0.18,
        "airport": 0.10,
        "residential_area": 0.10,
        "bus_terminal": 0.04,
    },
}