import pandas as pd

from config.collection_schedule import UBER_FARES_CSV


def main():
    print("=" * 70)
    print("UBER FARE DATA QUALITY AUDIT")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load data
    # ---------------------------------------------------------
    df = pd.read_csv(UBER_FARES_CSV)

    print(f"\nFare file: {UBER_FARES_CSV}")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    # ---------------------------------------------------------
    # 2. Columns
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("COLUMNS")
    print("-" * 70)

    for column in df.columns:
        print(f"- {column}")

    # ---------------------------------------------------------
    # 3. Missing values
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("MISSING VALUES")
    print("-" * 70)

    missing = df.isnull().sum()

    for column, count in missing.items():
        if count > 0:
            print(f"{column}: {count}")

    if missing.sum() == 0:
        print("No missing values found.")

    # ---------------------------------------------------------
    # 4. Duplicate rows
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("DUPLICATES")
    print("-" * 70)

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_count}")

    # ---------------------------------------------------------
    # 5. Timestamp information
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("TIMESTAMP")
    print("-" * 70)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps = df["timestamp"].isna().sum()

    print(f"Invalid timestamps: {invalid_timestamps}")

    if df["timestamp"].notna().any():
        print(f"Earliest timestamp: {df['timestamp'].min()}")
        print(f"Latest timestamp  : {df['timestamp'].max()}")

    # ---------------------------------------------------------
    # 6. Providers
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("PROVIDERS")
    print("-" * 70)

    print(df["provider"].value_counts(dropna=False))

    # ---------------------------------------------------------
    # 7. Unique routes
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("ROUTES")
    print("-" * 70)

    unique_routes = df[
        ["pickup", "dropoff"]
    ].drop_duplicates()

    print(f"Unique pickup/dropoff routes: {len(unique_routes)}")

    # ---------------------------------------------------------
    # 8. Observations per route
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("OBSERVATIONS PER ROUTE")
    print("-" * 70)

    route_counts = (
        df.groupby(
            ["pickup", "dropoff"]
        )
        .size()
        .sort_values(ascending=False)
    )

    print(f"Minimum observations per route: {route_counts.min()}")
    print(f"Maximum observations per route: {route_counts.max()}")
    print(f"Average observations per route: {route_counts.mean():.2f}")

    print("\nTop routes by number of observations:")

    for route, count in route_counts.head(10).items():
        pickup, dropoff = route
        print(f"{count:>3} | {pickup} -> {dropoff}")

    # ---------------------------------------------------------
    # 9. Ride types
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("UBER RIDE TYPES")
    print("-" * 70)

    ride_counts = df["ride_name"].value_counts()

    print(f"Unique ride types: {df['ride_name'].nunique()}")

    print("\nRide type counts:")

    for ride_name, count in ride_counts.items():
        print(f"{count:>3} | {ride_name}")

    # ---------------------------------------------------------
    # 10. Fare / price statistics
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("CURRENT PRICE")
    print("-" * 70)

    df["current_price"] = pd.to_numeric(
        df["current_price"],
        errors="coerce"
    )

    print(df["current_price"].describe())

    invalid_prices = (
        df["current_price"].isna()
        | (df["current_price"] <= 0)
    ).sum()

    print(f"\nInvalid/non-positive prices: {invalid_prices}")

    # ---------------------------------------------------------
    # 11. Original price
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("ORIGINAL PRICE")
    print("-" * 70)

    df["original_price"] = pd.to_numeric(
        df["original_price"],
        errors="coerce"
    )

    original_price_available = df["original_price"].notna().sum()

    print(
        f"Rows with original price: "
        f"{original_price_available} / {len(df)}"
    )

    # ---------------------------------------------------------
    # 12. Promotion
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("PROMOTIONS")
    print("-" * 70)

    promotion_available = df["promotion"].notna().sum()

    print(
        f"Rows with promotion information: "
        f"{promotion_available} / {len(df)}"
    )

    if promotion_available > 0:
        print("\nPromotion values:")
        print(df["promotion"].value_counts(dropna=False).head(20))

    # ---------------------------------------------------------
    # 13. ETA
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("ETA")
    print("-" * 70)

    df["eta_minutes"] = pd.to_numeric(
        df["eta_minutes"],
        errors="coerce"
    )

    print(df["eta_minutes"].describe())

    invalid_eta = (
        df["eta_minutes"].notna()
        & (df["eta_minutes"] < 0)
    ).sum()

    print(f"\nNegative ETA values: {invalid_eta}")

    # ---------------------------------------------------------
    # 14. Collection slots
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("TIME SLOTS")
    print("-" * 70)

    print(df["time_slot"].value_counts(dropna=False).sort_index())

    # ---------------------------------------------------------
    # 15. Days of week
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("DAYS OF WEEK")
    print("-" * 70)

    print(df["day_of_week"].value_counts(dropna=False))

    # ---------------------------------------------------------
    # 16. Price distribution by ride type
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("PRICE BY RIDE TYPE")
    print("-" * 70)

    price_by_ride = (
        df.groupby("ride_name")["current_price"]
        .agg(
            count="count",
            mean="mean",
            median="median",
            min="min",
            max="max",
        )
        .sort_values("count", ascending=False)
    )

    print(price_by_ride.to_string())

    # ---------------------------------------------------------
    # 17. Same route + ride type observations
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("ROUTE + RIDE TYPE OBSERVATIONS")
    print("-" * 70)

    route_ride_counts = (
        df.groupby(
            ["pickup", "dropoff", "ride_name"]
        )
        .size()
        .sort_values(ascending=False)
    )

    print(
        f"Unique route + ride type combinations: "
        f"{len(route_ride_counts)}"
    )

    print("\nTop route + ride type combinations:")

    for key, count in route_ride_counts.head(10).items():
        pickup, dropoff, ride_name = key

        print(
            f"{count:>3} | "
            f"{pickup} -> {dropoff} | "
            f"{ride_name}"
        )

    # ---------------------------------------------------------
    # 18. Potential price anomalies
    # ---------------------------------------------------------
    print("\n" + "-" * 70)
    print("POTENTIAL PRICE ANOMALIES")
    print("-" * 70)

    if df["current_price"].notna().any():
        q1 = df["current_price"].quantile(0.25)
        q3 = df["current_price"].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        anomalies = df[
            (df["current_price"] < lower_bound)
            | (df["current_price"] > upper_bound)
        ]

        print(f"Q1: {q1:.2f}")
        print(f"Q3: {q3:.2f}")
        print(f"IQR: {iqr:.2f}")
        print(f"Lower bound: {lower_bound:.2f}")
        print(f"Upper bound: {upper_bound:.2f}")
        print(f"Potential price anomalies: {len(anomalies)}")

        if len(anomalies) > 0:
            print("\nHighest priced observations:")

            highest = (
                df.nlargest(10, "current_price")[
                    [
                        "pickup",
                        "dropoff",
                        "ride_name",
                        "current_price",
                        "time_slot",
                        "day_of_week",
                    ]
                ]
            )

            print(highest.to_string(index=False))

    # ---------------------------------------------------------
    # 19. Final summary
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    print(f"Rows                    : {len(df)}")
    print(f"Unique routes            : {len(unique_routes)}")
    print(f"Unique ride types        : {df['ride_name'].nunique()}")
    print(f"Duplicate rows           : {duplicate_count}")
    print(f"Invalid timestamps       : {invalid_timestamps}")
    print(f"Invalid/non-positive fare: {invalid_prices}")
    print(f"Negative ETA values      : {invalid_eta}")

    print("\nNo files were modified.")


if __name__ == "__main__":
    main()