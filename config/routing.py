"""
Configuration for the Routing module.
"""

# Maximum Trips
MAX_TRIPS_TO_ROUTE = 50

# Route Profile
ROUTING_PROFILE="car"

SAVE_BATCH_SIZE=25

REQUESTS_PER_SECOND=0.25

####################################################################
# ROUTING API
####################################################################

ROUTING_PROVIDER = "graphhopper"

BASE_URL = "https://graphhopper.com/api/1/route"

API_KEY = "f1704322-79d2-4d6a-8196-c04dc40dd241"

####################################################################
# REQUEST SETTINGS
####################################################################

REQUEST_TIMEOUT = 30          # seconds

MAX_RETRIES = 3

####################################################################
# RATE LIMITING
####################################################################

REQUEST_DELAY = 0.5           # seconds between API calls

MINUTE_LIMIT_SLEEP = 60      # seconds
MAX_MINUTE_LIMIT_RETRIES = 5
####################################################################
# BATCH PROCESSING
####################################################################

PROGRESS_INTERVAL = 100

####################################################################
# OUTPUT SETTINGS
####################################################################

ROAD_DISTANCE_DECIMALS = 3

DURATION_DECIMALS = 2