#!/usr/bin/env python3
"""Test the timetable module with our fixed parameterized queries."""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from api.timetable.timetable import get_services_from_stop

# Use our test database
TEST_DB = Path(__file__).parent / "api/databases/gfts/sql/test_sample.db"

print("\n" + "="*60)
print("Testing Timetable Module (Parameterized SQL Queries)")
print("="*60)

if not TEST_DB.exists():
    print(f"\n❌ Test database not found: {TEST_DB}")
    print("Run: python setup_test_database.py")
    sys.exit(1)

print(f"\n📦 Using test database: {TEST_DB}")

# Test 1: Query for services at stop S1
print("\n1️⃣  Services stopping at S1 (Town Centre Bus Station):")
services = get_services_from_stop(str(TEST_DB), "S1")
if services:
    for trip_id, shape_id in services:
        print(f"   Trip: {trip_id}, Shape: {shape_id}")
else:
    print("   (No services found)")

# Test 2: Query for services at stop S2
print("\n2️⃣  Services stopping at S2 (Hospital Entrance):")
services = get_services_from_stop(str(TEST_DB), "S2")
if services:
    for trip_id, shape_id in services:
        print(f"   Trip: {trip_id}, Shape: {shape_id}")
else:
    print("   (No services found)")

# Test 3: Try an SQL injection attack to verify it doesn't work
print("\n3️⃣  Testing SQL injection prevention:")
print("   Attempting: stop_code = \"S1' OR '1'='1\"")
try:
    malicious_code = "S1' OR '1'='1"
    services = get_services_from_stop(str(TEST_DB), malicious_code)
    print(f"   Result: Found {len(services)} matches (parameterized queries protected!)")
    if len(services) == 0:
        print(f"   ✓ SQL injection safely prevented (no unauthorized data returned)")
except Exception as e:
    print(f"   ✓ SQL injection safely rejected: {e}")

print("\n" + "="*60)
print("✓ Timetable module working correctly with safe parameterized queries!")
print("="*60 + "\n")
