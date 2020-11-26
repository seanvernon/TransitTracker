from arrival import Arrival
from urllib.request import urlopen

import datetime
import sys
import xml.etree.ElementTree as ET

# Calls the CTA Train Tracker Arrival API to get a list of ETAs
# for all trains at the requested station.
# Returns a list of Arrival objects.
def arrivals_at_station(station, key):
    URL_BASE = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    arr_xml = urlopen(f"{URL_BASE}?key={key}&mapid={station}")
    arr_xml = ET.parse(arr_xml)

    etas = []
    for child in arr_xml.getroot():
        if child.tag == "eta":
            etas.append(child)
        elif child.tag == "errCd":
            if child.text != "0":
                print(f"API Error {child.text}")
                return []

    arr_lst = []
    for eta in etas:    
        station_name = eta[2].text 
        line = eta[5].text
        stop_desc = eta[3].text
        pred_t = convert_timestamp(eta[9].text)
        arr_t = convert_timestamp(eta[10].text)
        wait_time = round((arr_t - pred_t).seconds / 60)
        arr_lst.append(Arrival(station_name, line, stop_desc, wait_time))
    return arr_lst

# Converts timestamps returned by API to datetime.datetime objects.
def convert_timestamp(api_ts):
    api_ts = api_ts[:4] + "-" + api_ts[4:6] + "-" + api_ts[6:]
    return datetime.datetime.fromisoformat(api_ts)


if __name__ == "__main__":

    if (sys.argv[1] == "-h") or (sys.argv[1] == "--help"):
        print("Usage: python train_arrival_times.py <station code>")

    else:
        with open("../api/train_api_key.txt", 'r') as file:
            TRAIN_KEY = file.readline()[:-1]

        station = sys.argv[1]
        if (int(station) < 40000) or (int(station) > 49999):
            print("Invalid station code")

        else:
            arrivals = arrivals_at_station(station, TRAIN_KEY)
            for arrival in sorted(arrivals, key=lambda arrival: arrival.wait_time):
                print(arrival)
