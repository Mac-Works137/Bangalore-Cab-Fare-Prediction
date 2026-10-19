from collector.services.osm_service import OSMService
from config.location_categories import LOCATION_CATEGORIES

service = OSMService()

category_config = LOCATION_CATEGORIES["college"]

locations = service.fetch_locations(category_config)

print(f"Fetched {len(locations)} locations.\n")

for location in locations[:5]:
    print(location)