#!/usr/bin/env python3
"""Visualize BODS API location data on an interactive map."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.bods_api import BODS_request

import plotly.express as px

# Load API key: prefer ../../../SECRET.txt, fall back to environment variable BODS_API_KEY
secret_path = Path(__file__).parent.parent.parent / "SECRET.txt"
if secret_path.exists():
    with open(secret_path, "r") as api_reader:
        API_KEY = api_reader.readline().strip()
else:
    API_KEY = os.environ.get("BODS_API_KEY")
    if not API_KEY:
        raise FileNotFoundError(
            "SECRET.txt not found and environment variable BODS_API_KEY is not set.\n"
            "Create SECRET.txt in project root or export BODS_API_KEY to proceed."
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

fig.show()
