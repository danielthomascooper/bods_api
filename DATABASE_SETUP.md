# Database Setup Complete ✅

## What Was Created

You now have a **fully functional GTFS database** for testing and development:

```
📄 Database Location
   /home/habrt/source/bods_api/api/databases/gfts/sql/test_sample.db  (96 KB)

📝 Sample Data
   - 1 Transit Agency (Reading Buses)
   - 2 Routes (Route 1, Route 2)
   - 4 Stops (Town Centre, Hospital, Station, Park)
   - 4 Trips (T1-T4) with schedules
   - 10 Stop Times
   - Service calendars (weekday/weekend)

🗂️ All GTFS Tables
   ✓ agency, routes, stops, trips
   ✓ calendar, calendar_dates
   ✓ stop_times, feed_info
   ✓ shapes, frequencies
```

## Scripts Created

### 1. **setup_test_database.py** — Create the database
```bash
python setup_test_database.py
```
- Generates sample GTFS CSV files
- Converts them to SQLite
- Creates `/api/databases/gfts/sql/test_sample.db`

### 2. **test_database_queries.py** — Test queries
```bash
python test_database_queries.py
```
- Shows agencies, routes, stops
- Demonstrates trip lookups
- Tests parameterized queries (the safe SQL injection prevention)

### 3. **test_timetable_module.py** — Test the timetable module
```bash
python test_timetable_module.py
```
- Uses the fixed `api/timetable/timetable.py` module
- Verifies parameterized queries prevent SQL injection
- Demonstrates real-world usage

## Next Steps

### Option A: Use Test Database (Development/Demo)
The test database is perfect for:
- ✅ Testing your API code
- ✅ Verifying parameterized queries work
- ✅ Developing features without 25GB downloads
- ✅ Unit testing and CI/CD

**To point your code to this database:**
```python
# In your code:
db_path = "api/databases/gfts/sql/test_sample.db"
```

### Option B: Use Real GTFS Data (Production)
To download ~25GB of real UK bus timetable data:

```bash
python download_gtfs_data.py
```

This script will:
1. Prompt for confirmation (download is ~25 GB, takes 2-3 hours)
2. Download official GTFS Schedule data from BODS
3. Convert to SQLite
4. Create `/api/databases/gfts/sql/blue.db` and `green.db`

Alternatively, use the command directly (no confirmation):
```bash
python -c "import sys; sys.path.insert(0, '.'); from api.databases.caching import update_databases; print(update_databases())"
```

## Database Manager

Use [api/databases/manager.py](api/databases/manager.py) for blue/green switching:

```python
from api.databases.manager import DatabaseManager

manager = DatabaseManager(
    blue_database="api/databases/gfts/sql/blue.db",
    green_database="api/databases/gfts/sql/green.db",
    current_db_cache="api/databases/gfts/sql/current_database.txt"
)

# Get current database path
db_path = manager.get_current_database_path()

# Update inactive database (zero-downtime deployment)
manager.update_inactive_database()
manager.swap_database_path()
```

## Run the API Server

```bash
# Set your BODS API key
export BODS_API_KEY=your_api_key_here

# Start Flask server (uses test database by default for demo)
python flask_server.py
```

Then query it:
```bash
curl http://127.0.0.1:5000/locations?lineRef=17&operatorRef=RBUS
```

## Security ✅

All security fixes from the audit are in place:
- ✅ SQL injection prevention via parameterized queries
- ✅ Environment-based config (no hardcoded secrets)
- ✅ Thread-safe stop data loading
- ✅ Proper error handling and logging
- ✅ HTTPS-ready configuration

See **AUDIT_REPORT.md** for full details.
