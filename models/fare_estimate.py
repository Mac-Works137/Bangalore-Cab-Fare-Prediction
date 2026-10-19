from dataclasses import dataclass
from datetime import datetime


@dataclass
class FareEstimate:

    provider: str

    pickup: str

    dropoff: str

    ride_name: str

    seats: int | None

    current_price: float | None

    original_price: float | None

    eta_minutes: int | None

    arrival_time: str | None

    promotion: str | None

    description: str | None

    timestamp: datetime

    time_slot: str | None

    day_of_week: str | None