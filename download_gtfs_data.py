#!/usr/bin/env python3
"""Download real GTFS data from BODS.

This script handles downloading the full, official UK bus timetable data from the
Bus Open Data Service (BODS). This is ~25 GB and takes 2-3 hours depending on
internet speed.

Usage:
    python download_gtfs_data.py
"""

import os
import sys
import logging
from pathlib import Path

# Ensure we're in the correct directory for imports and path resolution
REPO_ROOT = Path(__file__).parent.absolute()
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from api.databases.caching import update_databases

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Download GTFS data."""
    print("\n" + "="*70)
    print("GTFS DOWNLOAD - Real UK Bus Timetable Data")
    print("="*70)
    print("\n⚠️  WARNING: This will download ~25 GB of data")
    print("   Estimated time: 2-3 hours")
    print("   Location: api/databases/gfts/sql/blue.db & green.db\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ("yes", "y"):
        print("Cancelled.")
        return
    
    print("\n📥 Starting download...\n")
    
    try:
        updated_keys = update_databases()
        print("\n" + "="*70)
        print("✅ Download complete!")
        print(f"   Updated: {', '.join(updated_keys) if updated_keys else 'all databases'}")
        print("="*70 + "\n")
    except Exception as e:
        logger.error("Download failed: %s", e)
        print("\n" + "="*70)
        print("❌ Download failed!")
        print(f"   Error: {e}")
        print("="*70 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
