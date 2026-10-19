from collector.services.trip_sampler import TripSampler
from collector.services.routing_service import RoutingService


def main():

    # -------------------------------
    # File paths
    # -------------------------------

    trip_pairs_path = "data/raw/trips/trip_pairs.csv"

    routes_output_path = (
        "data/processed/routes/routes.csv"
    )

    # -------------------------------
    # Sample today's trips
    # -------------------------------

    sampler = TripSampler()

    sampler.load_trip_pairs(trip_pairs_path)

    sampler.initialize_sampling_column()

    sampler.compute_trip_weights()

    sampled_trips = sampler.sample_trips()

    print(f"Sampled {len(sampled_trips)} trips.")

    # -------------------------------
    # Route the sampled trips
    # -------------------------------

    routing_service = RoutingService()

    routing_service.set_trips(sampled_trips)

    successful_indices = routing_service.enrich_routes(
        routes_output_path
    )

    # -------------------------------
    # Update routing status
    # -------------------------------

    sampler.mark_as_routed(successful_indices)

    sampler.save_trip_pairs(trip_pairs_path)

    print(
        f"\nMarked {len(successful_indices)} trips as routed."
    )

    print("\nDaily route collection completed successfully.")


if __name__ == "__main__":
    main()