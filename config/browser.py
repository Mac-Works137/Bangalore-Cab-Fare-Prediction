"""
Browser configuration for Playwright.
"""

# Persistent profile directory
PROFILE_DIR = "playwright_profile_bangalore"

# Browser window
VIEWPORT = {
    "width": 390,
    "height": 844,
}

# Bangalore coordinates (Manyata Tech Park area)
GEOLOCATION = {
    "latitude": 13.0475,
    "longitude": 77.6215,
}

# Browser locale
LOCALE = "en-IN"

# Timezone
TIMEZONE = "Asia/Kolkata"

# Grant browser geolocation permission
PERMISSIONS = [
    "geolocation",
]