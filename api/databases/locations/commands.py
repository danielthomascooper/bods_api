CREATE_TABLE_COMMANDS = {"vehicles": """DROP TABLE IF EXISTS vehicles;
                                        
                                        CREATE TABLE vehicles (
                                        vehicle_id TEXT PRIMARY KEY,
                                        trip_id TEXT,
                                        position_lat REAL,
                                        position_lon REAL,
                                        bearing INTEGER,
                                        current_stop_sequence INTEGER,
                                        current_status TEXT,
                                        timestamp INTEGER NOT NULL,
                                        FOREIGN KEY(trip_id) REFERENCES live_trips(trip_id));""",
                         "live_trips": """DROP TABLE IF EXISTS live_trips;
                         
                                          CREATE TABLE live_trips (
                                          trip_id TEXT PRIMARY KEY,
                                          start_time TEXT,
						                  start_date TEXT,
						                  schedule_relationship TEXT,
						                  route_id TEXT);"""}


UPDATE_VEHICLES_COMMAND = """REPLACE INTO vehicles (vehicle_id, trip_id, position_lat, position_lon, bearing, current_stop_sequence, current_status, timestamp)
               SELECT
                 vehicle_id
                 , COALESCE(:trip_id, trip_id) as trip_id
                 , COALESCE(:position_lat, position_lat) as position_lat
                 , COALESCE(:position_lon, position_lon) as position_lon
                 , COALESCE(:bearing, bearing) as bearing
                 , COALESCE(:current_stop_sequence, current_stop_sequence) as current_stop_sequence
                 , COALESCE(:current_status, current_status) as current_status
                 , COALESCE(:timestamp, timestamp) as timestamp
                FROM
                  vehicles
                WHERE
                  vehicle_id = :vehicle_id
               UNION ALL
               SELECT
                 T.vehicle_id, T.trip_id, T.position_lat, T.position_lon, T.bearing, T.current_stop_sequence, T.current_status, T.timestamp
               FROM
               (
               SELECT
                 :vehicle_id as vehicle_id,
                 :trip_id as trip_id,
                 :position_lat as position_lat,
                 :position_lon as position_lon,
                 :bearing as bearing,
                 :current_stop_sequence as current_stop_sequence,
                 :current_status as current_status,
                 :timestamp as timestamp
               ) AS T
               WHERE
                 NOT EXISTS (SELECT * FROM vehicles AS V WHERE V.vehicle_id = T.vehicle_id)"""

UPDATE_TRIPS_COMMAND = """REPLACE INTO live_trips (trip_id, start_time, start_date, schedule_relationship, route_id) 
               SELECT
                 trip_id
                 , COALESCE(:start_time, start_time) as start_time
                 , COALESCE(:start_date, start_date) as start_date
                 , COALESCE(:schedule_relationship, schedule_relationship) as schedule_relationship
                 , COALESCE(:route_id, route_id) as route_id
                FROM
                  live_trips
                WHERE
                  trip_id = :trip_id
               UNION ALL
               SELECT
                 T.trip_id, T.start_time, T.start_date, T.schedule_relationship, T.route_id
               FROM
               (
               SELECT
                 :trip_id as trip_id,
                 :start_time as start_time,
                 :start_date as start_date,
                 :schedule_relationship as schedule_relationship,
                 :route_id as route_id
               ) AS T
               WHERE
                 NOT EXISTS (SELECT * FROM live_trips AS L WHERE L.trip_id = T.trip_id)"""
