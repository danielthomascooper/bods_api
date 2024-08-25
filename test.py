from api.bods_api import BODS_request

import plotly.express as px

with open("SECRET.txt", "r") as api_reader:
    API_KEY = api_reader.readline().strip()

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
                        mapbox_style="open-street-map"
                        )
fig.show()