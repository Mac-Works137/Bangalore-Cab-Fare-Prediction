"""
Category-specific rules for filtering OpenStreetMap locations.

These rules help remove sub-entities such as departments, offices,
laboratories, stores, etc., while keeping only representative
locations for trip generation.

Rule semantics
--------------
require_required_keywords:
    If True:
        - The location name must contain at least ONE keyword from
          'required_keywords'.

    If False:
        - No inclusion check is performed.

forbidden_keywords:
    If ANY forbidden keyword appears in the location name,
    the location is rejected.

All keyword matching is intended to be:
    - case-insensitive
    - substring-based

Example
-------
"RV College of Engineering"

contains:
    "college"

→ accepted

-------------------------------------------------------

"Central Purchase and Stores"

contains:
    "purchase"
    "stores"

→ rejected
"""

CATEGORY_RULES = {

    ####################################################################
    # AIRPORT
    ####################################################################
    "airport": {
        "require_required_keywords": False,
        "required_keywords": [],
        "forbidden_keywords": [],
    },

    ####################################################################
    # RAILWAY STATION
    ####################################################################
    "railway_station": {
        "require_required_keywords": False,
        "required_keywords": [
            "station",
            "junction",
            "railway",
        ],
        "forbidden_keywords": [
            "booking office",
            "parcel office",
            "ticket office",
        ],
    },

    ####################################################################
    # METRO STATION
    ####################################################################
    "metro_station": {
        "require_required_keywords": False,
        "required_keywords": [
            "station",
        ],
        "forbidden_keywords": [
            "depot",
            "office",
        ],
    },

    ####################################################################
    # BUS TERMINAL
    ####################################################################
    "bus_terminal": {
        "require_required_keywords": True,
        "required_keywords": [
            "bus station",
            "bus stand",
            "terminal",
        ],
        "forbidden_keywords": [
            "bus stop",
        ],
    },

    ####################################################################
    # MALL
    ####################################################################
    "mall": {
        "require_required_keywords": True,
        "required_keywords": [
            "mall",
            "plaza",
            "centre",
            "center",
            "arcade",
        ],
        "forbidden_keywords": [
            "bazaar",
            "factory",
            "westside",
            "manyavar",
            "mohey",
            "silk",
            "store",
            "shop",
        ],
    },

    ####################################################################
    # HOSPITAL
    ####################################################################
    "hospital": {
        "require_required_keywords": True,
        "required_keywords": [
            "hospital",
            "medical centre",
            "medical center",
            "clinic",
            "health centre",
            "health center",
        ],
        "forbidden_keywords": [
            "diagnostic",
            "diagnostics",
            "collection centre",
            "collection center",
            "laboratory",
            "lab",
            "blood bank",
        ],
    },

    ####################################################################
    # COLLEGE
    ####################################################################
    "college": {
        "require_required_keywords": True,
        "required_keywords": [
            "college",
            "university",
            "institute",
            "academy",
            "school",
        ],
        "forbidden_keywords": [
            "department",
            "centre",
            "center",
            "research",
            "laboratory",
            "lab",
            "office",
            "hostel",
            "physics",
            "chemistry",
            "purchase",
            "stores",
            "amenities",
            "club",
            "council",
        ],
    },

    ####################################################################
    # HOTEL
    ####################################################################
    "hotel": {
        "require_required_keywords": True,
        "required_keywords": [
            "hotel",
            "resort",
            "lodge",
            "inn",
            "residency",
            "suite",
            "suites",
        ],
        "forbidden_keywords": [
            "restaurant",
            "bar",
            "cafe",
        ],
    },

    ####################################################################
    # TOURIST ATTRACTION
    ####################################################################
    "tourist_attraction": {
        "require_required_keywords": False,
        "required_keywords": [],
        "forbidden_keywords": [
            "cross",
            "hole",
        ],
    },

    ####################################################################
    # RESIDENTIAL AREA
    ####################################################################
    "residential_area": {
        "require_required_keywords": False,
        "required_keywords": [],
        "forbidden_keywords": [],
    },

    ####################################################################
    # IT PARK
    ####################################################################
    "it_park": {
        "require_required_keywords": True,
        "required_keywords": [
            "tech park",
            "technology park",
            "business park",
            "software",
            "campus",
            "itpb",
        ],
        "forbidden_keywords": [
            "office",
            "store",
            "clinic",
            "finance",
            "railway",
            "commissioner",
            "department",
            "house",
            "printers",
            "travel",
        ],
    },
}