import pandas as pd

locations = pd.read_csv(
    "data/raw/locations/locations.csv"
)

count = len(locations)

print(f"Locations after filtering: {count}")

max_unique_routes = count * (count - 1)

print(f"Maximum possible directed routes: {max_unique_routes}")