from collector.services.trip_sampler import TripSampler

sampler = TripSampler()

sampler.load_trip_pairs(
    "data/raw/trips/trip_pairs.csv"
)

sampler.initialize_sampling_column()

sampler.compute_trip_weights()

sampled_trips = sampler.sample_trips()

sampler.mark_as_routed(sampled_trips)

print(
    sampler.trip_pairs_df.loc[
        sampled_trips.index,
        "is_routed"
    ].head()
)

sampler.save_trip_pairs(
    "data/raw/trips/trip_pairs.csv"
)