import csv
import logging
import threading
from lxml import etree
import pandas as pd
import json
import xmltodict
from api.xml_methods import local_xpath, element_to_dict, flatten
import os

logger = logging.getLogger(__name__)

_stop_dict: dict[str, dict] = {}
_stop_dict_lock = threading.Lock()

def load_stops(path: str) -> dict[str, dict]:
    loaded_stops = {}
    with open(path, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            acto_code: str = row.pop("ATCOCode")
            loaded_stops[acto_code] = row
    return loaded_stops


def _ensure_stops_loaded(rel_path: str) -> dict[str, dict]:
    global _stop_dict
    if _stop_dict:
        return _stop_dict
    with _stop_dict_lock:
        if not _stop_dict:
            logger.info("Loading stop data from %s", rel_path)
            _stop_dict = load_stops(rel_path)
            logger.info("Loaded %d stops", len(_stop_dict))
    return _stop_dict

class LocationResponse:
    def __init__(self, response_tree: etree.Element, stop_path: str = "Stops.csv"):
        """Create new location response object.

        Parameters
        ----------
        response_tree : etree.Element
            The full etree returned from the xpath returned from the BODS api.
        stop_path : str = "Stops.csv"
            The path to the NaPTaN csv file containing all stop data.
        """
        self.root: etree.Element = response_tree
        self.namespace = etree.QName(self.root).namespace  # get root default namespace

        if os.path.isabs(stop_path):
            rel_path = stop_path
        else:
            script_dir = os.path.dirname(__file__)
            rel_path = os.path.join(script_dir, "..", stop_path)
        self._stop_dict = _ensure_stops_loaded(rel_path)

        self.fix_station_names()


    def add_namespace(self, local_name: str) -> str:
        """Add the default namespace to the local name.

        Parameters
        ----------
        local_name : str
            The local name to be added

        Returns
        -------
        str
            The full tag including namespace.
        """
        return f"{{{self.namespace}}}{local_name}"

    def to_dict(self):
        vehicle_expr = (f"//{local_xpath('ServiceDelivery')}/"
                        f"{local_xpath('VehicleMonitoringDelivery')}/"
                        f"{local_xpath('VehicleActivity')}")
        vehicle_elements = self.root.xpath(vehicle_expr)
        vehicle_list = [element_to_dict(elem) for elem in vehicle_elements]

        return vehicle_list

    def to_df(self):
        """Returns each bus location as a pandas dataframe"""
        bus_list = self.to_dict()
        flat_list = [flatten(bus) for bus in bus_list]
        return_df = pd.DataFrame(flat_list)
        return_df[['MonitoredVehicleJourney_VehicleLocation_Latitude', 'MonitoredVehicleJourney_VehicleLocation_Longitude']] = (
            return_df[['MonitoredVehicleJourney_VehicleLocation_Latitude', 'MonitoredVehicleJourney_VehicleLocation_Longitude']].apply(pd.to_numeric))
        return return_df

    def to_json(self):
        """Returns the response as a json string"""
        return json.dumps(xmltodict.parse(etree.tostring(self.root)))

    def fix_station_names(self):
        """Replace the origin and dest names with the properly formatted versions."""
        orig_name_elems = self.root.xpath(f"//{local_xpath('MonitoredVehicleJourney')}/{local_xpath('OriginName')}")
        orig_ref_elems = self.root.xpath(f"//{local_xpath('MonitoredVehicleJourney')}/{local_xpath('OriginRef')}")
        dest_name_elems = self.root.xpath(f"//{local_xpath('MonitoredVehicleJourney')}/{local_xpath('DestinationName')}")
        dest_ref_elems = self.root.xpath(f"//{local_xpath('MonitoredVehicleJourney')}/{local_xpath('DestinationRef')}")
        for orig_name_elem, orig_ref_elem, dest_name_elem, dest_ref_elem in \
            zip(orig_name_elems, orig_ref_elems, dest_name_elems, dest_ref_elems):
            try:
                orig_name_elem.text = self._stop_dict[orig_ref_elem.text]["CommonName"]
                dest_name_elem.text = self._stop_dict[dest_ref_elem.text]["CommonName"]
            except KeyError:
                continue


