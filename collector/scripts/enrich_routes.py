from collector.services.routing_service import RoutingService

service = RoutingService()

service.load_trips("data/raw/trips/trip_pairs.csv")

trip = service.trips_df.iloc[0]

service.enrich_routes(
    "data/processed/routes/routes_test.csv"
)