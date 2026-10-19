"""
Fetches Bangalore locations from OpenStreetMap
and saves them as locations.csv.
"""

import time
import pandas as pd
from pathlib import Path

from config.location_categories import LOCATION_CATEGORIES
from collector.services.osm_service import OSMService

OUTPUT_PATH = Path("data/raw/locations/locations.csv")

def main():
    service = OSMService()

    all_locations = []

    summary={}

    

    print("Starting OpenStreetMap location collection...\n")

    for category_key, category_config in LOCATION_CATEGORIES.items():

        print(f"Fetching '{category_key}'...")

        try:
            locations = service.fetch_locations(category_config)

            summary[category_key]={
                "status":"Success",
                "count":len(locations),
                "target": category_config["target_count"]
            }

            expected_count = category_config["target_count"]

            if len(locations) < expected_count:
                print(
                    f"  Warning: Expected {expected_count} locations "
                    f"but found only {len(locations)}."
                )

            for location in locations:
                location["category_key"] = category_key

            all_locations.extend(locations)

            

            print(f"  Success: Collected {len(locations)} locations.\n")

        except Exception as e:
            
            

            print(
                f"  Failed to fetch '{category_key}'. "
                f"Reason: {e}\n"
            )

            summary[category_key]={
                    "status":"Failed",
                    "count":0,
                    "error":str(e)
            }

            

        
        
        time.sleep(10)

    # Create output directory if it does not exist
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save to CSV
    df = pd.DataFrame(all_locations)
    if not df.empty:
        
        df.to_csv(
            OUTPUT_PATH,
            index=False
        )
    
    else:
        print("No locations were collected.")

    print("\n=============== COLLECTION SUMMARY ==================\n")
    success_count=0
    failed_count=0
    for category,info in summary.items():
        if info["status"]=="Success":
            success_count+=1

            if info["count"]==info["target"]:
                print(
                    f"{category:<25}"
                    f"{info['count']}/{info['target']}"
                )
            else:
                print(
                    f"{category:<25}"
                    f"{info['count']}/{info['target']} "
                    f"(Target not met)"
                )
        else:
            failed_count+=1
            print(
                f"{category:<25}"
                f"{info['error']}"
            )
    
    # Final Summary
    print("\n" + "=" * 60)
    print("Location Collection Summary")
    print("=" * 60)
    print(f"Successful categories : {success_count}")
    print(f"Failed categories     : {failed_count}")
    print(f"Total locations saved : {len(df)}")
    print(f"Output file           : {OUTPUT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()