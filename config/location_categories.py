"""
Configuration for all supported Bangalore location categories.

This file defines:
1. High-level category
2. Subcategory
3. Target number of locations
4. Search radius
5. OpenStreetMap tags used for fetching locations
"""

# Default search radius (in meters) around Bangalore.
DEFAULT_SEARCH_RADIUS_M = 50000

# Center coordinates of Bangalore (used for Overpass API radius searches).
BANGALORE_CENTER = {
    "latitude": 12.9716,
    "longitude": 77.5946,
}

# Maps each supported location type to its metadata and
# the corresponding OpenStreetMap tags used for fetching.
LOCATION_CATEGORIES = {

    "airport": {
        "category": "Transport",
        "subcategory": "Airport",
        "target_count": 1,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "aeroway": "aerodrome"
            }
        ]
    },

    "railway_station": {
        "category": "Transport",
        "subcategory": "Railway Station",
        "target_count": 10,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "railway": "station"
            }
        ]
    },

    "metro_station": {
        "category": "Transport",
        "subcategory": "Metro Station",
        "target_count": 40,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "railway": "station",
                "station": "subway"
            },
            {
                "railway": "subway_entrance"
            }
        ]
    },

    "bus_terminal": {
        "category": "Transport",
        "subcategory": "Bus Terminal",
        "target_count": 15,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "amenity": "bus_station"
            }
        ]
    },

    "it_park": {
        "category": "Commercial",
        "subcategory": "IT Park",
        "target_count": 40,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "landuse": "commercial"
            },
            {
                "office": "company"
            },
            {
                "office": "it"
            },
            {
                "building": "office"
            }
        ]
    },

    "mall": {
        "category": "Commercial",
        "subcategory": "Mall",
        "target_count": 25,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "shop": "mall"
            }
        ]
    },

    "hospital": {
        "category": "Healthcare",
        "subcategory": "Hospital",
        "target_count": 25,
        "search_radius_m": 10000,
        "osm_tags": [
            {
                "amenity": "hospital"
            }
        ]
    },

    "college": {
        "category": "Education",
        "subcategory": "College / University",
        "target_count": 30,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "amenity": "college"
            },
            {
                "amenity": "university"
            }
        ]
    },

    "hotel": {
        "category": "Hospitality",
        "subcategory": "Hotel",
        "target_count": 20,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "tourism": "hotel"
            }
        ]
    },

    "tourist_attraction": {
        "category": "Recreation",
        "subcategory": "Tourist Attraction",
        "target_count": 15,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "tourism": "attraction"
            }
        ]
    },

    "residential_area": {
        "category": "Residential",
        "subcategory": "Residential Area",
        "target_count": 29,
        "search_radius_m": DEFAULT_SEARCH_RADIUS_M,
        "osm_tags": [
            {
                "landuse": "residential"
            },
            {
                "place": "suburb"
            },
            {
                "place": "neighbourhood"
            }
        ]
    }


}