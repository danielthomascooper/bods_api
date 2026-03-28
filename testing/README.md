# Testing Directory

This directory contains all testing scripts, utilities, and analysis tools for the BODS API project.

## Structure

```
testing/
├── database/               # Database testing and setup
│   ├── setup_test_database.py    # Create sample GTFS data and test database
│   ├── test_database_queries.py  # Test raw SQL queries
│   └── test_timetable_module.py  # Test timetable module functionality
│
├── api/                    # API testing and visualization
│   └── test_bods_api_visualization.py  # Visualize bus locations on interactive map
│
├── analysis/              # Data analysis and exploration scripts
│   └── analyze_disappearing_buses.py   # Analyze bus count patterns
│
├── utilities/             # Helper utilities
│   └── csv_methods.py     # CSV file manipulation tools
│
└── visualization/         # Visualization scripts
    └── map_visualization.py       # Generate map visualizations
```

## Usage

### Running Database Tests

```bash
# Setup test database with sample GTFS data
python -m testing.database.setup_test_database

# Test database queries
python -m testing.database.test_database_queries

# Test timetable module
python -m testing.database.test_timetable_module
```

### Running API Tests

```bash
# Visualize bus locations on a map
python -m testing.api.test_bods_api_visualization
```

### Running Analysis

```bash
# Analyze disappearing buses pattern
python -m testing.analysis.analyze_disappearing_buses
```

### Using Utilities

```python
from testing.utilities.csv_methods import csv_editor

with csv_editor('path/to/file.csv') as editor:
    # Edit the CSV file
    pass
```

## Notes

- All modules require the `SECRET.txt` file at the project root with your BODS API key
- Database tests use a sample database at `api/databases/gfts/sql/test_sample.db`
- All visualization code requires matplotlib and related libraries
