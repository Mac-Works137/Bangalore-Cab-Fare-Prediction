import csv
from pathlib import Path


class FareCSVWriter:

    def __init__(self, csv_path):

        self.csv_path = Path(csv_path)

        # Make sure the parent directory exists.
        self.csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.csv_path.exists():

            with open(
                self.csv_path,
                "w",
                newline="",
                encoding="utf-8",
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "timestamp",
                    "time_slot",
                    "day_of_week",
                    "provider",
                    "pickup",
                    "dropoff",
                    "ride_name",
                    "seats",
                    "current_price",
                    "original_price",
                    "eta_minutes",
                    "arrival_time",
                    "promotion",
                    "description",
                ])

    def append(self, fare):

        with open(
            self.csv_path,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow([

                fare.timestamp,

                fare.time_slot,

                fare.day_of_week,

                fare.provider,

                fare.pickup,

                fare.dropoff,

                fare.ride_name,

                fare.seats,

                fare.current_price,

                fare.original_price,

                fare.eta_minutes,

                fare.arrival_time,

                fare.promotion,

                fare.description,
            ])