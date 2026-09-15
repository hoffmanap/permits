import json
import os
import urllib.parse
import urllib.request

ENDPOINTS = {
    "residential": "https://gis.elpasotexas.gov/arcgis/rest/services/Planning/NewResidential/FeatureServer/1",
    "commercial": "https://gis.elpasotexas.gov/arcgis/rest/services/Planning/NewCommercial/FeatureServer/0",
}


def fetch_layer_geojson(base_url: str) -> dict:
    query_url = f"{base_url.rstrip('/')}/query"
    offset = 0
    record_limit = 1000
    all_features = []

    while True:
        params = {
            "where": "1=1",
            "outFields": "*",  # Explicitly request all schema attributes
            "outSR": "4326",  # Force WGS84 Lat/Lng projection
            "f": "geojson",
            "resultRecordCount": record_limit,
            "resultOffset": offset,
        }

        url = f"{query_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"Error requesting {url}: {e}")
            break

        features = data.get("features", [])
        if not features:
            break

        # Retain features with valid geometry
        valid_features = [
            f
            for f in features
            if f.get("geometry") and f["geometry"].get("coordinates")
        ]
        all_features.extend(valid_features)

        print(f"Fetched {len(all_features)} records so far...")

        if len(features) < record_limit:
            break

        offset += record_limit

    return {"type": "FeatureCollection", "features": all_features}


def main():
    os.makedirs("data", exist_ok=True)

    for name, endpoint in ENDPOINTS.items():
        print(f"\n--- Fetching {name.upper()} dataset ---")
        geojson_data = fetch_layer_geojson(endpoint)
        output_path = os.path.join("data", f"{name}.geojson")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f)

        print(
            f"Successfully saved {len(geojson_data['features'])} features to {output_path}"
        )


if __name__ == "__main__":
    main()
