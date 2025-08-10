import requests
import json
from datetime import datetime, timedelta


def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found, using default settings")
        return {
            "time_period": {"days": 1},
            "earthquake_filters": {"minmagnitude": 1.0},
            "api_settings": {"format": "geojson"}
        }


def get_data():
    config = load_config()

    end_time = datetime.now()
    days_back = config["time_period"]["days"]
    start_time = end_time - timedelta(days=days_back)

    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    params = {
        'format': 'geojson',
        'starttime': start_time.strftime('%Y-%m-%d'),
        'endtime': end_time.strftime('%Y-%m-%d')
    }

    earthquake_filters = config.get("earthquake_filters", {})

    if earthquake_filters.get("minmagnitude") is not None:
        params['minmagnitude'] = earthquake_filters["minmagnitude"]

    if earthquake_filters.get("maxmagnitude") is not None:
        params['maxmagnitude'] = earthquake_filters["maxmagnitude"]

    orderby = earthquake_filters.get("orderby")
    if orderby in ["time", "time-asc", "magnitude", "magnitude-asc"]:
        params['orderby'] = orderby

    location_filters = config.get("location_filters", {})
    lat = location_filters.get("latitude")
    lon = location_filters.get("longitude")
    radius_km = location_filters.get("maxradiuskm")

    if lat is not None and lon is not None and radius_km is not None:
        params['latitude'] = lat
        params['longitude'] = lon
        params['maxradiuskm'] = radius_km

    api_limit = config.get("api_settings", {}).get("limit")
    if api_limit and 1 <= api_limit <= 20000:
        params['limit'] = api_limit

    try:
        period_desc = config["time_period"].get("description", f"{days_back} days")
        min_mag = params.get('minmagnitude', 'any')
        print(f"Fetching earthquake data for {period_desc}, magnitude {min_mag}+...")
        print(f"Date range: {params['starttime']} to {params['endtime']}")
        print(f"API URL: {base_url}")
        print(f"Parameters: {params}")

        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"API returned status code: {response.status_code}")
            print(f"Response text: {response.text}")
            response.raise_for_status()

        data = response.json()
        print(f"Successfully fetched {len(data['features'])} earthquakes")

        with open('input/earthquake_data.json', 'w') as f:
            json.dump(data, f, indent=2)

        return data, config

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Full URL: {response.url}")
        return None, config
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, config