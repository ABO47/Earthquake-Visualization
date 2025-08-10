from src.api import get_data


def process_data():
    data, config = get_data()

    if not data:
        return [], [], [], config

    features = data.get('features', [])
    mags, lats, lons = [], [], []

    for earthquake in features:
        try:
            mag = earthquake['properties']['mag']
            coords = earthquake['geometry']['coordinates']

            if mag is not None:
                mags.append(mag)
                lons.append(coords[0])
                lats.append(coords[1])

        except (KeyError, IndexError, TypeError):
            continue

    print(f"Processed {len(mags)} valid earthquakes")
    return mags, lats, lons, config