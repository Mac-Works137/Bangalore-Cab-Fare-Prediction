import pandas as pd

df = pd.read_csv(
    "data/raw/trips/trip_pairs.csv"
)

duplicates = df.duplicated(
    subset=[
        "pickup_osm_id",
        "drop_osm_id",
    ]
)

duplicate_rows = df[duplicates]

print(f"Total routes      : {len(df)}")
print(f"Duplicate routes  : {len(duplicate_rows)}")
print(
    f"Unique routes     : "
    f"{len(df)-len(duplicate_rows)}"
)

if len(duplicate_rows) > 0:
    print("\nExamples:\n")

    print(
        duplicate_rows[
            [
                "pickup_name",
                "drop_name",
            ]
        ].head(20)
    )