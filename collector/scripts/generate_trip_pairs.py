import random
import pandas as pd
from collector.services.route_generator import RouteGenerator
from config.trip_patterns import TOTAL_TRIPS

def weighted_sample_without_replacement(
    routes_df,
    sample_size,
):
    """
    Performs weighted sampling without replacement.
    """

    random.seed(42)

    rows = routes_df.to_dict(
        orient="records"
    )

    selected = []

    sample_size = min(
        sample_size,
        len(rows),
    )

    while len(selected) < sample_size:

        total_weight = sum(
            row["trip_weight"]
            for row in rows
        )

        r = random.uniform(
            0,
            total_weight,
        )

        cumulative = 0

        for i, row in enumerate(rows):

            cumulative += row["trip_weight"]

            if cumulative >= r:

                selected.append(row)

                rows.pop(i)

                break

    return pd.DataFrame(selected)

def main():

    generator = RouteGenerator()

    generator.load_locations(
        "data/raw/locations/validated_locations.csv"
    )

    #
    # Generate every valid unique route
    #

    routes_df = generator.generate_routes()

    print(
        f"\nTotal unique routes available: {len(routes_df)}"
    )

    #
    # Sample 25,000 routes WITHOUT replacement
    #

    sample_size = min(
        TOTAL_TRIPS,
        len(routes_df),
    )

    output_path = (
        "data/raw/trips/trip_pairs.csv"
    )

    trip_pairs = weighted_sample_without_replacement(
        routes_df,
        sample_size,
    )

    trip_pairs.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved {len(trip_pairs)} trips to:"
    )

    print(output_path)


if __name__ == "__main__":
    main()