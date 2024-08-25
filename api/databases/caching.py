import datetime
import json
import logging
import xmltodict
import requests
import csv
import time

def seconds_until_gtfs(timestamp: int|str) -> int:
    timestamp = int(timestamp)
    SPARE_TIME = 5 * 60
    current_timestamp = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    current_hour = current_timestamp.hour

    if 6 <= current_hour < 18:
        update_time = datetime.datetime(current_timestamp.year,
                                        current_timestamp.month,
                                        current_timestamp.day,
                                        18 + SPARE_TIME // 3600,
                                        SPARE_TIME // 60,
                                        SPARE_TIME % 60,
                                        tzinfo=datetime.timezone.utc)
    else:
        update_time = datetime.datetime(current_timestamp.year,
                                        current_timestamp.month,
                                        current_timestamp.day,
                                        6 + SPARE_TIME // 3600,
                                        SPARE_TIME // 60,
                                        SPARE_TIME % 60,
                                        tzinfo=datetime.timezone.utc)
        if 18 <= current_hour:
            update_time = update_time + datetime.timedelta(1)

    time_until_gtfs = update_time - current_timestamp
    return int(time_until_gtfs.total_seconds())


# paths to download each api
API_PATHS = {"gazetteer": "https://naptan.api.dft.gov.uk/v1/nptg",
             "gtfs": "https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/all/"}

# minimum time between database fetches as a function
TIME_LIMITS = {"gazetteer": lambda _: 3600 * 12,
               "gtfs": seconds_until_gtfs}

def update_databases() -> None:
    """Update databases if time specified in 'TIME_LIMITS' has passed"""
    global API_PATHS, TIME_LIMITS
    existing_keys = {}  # get all existing keys
    with open("last_fetched.csv", newline="") as file_reader:
        csv_reader = csv.DictReader(file_reader)
        for row in csv_reader:
            if not row:  # skip empty lines
                continue
            key, timestamp = row["key"], row["fetched"]
            existing_keys[key] = True
            if (key in API_PATHS) and (time.time() - int(timestamp) > TIME_LIMITS[key](timestamp)):
                logging.info(f"outdated: {key}")
                download_data(key)

    for key in API_PATHS:  # download all never downloaded files
        if key not in existing_keys:
            logging.info(f"never fetched: {key}")
            download_data(key)


def update_timing(key: str) -> None:
    """Update the timing of the 'last_fetched.csv' file' for 'key' if cached file is stale.

    Parameters
    ----------
    key : str
        The key to update the timings for.

    Returns
    -------
    None
    """

    with open("last_fetched.csv", newline="") as file_reader:
        csv_rows = []
        exists = False  # if key exists in file
        csv_reader = csv.DictReader(file_reader)
        for row_dict in csv_reader:
            if row_dict["key"] == key:
                row_dict["fetched"] = str(int(time.time()))  # update time
                exists = True
            csv_rows.append(row_dict)
        if not exists:
            csv_rows.append({"key": key, "fetched": str(int(time.time()))})  # add new row with key if not exists

    with open("last_fetched.csv", "w", newline="") as file_writer:  # save changes to file
        csv_writer = csv.DictWriter(file_writer, csv_rows[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(csv_rows)  # update timings


def download_data(key: str) -> None:
    """Download the specified key to store on the hard-drive.

    Parameters
    ----------
    key : str
        Database key to download.

    Returns
    -------
    None

    """
    global API_PATHS

    logging.info(f"downloading: {key}")
    match key:
        case "gazetteer":
            response_return = requests.get(API_PATHS[key])  # get file from api
            with open("gazetteer.json", "w+") as json_file:
                json.dump(xmltodict.parse(response_return.text.encode()),
                          json_file)  # convert to dict and dump to 'json_file'
        case "gtfs":
            response_return = requests.get(API_PATHS[key], stream=True)  # stream rather than all in memory
            with open("itm_all_gtfs.zip", "wb") as writer:
                for chunk in response_return.iter_content(1024*1024*100):  # 100 MB chunks
                    writer.write(chunk)

    logging.info(f"downloaded: {key}")
    update_timing(key)


def get_database(key: str) -> dict:
    """Get database contents as dictionary.

    Parameters
    ----------
    key : str
        Database key to fetch
    Returns
    -------
    dict
        Dictionary containing all json data
    """


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    update_databases()  # test update
