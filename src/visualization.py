import os
from plotly.graph_objs import Scattergeo, Layout
from plotly import offline
from src.data_processing import process_data


def create_map():
    mags, lats, lons, config = process_data()

    if not mags:
        print("No earthquake data to visualize")
        return

    os.makedirs('output', exist_ok=True)

    min_mag = min(mags)
    if min_mag < 0:
        sizes = [(mag - min_mag + 0.5) * 3 for mag in mags]
    else:
        sizes = [mag * 3 for mag in mags]

    data = [Scattergeo(
        lon=lons,
        lat=lats,
        mode='markers',
        marker=dict(
            size=sizes,
            color=mags,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Magnitude"),
            sizemin=2
        ),
        text=[f'Magnitude: {mag}' for mag in mags],
        hovertemplate='<b>Magnitude:</b> %{text}<br>' +
                      '<b>Latitude:</b> %{lat}<br>' +
                      '<b>Longitude:</b> %{lon}<extra></extra>'
    )]

    viz_config = config.get("visualization", {})
    title = viz_config.get("title", "Global Earthquakes")

    layout = Layout(
        title=title,
        geo=dict(
            projection_type='equirectangular',
            showland=True,
            landcolor='lightgray',
            showocean=True,
            oceancolor='lightblue'
        )
    )

    fig = {'data': data, 'layout': layout}
    offline.plot(fig, filename='output/earthquake_map.html')
    print("Map saved to output/earthquake_map.html")