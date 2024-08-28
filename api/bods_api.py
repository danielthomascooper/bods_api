from lxml import etree
from typing import Literal
import requests
from api.location.responses import LocationResponse

data_types = ["location", "timetable", "fares"]  # allowed data types


api_urls = {  # url for each BODS api
    "location": "https://data.bus-data.dft.gov.uk/api/v1/datafeed/",
    "timetable": "https://data.bus-data.dft.gov.uk/api/v1/dataset/",
    "fares": "https://data.bus-data.dft.gov.uk/api/v1/fares/dataset/"
}

allowed_keywords = {  # list of allowed keywords for each api
    "location": ["boundingBox",
                 "operatorRef",
                 "lineRef",
                 "producerRef",
                 "originRef",
                 "destinationRef",
                 "vehicleRef"],
    "timetable": ["adminArea",
                 "endDateStart",
                 "endDateEnd",
                 "limit",
                 "modifiedDate",
                 "noc",
                 "offset",
                 "search",
                 "status",
                 "startDateStart",
                 "startDateEnd",
                 "datasetID",
                 "dqRag",
                 "bodsCompliance"],
    "fares": ["noc",
              "status",
              "boundingBox",
              "limit",
              "offset"]
}

def get_api_path(base_url: str, query_params: dict):
    """Helper function returns api url with parameters"""
    return base_url + "?" + "&".join([f"{k}={query_params[k]}" for k in query_params])


def BODS_request(api_key: str,
                 data_type: Literal["location", "location_proto", "timetable", "fares"],
                 **params) -> LocationResponse|str:
        if not data_type in data_types:
            raise ValueError(f"'{data_type}' is an invalid data type, must be one of {data_types}")

        if not params:
            raise ValueError("Must include at least one parameter in request.")

        for param in params:
            if not param in allowed_keywords[data_type]:
                raise ValueError(f"'{param}' is not a valid keyword for data type '{data_type}'")

        params["api_key"] = api_key
        api_url = get_api_path(api_urls[data_type], params)

        r = requests.get(api_url)
        tree = etree.fromstring(r.text)
        match data_type:
            case "location":
                return LocationResponse(tree)
            case "timetable":
                return "timetable placeholder"
            case "fares":
                return "fares placeholder"


if __name__ == "__main__":
    pass