import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.bods_api import BODS_request

import plotly.express as px

# Load API key: prefer ../SECRET.txt, fall back to environment variable BODS_API_KEY
secret_path = os.path.join(os.path.dirname(__file__), "..", "SECRET.txt")
if os.path.exists(secret_path):
    with open(secret_path, "r") as api_reader:
        API_KEY = api_reader.readline().strip()
else:
    API_KEY = os.environ.get("BODS_API_KEY")
    if not API_KEY:
        raise FileNotFoundError(
            "SECRET.txt not found and environment variable BODS_API_KEY is not set.\n"
            "Create ../SECRET.txt or export BODS_API_KEY to proceed."
        )

search_params = {"lineRef": "X4",
                 "operatorRef": "FBRI"}


my_data = BODS_request(API_KEY, "location", **search_params)
my_df = my_data.to_df()

fig = px.scatter_mapbox(my_df,
                        lat='MonitoredVehicleJourney_VehicleLocation_Latitude',
                        lon='MonitoredVehicleJourney_VehicleLocation_Longitude',
                        text='MonitoredVehicleJourney_PublishedLineName',
                        hover_name='MonitoredVehicleJourney_DestinationName',
                        color='MonitoredVehicleJourney_DestinationName',
                        mapbox_style="carto-positron"
                        )

# Calculate center and zoom
center_lat = my_df['MonitoredVehicleJourney_VehicleLocation_Latitude'].mean()
center_lon = my_df['MonitoredVehicleJourney_VehicleLocation_Longitude'].mean()

fig.update_layout(
    mapbox=dict(
        center=dict(lat=center_lat, lon=center_lon),
        zoom=11
    ),
    width=1200,
    height=800
)


output_dir = os.path.dirname(__file__)
html_path = os.path.join(output_dir, "map_plot.html")
png_path = os.path.join(output_dir, "map_plot.png")
fig.write_html(html_path, include_plotlyjs='cdn')
print(f"Saved {html_path}")
try:
    fig.write_image(png_path, scale=2)
    print(f"Saved {png_path}")
except Exception as e:
    print("Could not save PNG (kaleido may be missing):", e)