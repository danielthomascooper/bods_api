import sqlite3
import os
from api.databases.locations.commands import *
import requests
import protobuf.gtfs_realtime_pb2 as gtfs_rt
import zipfile
import io
from time import perf_counter
from pathlib import Path


class LocationManager:
    def __init__(self, db_path: str|os.PathLike = os.path.join(os.path.dirname(__file__), 'bus_locations.db')):
        self.db_path = db_path
        self.create_db()

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        for table in CREATE_TABLE_COMMANDS:
            conn.executescript(CREATE_TABLE_COMMANDS[table])
            conn.commit()
        conn.close()

    def add_protobuf(self, msg: gtfs_rt.FeedMessage):
        vehicle_data = []
        trip_data = []
        for e in msg.entity:
            v = e.vehicle
            vehicle_data.append({"vehicle_id": v.vehicle.id,
                                 "trip_id": v.trip.trip_id if v.trip.trip_id else None,
                                 "position_lat": v.position.latitude if v.position.latitude else None,
                                 "position_lon": v.position.longitude if v.position.longitude else None,
                                 "bearing": v.position.bearing if v.position.bearing else None,
                                 "current_stop_sequence": v.current_stop_sequence if v.current_stop_sequence else None,
                                 "current_status": v.current_status if v.current_status else None,
                                 "timestamp": v.timestamp if v.timestamp else None})
            t = v.trip
            trip_data.append({"trip_id": t.trip_id,
                              "start_time": t.start_time if t.start_time else None,
                              "start_date": t.start_date if t.start_date else None,
                              "schedule_relationship": t.schedule_relationship if t.schedule_relationship else None,
                              "route_id": t.route_id if t.route_id else None})

        conn = sqlite3.connect(self.db_path)
        conn.executemany(UPDATE_VEHICLES_COMMAND, vehicle_data)
        conn.executemany(UPDATE_TRIPS_COMMAND, trip_data)
        conn.commit()
        conn.close()

    def add_protobuf_from_url(self, url: str, zipped=True) -> None:
        r = requests.get(url)
        new_msg = gtfs_rt.FeedMessage()

        if zipped:
            compressed_data = r.content
            z = zipfile.ZipFile(io.BytesIO(compressed_data))
            new_msg.ParseFromString(z.read("gtfsrt.bin"))
        else:
            try:
                new_msg.ParseFromString(r.content)
            except Exception as e:
                print(r.headers)
                print(r.content)
                raise e

        self.add_protobuf(new_msg)

def get_buses_details(bus_db: str|os.PathLike = os.path.join(os.path.dirname(__file__), 'bus_locations.db'),
              timetable_cache: str|os.PathLike = Path(__file__).parent.parent/'gfts'/'sql'/'current_database.txt',
              **kwargs):
    with open(Path(timetable_cache).absolute(), 'r') as f:
        timetable_path = str(f.read()).strip()

    conditions = []
    params = []

    start_of_command = """SELECT 
                             v.position_lat,
                             v.position_lon,
                             v.bearing,
                             v.current_stop_sequence,
                             v.current_status,
                             v.timestamp,
                             lt.trip_id,
                             lt.start_time,
                             lt.start_date,
                             lt.schedule_relationship,
                             lt.route_id,
                             a.agency_name,
                             a.agency_noc,
                             r.route_short_name
                           FROM
                             main.vehicles v
                           LEFT JOIN main.live_trips lt ON lt.trip_id = v.trip_id 
                           LEFT JOIN timetable.routes r ON lt.route_id = r.route_id 
                           LEFT JOIN timetable.agency a ON r.agency_id = a.agency_id 
                           """

    for arg in kwargs:
        if arg == 'bounding_box':
            lon1, lat1, lon2, lat2 = kwargs[arg]
            conditions.append("v.position_lat >= ? AND v.position_lat <= ? AND "
                              "v.position_lon >= ? AND v.position_lon <= ?")
            params.extend([min(lat1, lat2), max(lat1, lat2), min(lon1, lon2), max(lon1, lon2)])
        elif arg == 'routeId':
            conditions.append("lt.route_id = ?")
            params.append(kwargs[arg])
        elif arg == 'startTimeAfter':
            conditions.append("v.timestamp >= ?")
            params.append(kwargs[arg])
        elif arg == 'startTimeBefore':
            conditions.append("v.timestamp <= ?")
            params.append(kwargs[arg])
        elif arg == 'operatorRef':
            conditions.append("a.agency_noc = ?")
            params.append(kwargs[arg])
        elif arg == 'vehicleRef':
            conditions.append("v.vehicle_id = ?")
            params.append(kwargs[arg])

    if conditions:
        command = start_of_command + "WHERE " + " AND ".join(conditions)
    else:
        command = start_of_command
    conn = sqlite3.connect(bus_db)
    cursor = conn.cursor()
    cursor.execute("ATTACH ? AS 'timetable'", (timetable_path,))
    selected_cursor = cursor.execute(command, params)
    return_data = selected_cursor.fetchall()
    conn.close()
    return return_data


if __name__ == '__main__':
    # start_time = perf_counter()
    test_manager = LocationManager()
    # test_manager.create_db()
    test_manager.add_protobuf_from_url("https://data.bus-data.dft.gov.uk/avl/download/gtfsrt")
    # print(get_buses_details(bounding_box=(-0.7196044921875001,51.503406029464514,-1.1666107177734377,51.386786571080854)))
    print(get_buses_details())

    # print(perf_counter() - start_time)
