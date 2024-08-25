import sqlite3
import os
import zipfile
from api.databases.gfts.commands import *
import csv
from pathlib import Path
import subprocess
import pandas as pd
from time import perf_counter


def csv_to_db(database: str|os.PathLike, src_dir: str|os.PathLike):
    database = Path(database).as_posix()
    conn = sqlite3.connect(database)

    for file in os.listdir(src_dir):
        if file != "trips.csv":
            continue
        start_time = perf_counter()
        conn.execute(CREATE_TABLE_COMMANDS[file])
        full_csv_path = Path(os.path.join(src_dir, file)).as_posix()
        filename = Path(file).stem
        print(filename)

        # print(f'""{Path(database).as_posix()}""')
        # print(f'.import -skip 1 ""{Path(full_csv_path).as_posix()}"" {filename}')

        # command = ['sqlite3', f'""{Path(database).as_posix()}""', '-cmd', '.mode csv', f'.import -skip 1 ""{Path(full_csv_path).as_posix()}"" {filename}']
        # command = ['sqlite3', f'{Path(database).as_posix()}', f'.import --csv --skip 1 "{Path(full_csv_path).as_posix()}" {filename}']
        # print(command)
        #
        # result = subprocess.run(command, capture_output=True)
        # print(result.stdout.decode())
        # print(result.stderr.decode())

        with open(full_csv_path, 'r', newline="") as f:
            csv_reader = csv.DictReader(f)
            field_string = ", ".join([":"+x for x in csv_reader.fieldnames])
            cmd = f"INSERT INTO {filename} VALUES({field_string})"
            conn.executemany(cmd, csv_reader)
            conn.commit()
        conn.close()

        # chunk_size = 1E7
        # for chunk in pd.read_csv(full_csv_path, chunksize=chunk_size, dtype=COLUMN_TYPES[file]):
        #     chunk.to_sql(filename, conn, if_exists='append', index=False)
        # conn.commit()
        print(perf_counter() - start_time)
    conn.close()

def setup_database(zip_path: os.PathLike|str, extraction_dir: os.PathLike|str):
    # directories for raw and db files
    raw_dir = os.path.join(extraction_dir, "raw")
    sql_dir = os.path.join(extraction_dir, "sql")

    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir)
    if not os.path.isdir(sql_dir):
        os.makedirs(sql_dir)

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

    csv_to_db(raw_dir, sql_dir)

if __name__ == "__main__":
    # setup_database("itm_all_gtfs.zip", "gfts")
    csv_to_db(r"C:\Users\Daniel\OneDrive - University of Bristol\comp_tings\bods_api\api\databases\gfts\gfts.db",
              r"C:\Users\Daniel\OneDrive - University of Bristol\comp_tings\bods_api\api\databases\gfts\raw")