"""
Service for interacting with the OpenStreetMap Overpass API.

Responsibilities:
1. Build Overpass queries.
2. Fetch locations from OSM.
3. Parse API responses.
4. Remove duplicate locations.
"""

import requests
import time

from config.location_categories import BANGALORE_CENTER

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

REQUEST_TIMEOUT = 60

class OSMService:
    """Handles communication with the Overpass API."""
    def __init__(self):
        self.base_url = OVERPASS_URL
        self.timeout = REQUEST_TIMEOUT

    def fetch_locations(self, category_config: dict) -> list[dict]:
        osm_tags = category_config["osm_tags"]
        radius = category_config["search_radius_m"]
        category = category_config["category"]
        subcategory = category_config["subcategory"]
        target_count = category_config["target_count"]

        all_locations = []

        for tag in osm_tags:
            query = self._build_query(tag, radius)

            
            response = self._call_overpass(query)

            locations = self._parse_response(response)

            all_locations.extend(locations)

        all_locations = self._remove_duplicates(all_locations)

        for location in all_locations:
            location["category"] = category
            location["subcategory"] = subcategory

        return all_locations[:target_count]

    def _build_query(self, tag: dict, radius: int) -> str:
        tag_filter = ""

        for key, value in tag.items():
            tag_filter += f'["{key}"="{value}"]'

        lat = BANGALORE_CENTER["latitude"]
        lon = BANGALORE_CENTER["longitude"]

        return f"""
        [out:json];
        (
            node{tag_filter}(around:{radius},{lat},{lon});
            way{tag_filter}(around:{radius},{lat},{lon});
            relation{tag_filter}(around:{radius},{lat},{lon});
        );
        out center;
        """

    def _call_overpass(self, query: str) -> dict:

        headers = {
            "User-Agent": "BangaloreCabFarePrediction/1.0"
        }

        max_retries = 3

        for attempt in range(max_retries):

            try:
                response = requests.post(
                    self.base_url,
                    data={"data": query},
                    headers=headers,
                    timeout=self.timeout
                )

                response.raise_for_status()

                return response.json()

            except requests.exceptions.HTTPError as e:

                if response.status_code == 504 and attempt < max_retries - 1:
                    print(
                        f"Server busy. Retrying "
                        f"({attempt + 1}/{max_retries})..."
                    )
                    time.sleep(10)
                    continue
                
                if response.status_code==429 and attempt<max_retries-1:
                    print(
                        f"Rate limit reached. Waiting 30 seconds "
                        f"({attempt + 1}/{max_retries})..."
                    )

                    
                    time.sleep(30)
                    continue


                raise RuntimeError(
                    f"Overpass API returned an HTTP error: {e}"
                )

            except requests.exceptions.Timeout:

                if attempt < max_retries - 1:
                    print(
                        f"Request timed out. Retrying "
                        f"({attempt + 1}/{max_retries})..."
                    )
                    time.sleep(5)
                    continue

                raise RuntimeError(
                    "Overpass API request timed out."
                )

            except requests.exceptions.RequestException as e:
                raise RuntimeError(
                    f"Failed to communicate with the Overpass API: {e}"
                )

            except ValueError:
                raise RuntimeError(
                    "Invalid JSON received from the Overpass API."
                )

    def _parse_response(self, response: dict) -> list[dict]:
        locations = []

        elements = response.get("elements", [])

        for element in elements:
            if element["type"] == "node":
                lat = element.get("lat")
                lon = element.get("lon")
            else:
                center = element.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            tags = element.get("tags", {})

            if lat is None or lon is None:
                continue
            
            locations.append({
                "osm_id": f'{element["type"]}/{element["id"]}',
                "osm_type": element["type"],
                "name": tags.get("name", ""),
                "latitude": lat,
                "longitude": lon,
                "address": "",
                "category": "",
                "subcategory": ""
            })

        return locations

    def _remove_duplicates(self, locations: list[dict]) -> list[dict]:
        seen = set()
        unique_locations = []

        for location in locations:
            osm_id = location.get("osm_id")

            if osm_id is None:
                continue

            if osm_id not in seen:
                seen.add(osm_id)
                unique_locations.append(location)

        return unique_locations
