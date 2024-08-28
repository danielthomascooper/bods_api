import sqlite3
import os
import zipfile
from api.databases.gfts.commands import *
import csv
from pathlib import Path
from time import perf_counter
import glob
import logging


def gtfs_files_to_db(database: str|os.PathLike, src_dir: str|os.PathLike):
    """Save directory of GTFS compliant files to database.

    Parameters
    ----------
    database : str or os.PathLike
        The database file to be written to.
    src_dir : str or os.PathLike
        The directory containing the GTFS compliant files.

    Returns
    -------
    None
    """
    database = Path(database).as_posix()  # convert to posix form
    conn = sqlite3.connect(database)

    for file in os.listdir(src_dir):
        start_time = perf_counter()
        conn.executescript(CREATE_TABLE_COMMANDS[file])
        full_csv_path = Path(os.path.join(src_dir, file)).as_posix()
        filename = Path(file).stem
        logging.info(f"Saving '{file}' to second SQL database")

        with open(full_csv_path, 'r', newline="") as f:
            csv_reader = csv.DictReader(f)
            field_string = ", ".join([":"+x for x in csv_reader.fieldnames])
            cmd = f"INSERT INTO {filename} VALUES({field_string})"
            conn.executemany(cmd, csv_reader)
            conn.commit()

        file_time = perf_counter() - start_time
        logging.info(f"Uploading file {file} took {file_time // 60}:{file_time % 60:.2f}")
    conn.close()

def create_database(zip_path: os.PathLike|str, extraction_dir: os.PathLike|str, database_path: os.PathLike|str):
    # directories for raw and db files
    raw_dir = os.path.join(extraction_dir, "raw")
    sql_dir = os.path.join(extraction_dir, "sql")

    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir)
    if not os.path.isdir(sql_dir):
        os.makedirs(sql_dir)

    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    for f in csv_files:
        os.remove(f)

    if not os.path.isfile(zip_path):
        raise ValueError(f"'{zip_path}' is not a valid .zip file")

    if os.path.exists(extraction_dir) and not os.path.isdir(extraction_dir):
        raise ValueError(f"'{extraction_dir}' is not a valid directory")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(raw_dir)

    for file in os.listdir(raw_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".txt"):
            new_filename = filename.split(".")[0] + ".csv"

            old_path = os.path.join(raw_dir, filename)
            new_path = os.path.join(raw_dir, new_filename)
            os.rename(old_path, new_path)

    gtfs_files_to_db(os.path.join(sql_dir, database_path), raw_dir)

if __name__ == "__main__":
    create_database("itm_all_gtfs.zip", "gfts", "gfts.db")
