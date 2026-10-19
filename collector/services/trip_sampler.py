import pandas as pd

from config.sampling import (
    CATEGORY_WEIGHTS,
    DAILY_SAMPLE_SIZE,
)


class TripSampler:

    def __init__(self):

        self.trip_pairs_df = None

    def load_trip_pairs(self, input_path):
        """
        Loads the generated trip pairs dataset.
        """

        self.trip_pairs_df = pd.read_csv(input_path)

    def initialize_sampling_column(self):
        """
        Adds the is_routed column if it does not already exist.
        """

        if "is_routed" not in self.trip_pairs_df.columns:
            self.trip_pairs_df["is_routed"] = False

    def compute_trip_weights(self):
        """
        Computes a sampling weight for every trip based on the
        pickup and drop categories.
        """

        pickup_weights = (
            self.trip_pairs_df["pickup_category"]
            .map(CATEGORY_WEIGHTS)
            .fillna(1)
        )

        drop_weights = (
            self.trip_pairs_df["drop_category"]
            .map(CATEGORY_WEIGHTS)
            .fillna(1)
        )

        self.trip_pairs_df["trip_weight"] = (
            pickup_weights + drop_weights
        )

    def sample_trips(self):
        """
        Samples today's trips using weighted random sampling.
        """

        available_trips = self.trip_pairs_df[
            self.trip_pairs_df["is_routed"] == False
        ]

        sample_size = min(
            DAILY_SAMPLE_SIZE,
            len(available_trips),
        )

        sampled_trips = available_trips.sample(
            n=sample_size,
            weights="trip_weight",
            replace=False,
            random_state=None,
        )

        return sampled_trips
    
    def mark_as_routed(self, routed_indices):
        """
        Marks the sampled trips as routed.
        """

        self.trip_pairs_df.loc[
            routed_indices,
            "is_routed"
        ] = True
    
    def save_trip_pairs(self, output_path):
        """
        Saves the updated trip pairs dataset.
        """

        self.trip_pairs_df.to_csv(
            output_path,
            index=False,
        )