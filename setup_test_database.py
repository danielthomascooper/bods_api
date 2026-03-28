#!/usr/bin/env python3
"""
Test database setup script.

Creates sample GTFS CSV files and converts them to SQLite for testing.
This allows you to test the database functionality without downloading 25GB of real data.
"""

import os
import csv
import logging
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from api.databases.gtfs_conversion import gtfs_files_to_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create sample data directory
SAMPLE_DATA_DIR = Path(__file__).parent / "api" / "databases" / "gfts" / "raw"
DB_DIR = Path(__file__).parent / "api" / "databases" / "gfts" / "sql"

SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_gtfs() -> None:
    """Create sample GTFS CSV files for testing."""
    logger.info("Creating sample GTFS data in %s", SAMPLE_DATA_DIR)

    # Agency
    with open(SAMPLE_DATA_DIR / "agency.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "agency_id", "agency_name", "agency_url", "agency_timezone", 
            "agency_lang", "agency_phone", "agency_noc"
        ])
        writer.writeheader()
        writer.writerow({
            "agency_id": "RBUS",
            "agency_name": "Reading Buses",
            "agency_url": "https://www.reading-buses.co.uk",
            "agency_timezone": "Europe/London",
            "agency_lang": "en",
            "agency_phone": "0118 959 4000",
            "agency_noc": "RBUS"
        })
        logger.info("Created agency.csv with 1 agency")

    # Calendar
    with open(SAMPLE_DATA_DIR / "calendar.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "service_id", "monday", "tuesday", "wednesday", "thursday", 
            "friday", "saturday", "sunday", "start_date", "end_date"
        ])
        writer.writeheader()
        writer.writerow({
            "service_id": "WD",
            "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1,
            "friday": 1, "saturday": 0, "sunday": 0,
            "start_date": "20260101",
            "end_date": "20261231"
        })
        writer.writerow({
            "service_id": "WE",
            "monday": 0, "tuesday": 0, "wednesday": 0, "thursday": 0,
            "friday": 0, "saturday": 1, "sunday": 1,
            "start_date": "20260101",
            "end_date": "20261231"
        })
        logger.info("Created calendar.csv with 2 service calendars")

    # Calendar Dates
    with open(SAMPLE_DATA_DIR / "calendar_dates.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["service_id", "date", "exception_type"])
        writer.writeheader()
        # No exceptions for this test
        logger.info("Created calendar_dates.csv (empty)")

    # Routes
    with open(SAMPLE_DATA_DIR / "routes.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "route_id", "agency_id", "route_short_name", 
            "route_long_name", "route_type"
        ])
        writer.writeheader()
        writer.writerow({
            "route_id": "R1",
            "agency_id": "RBUS",
            "route_short_name": "1",
            "route_long_name": "Town Centre - Hospital",
            "route_type": 3  # Bus
        })
        writer.writerow({
            "route_id": "R2",
            "agency_id": "RBUS",
            "route_short_name": "2",
            "route_long_name": "Station - Park",
            "route_type": 3
        })
        logger.info("Created routes.csv with 2 routes")

    # Stops
    with open(SAMPLE_DATA_DIR / "stops.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stop_id", "stop_code", "stop_name", "stop_lat", "stop_lon",
            "wheelchair_boarding", "location_type", "parent_station", "platform_code"
        ])
        writer.writeheader()
        stops = [
            ("S1", "0100RDG00001", "Town Centre Bus Station", 51.4545, -0.9781, 1, None, None, None),
            ("S2", "0100RDG00002", "Hospital Entrance", 51.4560, -0.9750, 1, None, None, None),
            ("S3", "0100RDG00003", "Reading Station", 51.3333, -0.9667, 1, None, None, None),
            ("S4", "0100RDG00004", "Central Park", 51.4500, -0.9800, 1, None, None, None),
        ]
        for stop in stops:
            writer.writerow(dict(zip([
                "stop_id", "stop_code", "stop_name", "stop_lat", "stop_lon",
                "wheelchair_boarding", "location_type", "parent_station", "platform_code"
            ], stop)))
        logger.info("Created stops.csv with %d stops", len(stops))

    # Trips
    with open(SAMPLE_DATA_DIR / "trips.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "route_id", "service_id", "trip_id", "trip_headsign",
            "block_id", "shape_id", "wheelchair_accessible",
            "trip_direction_name", "vehicle_journey_code"
        ])
        writer.writeheader()
        trips = [
            ("R1", "WD", "T1", "Hospital", None, None, 1, None, "VJ001"),
            ("R1", "WD", "T2", "Town Centre", None, None, 1, None, "VJ002"),
            ("R2", "WE", "T3", "Park", None, None, 1, None, "VJ003"),
            ("R2", "WE", "T4", "Station", None, None, 1, None, "VJ004"),
        ]
        for trip in trips:
            writer.writerow(dict(zip([
                "route_id", "service_id", "trip_id", "trip_headsign",
                "block_id", "shape_id", "wheelchair_accessible",
                "trip_direction_name", "vehicle_journey_code"
            ], trip)))
        logger.info("Created trips.csv with %d trips", len(trips))

    # Stop Times
    with open(SAMPLE_DATA_DIR / "stop_times.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence",
            "stop_headsign", "pickup_type", "drop_off_type", "shape_dist_traveled",
            "timepoint", "stop_direction_name"
        ])
        writer.writeheader()
        stop_times = [
            ("T1", "08:00:00", "08:00:00", "S1", 1, None, 0, 0, 0, 1, None),
            ("T1", "08:15:00", "08:15:00", "S4", 2, None, 0, 0, None, 1, None),
            ("T1", "08:30:00", "08:30:00", "S2", 3, None, 0, 0, None, 1, None),
            ("T2", "09:00:00", "09:00:00", "S2", 1, None, 0, 0, 0, 1, None),
            ("T2", "09:15:00", "09:15:00", "S4", 2, None, 0, 0, None, 1, None),
            ("T2", "09:30:00", "09:30:00", "S1", 3, None, 0, 0, None, 1, None),
            ("T3", "10:00:00", "10:00:00", "S3", 1, None, 0, 0, 0, 1, None),
            ("T3", "10:20:00", "10:20:00", "S4", 2, None, 0, 0, None, 1, None),
            ("T4", "11:00:00", "11:00:00", "S4", 1, None, 0, 0, 0, 1, None),
            ("T4", "11:20:00", "11:20:00", "S3", 2, None, 0, 0, None, 1, None),
        ]
        for st in stop_times:
            writer.writerow(dict(zip([
                "trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence",
                "stop_headsign", "pickup_type", "drop_off_type", "shape_dist_traveled",
                "timepoint", "stop_direction_name"
            ], st)))
        logger.info("Created stop_times.csv with %d entries", len(stop_times))

    # Shapes (optional)
    with open(SAMPLE_DATA_DIR / "shapes.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence", "shape_dist_traveled"
        ])
        writer.writeheader()
        # Empty for this test
        logger.info("Created shapes.csv (empty)")

    # Feed Info
    with open(SAMPLE_DATA_DIR / "feed_info.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "feed_publisher_name", "feed_publisher_url", "feed_lang",
            "feed_start_date", "feed_end_date", "feed_version"
        ])
        writer.writeheader()
        writer.writerow({
            "feed_publisher_name": "Reading Buses",
            "feed_publisher_url": "https://www.reading-buses.co.uk",
            "feed_lang": "en",
            "feed_start_date": "20260101",
            "feed_end_date": "20261231",
            "feed_version": "1.0.0"
        })
        logger.info("Created feed_info.csv")

    # Frequencies & other files (required by schema but can be empty)
    for filename in ["frequencies.csv"]:
        csv_path = SAMPLE_DATA_DIR / filename
        if filename == "frequencies.csv":
            fieldnames = ["trip_id", "start_time", "end_time", "headway_secs", "exact_times"]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        logger.info("Created %s (empty)", filename)


def build_test_database() -> str:
    """Build the test database from sample GTFS data."""
    db_path = DB_DIR / "test_sample.db"
    logger.info("Building test database at %s", db_path)
    
    # Remove old database if it exists
    if db_path.exists():
        os.remove(db_path)
    
    # Convert GTFS CSVs to SQLite
    try:
        gtfs_files_to_db(db_path, SAMPLE_DATA_DIR)
        logger.info("✓ Database created successfully at %s", db_path)
        return str(db_path)
    except Exception as e:
        logger.error("✗ Failed to create database: %s", e)
        raise


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("GTFS Test Database Setup")
    logger.info("=" * 60)
    
    create_sample_gtfs()
    db_path = build_test_database()
    
    logger.info("=" * 60)
    logger.info("✓ Setup complete!")
    logger.info("Database: %s", db_path)
    logger.info("=" * 60)
