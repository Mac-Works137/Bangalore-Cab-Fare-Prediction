import random
from math import radians, sin, cos, sqrt, atan2

import pandas as pd

from config.trip_patterns import (
    RANDOM_SEED,
    TOTAL_TRIPS,
    TRIP_PATTERNS,
    MIN_TRIP_DISTANCE_KM,
    MAX_TRIP_DISTANCE_KM,
)
from config.location_rules import CATEGORY_RULES

class TripGenerator:

    def __init__(self):

        random.seed(RANDOM_SEED)

        self.locations_df = None

        self.locations_by_category = {}

        self.generated_trips = []

        self.rejection_counts={}

        self.total_generation_attempts = 0

        self.total_generation_attempts=0
    
    def load_locations(self, csv_path):

        self.locations_df = pd.read_csv(csv_path)

        if self.locations_df.empty:
            raise ValueError("locations.csv is empty.")

        self._apply_location_rules()
        self._load_category_groups()
        self._validate_configuration()

    def _apply_location_rules(self):
        """
        Filters the loaded locations according to the rules defined in
        config/location_rules.py and prints a summary of the filtering.
        """

        print("\nApplying location filtering rules...\n")

        # ---------------------------------------------------------
        # Count locations before filtering
        # ---------------------------------------------------------

        before_counts = (
            self.locations_df["category_key"]
            .value_counts()
            .to_dict()
        )

        filtered_rows = []

        # Stores the complete rows of removed locations
        removed_locations = {}

        # ---------------------------------------------------------
        # Apply filtering rules
        # ---------------------------------------------------------

        for _, row in self.locations_df.iterrows():

            if self._is_valid_location(row):

                filtered_rows.append(row)

            else:

                category = row["category_key"]

                if category not in removed_locations:
                    removed_locations[category] = []

                removed_locations[category].append(row)

        # ---------------------------------------------------------
        # Replace dataframe with filtered dataframe
        # ---------------------------------------------------------

        self.locations_df = pd.DataFrame(filtered_rows)

        # ---------------------------------------------------------
        # Count locations after filtering
        # ---------------------------------------------------------

        after_counts = (
            self.locations_df["category_key"]
            .value_counts()
            .to_dict()
        )

        # ---------------------------------------------------------
        # Print filtering summary
        # ---------------------------------------------------------

        print("Filtering Summary")
        print("-" * 65)

        print(
            f"{'Category':<22}"
            f"{'Before':>8}"
            f"{'After':>8}"
            f"{'Removed':>10}"
        )

        print("-" * 65)

        categories = sorted(before_counts.keys())

        total_before = 0
        total_after = 0

        for category in categories:

            before = before_counts.get(category, 0)
            after = after_counts.get(category, 0)

            removed = before - after

            total_before += before
            total_after += after

            print(
                f"{category:<22}"
                f"{before:>8}"
                f"{after:>8}"
                f"{removed:>10}"
            )

        print("-" * 65)

        print(
            f"{'Total':<22}"
            f"{total_before:>8}"
            f"{total_after:>8}"
            f"{total_before-total_after:>10}"
        )

        # ---------------------------------------------------------
        # Print removed locations
        # ---------------------------------------------------------

        print("\nRemoved Locations")
        print("-" * 65)

        if not removed_locations:

            print("No locations were removed.")

        else:

            for category in sorted(removed_locations.keys()):

                print(f"\n{category}:")

                for row in sorted(
                    removed_locations[category],
                    key=lambda x: str(x["name"]).lower()
                ):

                    print(
                        f"    - {row['name']} "
                        f"({row['latitude']:.6f}, "
                        f"{row['longitude']:.6f})"
                    )

        print()

    def _is_valid_location(self, row):
        """
        Returns True if the location satisfies the filtering rules for its
        category.
        """

        category = row["category_key"]

        name = str(row["name"]).strip().lower()

        # If we encounter a nan value then we return false
        # Eventually dealing with the nan values here instead of in the dataset
        if not name or name=="nan":
            return False 
        
        rules = CATEGORY_RULES.get(category)

        if rules is None:
            return True

        # ---------------------------------------------------------
        # Check required keywords
        # ---------------------------------------------------------

        if rules["require_required_keywords"]:

            has_required_keyword = any(
                keyword in name
                for keyword in rules["required_keywords"]
            )

            if not has_required_keyword:
                return False

        # ---------------------------------------------------------
        # Check forbidden keywords
        # ---------------------------------------------------------

        has_forbidden_keyword = any(
            keyword in name
            for keyword in rules["forbidden_keywords"]
        )

        if has_forbidden_keyword:
            return False

        return True

    def _load_category_groups(self):

        self.locations_by_category = {}

        grouped = self.locations_df.groupby("category_key")

        for category, group in grouped:

            self.locations_by_category[category] = group.to_dict(
                orient="records"
            )


    def _validate_configuration(self):
        """
        Validates that the trip generation configuration matches the
        available location categories.
        """

        available_categories = set(self.locations_by_category.keys())

        configured_categories = set(TRIP_PATTERNS.keys())

        # -------------------------------
        # Check 1
        # -------------------------------

        missing_patterns = available_categories - configured_categories

        if missing_patterns:
            raise ValueError(
                f"Missing trip patterns for categories: {sorted(missing_patterns)}"
            )

        # -------------------------------
        # Check 2
        # -------------------------------

        for pickup_category, destinations in TRIP_PATTERNS.items():

            for destination_category in destinations:

                if destination_category not in available_categories:

                    raise ValueError(
                        f"Unknown destination category "
                        f"'{destination_category}' "
                        f"in trip pattern for '{pickup_category}'."
                    )

        # -------------------------------
        # Check 3
        # -------------------------------

        for pickup_category, destinations in TRIP_PATTERNS.items():

            total_weight = sum(destinations.values())

            if abs(total_weight - 1.0) > 1e-6:

                raise ValueError(
                    f"Trip pattern weights for '{pickup_category}' "
                    f"sum to {total_weight:.4f} instead of 1.0."
                )
    

    def _choose_pickup_category(self):
        """
        Randomly selects a pickup category.
        """

        categories=list(TRIP_PATTERNS.keys())
        return random.choice(categories)

    def _choose_drop_category(self, pickup_category):
        """
        Randomly selects a destination category based on the
        configured trip patterns.
        """

        destinations = TRIP_PATTERNS[pickup_category]

        categories = list(destinations.keys())
        weights = list(destinations.values())

        return random.choices(
            categories,
            weights=weights,
            k=1
        )[0]
    
    def _choose_random_location(self, category):
        """
        Returns a random location belonging to the given category.
        """

        return random.choice(self.locations_by_category[category])

    def _calculate_distance(self, pickup_location, drop_location):
        """
        Calculates the great-circle distance (in kilometers) between
        two locations using the Haversine formula.

        Parameters
        ----------
        pickup_location : dict
            Pickup location.

        drop_location : dict
            Drop location.

        Returns
        -------
        float
            Distance in kilometers.
        """
        if(pickup_location["latitude"] is None
           or pickup_location["longitude"] is None
           or drop_location["latitude"] is None
           or drop_location["longitude"] is None
           ):
                raise ValueError("Location coordinates cannot be None.")
        
        EARTH_RADIUS_KM = 6371.0

        lat1 = radians(pickup_location["latitude"])
        lon1 = radians(pickup_location["longitude"])

        lat2 = radians(drop_location["latitude"])
        lon2 = radians(drop_location["longitude"])

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            sin(delta_lat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(delta_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return EARTH_RADIUS_KM * c

    def _is_valid_trip(
        self,
        pickup_location,
        drop_location,
        distance_km,
    ):
        """
        Validates a generated trip.

        Parameters
        ----------
        pickup_location : dict
            Pickup location.

        drop_location : dict
            Drop location.

        distance_km : float
            Great-circle distance between the pickup and drop locations.

        Returns
        -------
        tuple
            (is_valid, rejection_reason)

            If valid:
                (True, None)

            If invalid:
                (False, "same_location")
                (False, "distance_too_small")
                (False, "distance_too_large")
        """

        # ---------------------------------------------------------
        # Pickup and drop cannot be the same location.
        # ---------------------------------------------------------

        if pickup_location["osm_id"] == drop_location["osm_id"]:
            return False, "same_location"

        # ---------------------------------------------------------
        # Trip must satisfy minimum distance.
        # ---------------------------------------------------------

        if distance_km < MIN_TRIP_DISTANCE_KM:
            return False, "distance_too_small"

        # ---------------------------------------------------------
        # Trip must satisfy maximum distance.
        # ---------------------------------------------------------

        if distance_km > MAX_TRIP_DISTANCE_KM:
            return False, "distance_too_large"

        return True, None
    
    def _generate_single_trip(self):
        """
        Generates and returns a single valid trip.

        Raises
        ------
        RuntimeError
            If a valid trip cannot be generated within the maximum
            number of attempts.
        """

        MAX_GENERATION_ATTEMPTS = 1000

        for _ in range(MAX_GENERATION_ATTEMPTS):

            # Increment the generation count
            self.total_generation_attempts+=1

            # ---------------------------------------------------------
            # Select pickup category and location.
            # ---------------------------------------------------------

            pickup_category = self._choose_pickup_category()

            pickup_location = self._choose_random_location(
                pickup_category
            )

            # ---------------------------------------------------------
            # Select drop category and location.
            # ---------------------------------------------------------

            drop_category = self._choose_drop_category(
                pickup_category
            )

            drop_location = self._choose_random_location(
                drop_category
            )

            # ---------------------------------------------------------
            # Calculate trip distance.
            # ---------------------------------------------------------

            distance_km = self._calculate_distance(
                pickup_location,
                drop_location
            )

            # ---------------------------------------------------------
            # Validate the generated trip.
            # ---------------------------------------------------------

            is_valid, rejection_reason = self._is_valid_trip(
                pickup_location,
                drop_location,
                distance_km
            )

            if not is_valid:

                self.rejection_counts[rejection_reason] = (
                    self.rejection_counts.get(rejection_reason, 0) + 1
                )

                continue

            # ---------------------------------------------------------
            # Return the generated trip.
            # ---------------------------------------------------------

            trip = {
                "pickup_osm_id": pickup_location["osm_id"],
                "pickup_name": pickup_location["name"],
                "pickup_category": pickup_category,
                "pickup_latitude": pickup_location["latitude"],
                "pickup_longitude": pickup_location["longitude"],

                "drop_osm_id": drop_location["osm_id"],
                "drop_name": drop_location["name"],
                "drop_category": drop_category,
                "drop_latitude": drop_location["latitude"],
                "drop_longitude": drop_location["longitude"],

                "distance_km": round(distance_km, 3),
            }

            pair = (
                trip["pickup_osm_id"],
                trip["drop_osm_id"],
            )

            if pair in self.generated_pairs:

                self.rejection_counts["duplicate_route"] = (
                    self.rejection_counts.get("duplicate_route", 0) + 1
                )

                continue

            self.generated_pairs.add(pair)

            return trip

        raise RuntimeError(
            f"Failed to generate a valid trip after "
            f"{MAX_GENERATION_ATTEMPTS} attempts."
        )

    def generate_trip_pairs(self):
        """
        Generates the configured number of trip pairs.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing the generated trips.
        """

        self.generated_trips = []

        self.generated_pairs=set()

        while len(self.generated_trips) < TOTAL_TRIPS:

            trip = self._generate_single_trip()

            self.generated_trips.append(trip)

            if len(self.generated_trips) % 1000 == 0:

                print(
                    f"Generated {len(self.generated_trips)}/{TOTAL_TRIPS} trips..."
                )

        trips_df = pd.DataFrame(self.generated_trips)

        print("\nTrip generation completed successfully.")
        print(f"Generated trips : {len(trips_df)}")
        print(f"Total attempts       : {self.total_generation_attempts}")
        print(
            f"Rejected attempts    : "
            f"{self.total_generation_attempts - len(trips_df)}"
        )

        if self.rejection_counts:

            print("\nRejected trip summary:")

            for reason, count in sorted(self.rejection_counts.items()):
                print(f"  {reason}: {count}")

        return trips_df

"""
if __name__ == "__main__":

    generator = TripGenerator()

    generator.load_locations("data/raw/locations/locations.csv")

    trips_df = generator.generate_trip_pairs()

    print(trips_df.head())
"""