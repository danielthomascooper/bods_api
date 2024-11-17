# Python wrapper for BODS API
An API written in Python that uses the Bus Open Data Service (BODS) to get live bus location and other data such as 
timetables and fares. 

Uses SQLite3 to store cached locations for buses and the timetable data. This uses the [GFTS](https://gtfs.org/) data
format, both GFTS Schedule (.txt files) and GFTS Realtime (protobuf files).

This has the advantage over the BODS API that it caches the bus locations as the Realtime feed only provides deltas not 
a full list of all buses meeting certain parameters. It also integrates the Schedule data into one SQL database to allow
for easier access to schedules.

## Requirements
The following requirements are based on the versions used for development, and likely will work with higher versions:
```
Flask==3.1.0
folium==0.18.0
lxml==5.3.0
matplotlib==3.9.2
numpy==2.1.3
pandas==2.2.3
plotly==5.24.1
protobuf==5.28.3
Requests==2.32.3
xmltodict==0.14.2
```

The protobuf files are compiled from the proto file provided at https://gtfs.org/documentation/realtime/proto/.

The database files are large and require ~25GB of disk space.

## Usage
'flask_server.py' provides an example of how the API can be used. The main function to be used is bods_api.BODS_request 
which takes in the same arguments as the BODS API which are passed to the call to be used. In development is the
schedule database which is to be integrated to the same function.

The databases can be used directly until the API is finished.