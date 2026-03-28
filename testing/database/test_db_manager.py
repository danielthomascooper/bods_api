from pathlib import Path
from api.databases.manager import DatabaseManager

# Get paths relative to project root
project_root = Path(__file__).parent.parent.parent
db_dir = project_root / "api" / "databases" / "gfts" / "sql"
db_dir.mkdir(parents=True, exist_ok=True)

print("Testing DatabaseManager initialization...")
manager = DatabaseManager(
    str(db_dir / "blue.db"),
    str(db_dir / "green.db"),
    str(db_dir / "current_database.txt")
)
print(f"✅ DatabaseManager initialized successfully")
print(f"   Current database: {manager.current_database}")
print(f"   Current path: {manager.get_current_database_path()}")
print(f"\nNote: To actually update the database with GTFS data, call:")
print(f"   manager.update_inactive_database()  # This downloads 1.6GB and takes time")