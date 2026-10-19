import pandas as pd
from pathlib import Path

from config.location_categories import LOCATION_CATEGORIES
from collector.services.osm_service import OSMService

OUTPUT_PATH = Path("data/raw/locations/locations.csv")


def main():

    category_key = "it_park"        # Change this when needed

    service = OSMService()

    df = pd.read_csv(OUTPUT_PATH)

    config = LOCATION_CATEGORIES[category_key]

    locations = service.fetch_locations(config)

    for location in locations:
        location["category_key"] = category_key

    new_df = pd.DataFrame(locations)

    original_count=len(df)
    df = pd.concat([df, new_df], ignore_index=True)
    df = df.drop_duplicates(subset=["osm_id"])
    added=len(df)-original_count
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Added {added} new {category_key} locations.")
    print(f"Total locations: {len(df)}")

if __name__ == "__main__":
    main()