from lxml import etree
from typing import Literal
from urllib.parse import urlencode
import logging
import requests
from api.location.responses import LocationResponse

logger = logging.getLogger(__name__)

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


def BODS_request(api_key: str,
                 data_type: Literal["location", "location_proto", "timetable", "fares"],
                 **params) -> LocationResponse | str:
        if data_type not in data_types:
            raise ValueError(f"'{data_type}' is an invalid data type, must be one of {data_types}")

        if data_type in ("timetable", "fares"):
            raise NotImplementedError(f"'{data_type}' data type is not yet implemented")

        if not params:
            raise ValueError("Must include at least one parameter in request.")

        for param in params:
            if param not in allowed_keywords[data_type]:
                raise ValueError(f"'{param}' is not a valid keyword for data type '{data_type}'")

        params["api_key"] = api_key
        api_url = api_urls[data_type] + "?" + urlencode(params)

        r = requests.get(api_url, timeout=30)
        r.raise_for_status()

        tree = etree.fromstring(r.content)
        match data_type:
            case "location":
                return LocationResponse(tree)
            case "timetable":
                raise NotImplementedError("Timetable data type is not yet implemented")
            case "fares":
                raise NotImplementedError("Fares data type is not yet implemented")


if __name__ == "__main__":
    pass