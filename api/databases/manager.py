import os
from api.databases.gtfs_conversion import create_database
from typing import Literal
import pathlib


def local_to_abs(local_path: str|os.PathLike):
    return os.path.join(pathlib.Path(__file__).parent.resolve(), local_path)

GTFS_ZIP = local_to_abs("itm_all_gtfs.zip")
RAW_DIR = local_to_abs("gfts/")

class DatabaseManager:
    def __init__(self, blue_database: str|os.PathLike,
                 green_database: str|os.PathLike,
                 current_db_cache: str|os.PathLike,
                 current_database: Literal["blue", "green", ""] = ""):
        """Manages the current database path.

        Parameters
        ----------
        blue_database : str or os.PathLike
            The path to the blue database file.
        green_database : str or os.PathLike
            The path to the green database file.
        current_db_cache : str or os.PathLike:
            The path to the file containing the current database path.
        current_database : str
            The current database.
        """
        self.blue_database = os.path.abspath(blue_database)
        self.green_database = os.path.abspath(green_database)
        self.current_db_cache = os.path.abspath(current_db_cache)

        if not current_database:
            if not os.path.isfile(self.current_db_cache):
                pathlib.Path(self.current_db_cache).touch()
            with open(current_db_cache, "r") as cache_file:
                cached_db_path = cache_file.read()
                if os.path.normpath(cached_db_path) == os.path.normpath(self.blue_database):
                    self.current_database = "blue"
                elif os.path.normpath(cached_db_path) == os.path.normpath(self.green_database):
                    self.current_database = "green"
                else:
                    raise ValueError(f"Cached path '{cached_db_path}' does not match blue ({self.blue_database})"
                                     f" or green ({self.green_database}) database provided.")
        else:
            self.current_database = current_database

        if self.current_database not in ("blue", "green"):
            raise ValueError(f"Invalid current database '{current_database}'")

        self.set_cached_path()

    def set_cached_path(self):
        with open(self.current_db_cache, "w") as cache_file:
            if self.current_database == "blue":
                cache_file.write(f"{self.blue_database}")
            elif self.current_database == "green":
                cache_file.write(f"{self.green_database}")
            else:
                raise ValueError(f"Invalid current database '{self.current_database}'")

    def get_current_database_path(self):
        if self.current_database == "blue":
            return self.blue_database
        elif self.current_database == "green":
            return self.green_database
        else:
            raise ValueError(f"Invalid current database '{self.current_database}'")

    def swap_database_path(self):
        if self.current_database == "blue":
            self.current_database = "green"
        elif self.current_database == "green":
            self.current_database = "blue"
        else:
            raise ValueError(f"Invalid current database '{self.current_database}'")
        self.set_cached_path()

    def update_inactive_database(self):
        if self.current_database == "blue":
            path = self.green_database
        elif self.current_database == "green":
            path = self.blue_database
        else:
            raise ValueError(f"Invalid current database '{self.current_database}'")

        create_database(GTFS_ZIP, RAW_DIR, f"{path}")




if __name__ == "__main__":
    test_manager = DatabaseManager("gfts/sql/blue.db",
                                   "gfts/sql/green.db",
                                   "gfts/sql/current_database.txt")
    test_manager.update_inactive_database()
    test_manager.swap_database_path()
    # print(test_manager.current_database)

