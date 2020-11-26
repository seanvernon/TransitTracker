from arrival import Arrival
from urllib.request import urlopen

import datetime
import sys
import xml.etree.ElementTree as ET

# Calls the CTA BUS Tracker Arrival API to get a list of ETAs
# for all buses at the requested stop.
# Returns a list of Arrival objects.
def arrivals_at_stop(route, stop, key):
    URL_BASE = "http://www.ctabustracker.com/bustime/api/v1/getpredictions"
    arr_xml = urlopen(f"{URL_BASE}?key={key}&rt={route}&stpid={stop}")
    arr_xml = ET.parse(arr_xml)

    etas = []
    for child in arr_xml.getroot():
        if child.tag == "prd":
            etas.append(child)
        elif child.tag == "error":
            print(child[0].text)
            return []

    arr_lst = []
    for eta in etas: 
        if eta[1].text == "A": 
            station_name = eta[2].text 
            line = f"#{eta[6].text}"
            stop_desc = f"{eta[8].text} to {eta[9].text}"
            pred_t = convert_timestamp(eta[0].text)
            arr_t = convert_timestamp(eta[10].text)
            wait_time = round((arr_t - pred_t).seconds / 60)
            arr_lst.append(Arrival(station_name, line, stop_desc, wait_time))
    return arr_lst

# Converts timestamps returned by API to datetime.datetime objects.
def convert_timestamp(api_ts):
    api_ts = api_ts[:4] + "-" + api_ts[4:6] + "-" + api_ts[6:]
    return datetime.datetime.fromisoformat(api_ts)


if __name__ == "__main__":

    if (len(sys.argv) == 1) or (sys.argv[1] == "-h") or (sys.argv[1] == "--help"):
        print("usage: python bus_arrival_times.py <route> <stop code> <stop code> ...")

    else:
        with open("../api/bus_api_key.txt", 'r') as file:
            BUS_KEY = file.readline()[:-1]

        route = sys.argv[1]
        stops = sys.argv[2:]
        arrivals = []
        for stop in stops:
            if (int(stop) < 0) or (int(stop) > 29999):
                print(f"Invalid stop code {stop}")

            else:
                arrivals += arrivals_at_stop(route, stop, BUS_KEY)
        
        for arrival in sorted(arrivals, key=lambda arrival: arrival.wait_time):
            print(arrival)
