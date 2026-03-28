import os
import sqlite3
import folium
from datetime import datetime
from time import perf_counter
import logging

logger = logging.getLogger(__name__)

COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
          'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']


def get_database_path(db_cache_path: str | os.PathLike = "") -> str:
    if not db_cache_path:
        db_cache_path = os.path.join(os.path.dirname(__file__), "../databases/gfts/sql/current_database.txt")

    with open(db_cache_path, "r") as f:
        db_path = str(f.read())

    return db_path


def get_services_from_stop(db_path, stop_code: str):
    date_string = datetime.today().strftime("%Y%m%d")
    weekday_index = datetime.today().weekday()
    weekday = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")[weekday_index]

    # Validate weekday is a known column name to prevent injection via the column reference
    valid_weekdays = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    if weekday not in valid_weekdays:
        raise ValueError(f"Invalid weekday: {weekday}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT trips.trip_id, trips.shape_id FROM trips "
        f"JOIN calendar USING(service_id) "
        f"JOIN calendar_dates USING(service_id) "
        f"JOIN stop_times USING(trip_id) "
        f"WHERE stop_times.stop_id = ? "
        f"AND ((calendar.start_date < ? AND calendar.end_date > ? AND calendar.{weekday} = 1) "
        f"OR (calendar_dates.exception_type = 1 AND calendar_dates.date = ?))",
        (stop_code, date_string, date_string, date_string)
    )

    return cursor.fetchall()


if __name__ == "__main__":
    trip_ids, shape_ids = zip(*get_services_from_stop(get_database_path(), "0100BRZ00692"))
    trip_ids = list(set(trip_ids))

    with open("../databases/gfts/sql/current_database.txt", "r") as f:
        current_db_path = str(f.read())

    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()
    paths = []
    for shape_id, trip_id in zip(shape_ids, trip_ids):
        if shape_id:
            cursor.execute(
                "SELECT shapes.shape_pt_lat, shapes.shape_pt_lon "
                "FROM trips "
                "JOIN shapes USING(shape_id) "
                "WHERE trips.trip_id = ?",
                (trip_id,)
            )
        else:
            cursor.execute(
                "SELECT stops.stop_lat, stops.stop_lon "
                "FROM stop_times "
                "JOIN stops USING(stop_id) "
                "WHERE stop_times.trip_id = ? "
                "ORDER BY stop_times.stop_sequence",
                (trip_id,)
            )
        paths.append(cursor.fetchall())

    bus_map = folium.Map(location=(51.405394, -0.851258), zoom_start=10)
    for i, path in enumerate(paths):
        if not path:
            logger.warning("No shape data for trip %d", i)
        else:
            folium.PolyLine(locations=path, color=COLORS[i%len(COLORS)]).add_to(bus_map)
    bus_map.show_in_browser()
