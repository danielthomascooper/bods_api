# BODS API — Python Wrapper for the Bus Open Data Service

A Python API wrapper for the UK [Bus Open Data Service (BODS)](https://data.bus-data.dft.gov.uk/),
providing access to live bus locations, timetable schedules, and fares data.

## Features

- **Live bus locations** via the BODS Vehicle Monitoring API, returned as JSON.
- **Timetable database** built from GTFS Schedule data, stored in SQLite for fast local queries.
- **Caching layer** with TTL-based LRU cache to minimise redundant upstream requests.
- **Blue/green database switching** for zero-downtime GTFS database updates.
- **Flask server** exposing a `/locations` REST endpoint.

## Prerequisites

- Python 3.12+
- ~25 GB disk space for GTFS database files
- A BODS API key — register at <https://data.bus-data.dft.gov.uk/> and find your key in Account Settings

## Quick Start

```bash
# Clone and set up a virtual environment
git clone <repo-url> && cd bods_api
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt

# Configure your API key (choose one):
#   Option A — environment variable (recommended)
export BODS_API_KEY=your_api_key_here

#   Option B — SECRET.txt file (git-ignored)
echo "your_api_key_here" > SECRET.txt

# Run the Flask server
python flask_server.py
```

The server starts on `http://127.0.0.1:5000` by default.

## Configuration

All configuration is via environment variables (see [.env.example](.env.example)):

| Variable | Default | Description |
| --- | --- | --- |
| `BODS_API_KEY` | — | **Required.** Your BODS API key. |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (`true`/`false`). |
| `FLASK_HOST` | `127.0.0.1` | Host to bind the Flask server to. |
| `FLASK_PORT` | `5000` | Port for the Flask server. |
| `ALLOWED_ORIGINS` | `*` | CORS `Access-Control-Allow-Origin` header value. |
| `CACHE_TIMEOUT` | `15` | Cache TTL in seconds. |
| `CACHE_MAX_SIZE` | `256` | Maximum number of cached responses. |

## API Usage

### `/locations` endpoint

Query parameters are passed through to the BODS Vehicle Monitoring API:

```http
GET /locations?lineRef=X4&operatorRef=FBRI
```

Supported parameters: `boundingBox`, `operatorRef`, `lineRef`, `producerRef`,
`originRef`, `destinationRef`, `vehicleRef`.

### Python API

```python
from api.bods_api import BODS_request

response = BODS_request(api_key, "location", lineRef="X4", operatorRef="FBRI")
df = response.to_df()     # pandas DataFrame
json_str = response.to_json()  # JSON string
```

## Project Structure

```text
flask_server.py              # Flask application entry point
api/
  bods_api.py                # Core BODS API request logic
  xml_methods.py             # XML/etree utility functions
  location/
    responses.py             # LocationResponse class (XML → dict/df/json)
  timetable/
    timetable.py             # GTFS timetable queries (SQLite)
  databases/
    caching.py               # Database update scheduler & downloader
    gtfs_conversion.py       # GTFS ZIP → SQLite converter
    manager.py               # Blue/green database manager
    gfts/commands.py          # SQL CREATE TABLE definitions
protobuf/                    # GTFS Realtime protobuf definitions
testing/                     # Development/demo scripts (not production)
```

## Data Sources

- **BODS API** — <https://data.bus-data.dft.gov.uk/>
- **NaPTAN** (stop data) — <https://naptan.api.dft.gov.uk/>
- **GTFS Schedule** — <https://gtfs.org/>

## License

This project is not currently licensed. Contact the author for usage terms.
