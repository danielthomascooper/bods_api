#!/usr/bin/env python3
"""Test database queries."""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "api" / "databases" / "gfts" / "sql" / "test_sample.db"


def test_queries():
    """Run test queries against the database."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Run: python setup_test_database.py")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("TEST DATABASE QUERIES")
    print("="*60 + "\n")

    # Test 1: Count all agencies
    print("1️⃣  Agencies:")
    cursor.execute("SELECT agency_id, agency_name FROM agency")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Test 2: Count routes
    print("\n2️⃣  Routes:")
    cursor.execute("SELECT route_id, route_short_name, route_long_name FROM routes")
    for row in cursor.fetchall():
        print(f"   {row[0]} ({row[1]}): {row[2]}")

    # Test 3: Count stops
    print("\n3️⃣  Stops:")
    cursor.execute("SELECT stop_code, stop_name, stop_lat, stop_lon FROM stops")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} @ ({row[2]}, {row[3]})")

    # Test 4: Complex query - trips for a specific route
    print("\n4️⃣  Trips on Route R1:")
    cursor.execute("""
        SELECT t.trip_id, t.trip_headsign, c.start_date, c.end_date
        FROM trips t
        JOIN calendar c USING(service_id)
        WHERE route_id = 'R1'
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} → {row[1]} ({row[2]} to {row[3]})")

    # Test 5: Stop times for a specific trip
    print("\n5️⃣  Stop Times for Trip T1:")
    cursor.execute("""
        SELECT st.arrival_time, s.stop_name, st.stop_sequence
        FROM stop_times st
        JOIN stops s USING(stop_id)
        WHERE trip_id = 'T1'
        ORDER BY stop_sequence
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} at {row[1]} (stop #{row[2]})")

    # Test 6: Parameterized query (like timetable.py uses)
    print("\n6️⃣  Services stopping at S1:")
    stop_code = "S1"
    cursor.execute("""
        SELECT DISTINCT t.trip_id, t.trip_headsign, r.route_short_name
        FROM stop_times st
        JOIN stops s USING(stop_id)
        JOIN trips t USING(trip_id)
        JOIN routes r USING(route_id)
        WHERE s.stop_id = ?
    """, (stop_code,))
    for row in cursor.fetchall():
        print(f"   Trip {row[0]} → {row[1]} on Route {row[2]}")

    conn.close()

    print("\n" + "="*60)
    print("✓ All queries executed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_queries()
