import os
import sqlite3
import folium
import os
from time import sleep, perf_counter

def get_database_path(db_cache_path: str|os.PathLike = "") -> str:
    if not db_cache_path:
        db_cache_path = os.path.join(os.path.dirname(__file__), "../databases/gfts/sql/current_database.txt")

    with open(db_cache_path, "r") as f:
        db_path = str(f.read())

    return db_path


if __name__ == "__main__":
    with open("../databases/gfts/sql/current_database.txt", "r") as f:
        current_db_path = str(f.read())

    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT shapes.shape_pt_lat, "
                   "shapes.shape_pt_lon "
                   "FROM trips "
                   "JOIN shapes USING(shape_id) "
                   "WHERE trips.trip_id = 'VJ93a759c7907d9a3b592fd09998f1ab4425ec181f'")
    locations = cursor.fetchall()

    bus_map = folium.Map(location=(51.453611, -2.5975), zoom_start=12)
    folium.PolyLine(locations=locations).add_to(bus_map)
    bus_map.show_in_browser()

