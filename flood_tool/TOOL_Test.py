import requests
import json
import tool
import geo
from math import sqrt
import numpy as np


url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall'

resp = requests.get(url)#, params=settings)

#retrieve data
# data = resp.json()
data = json.loads(resp.text)
coord = data.get('items')
#print(coord)

E_N = np.array([[467950, 315350], [428150, 376850], [460850, 379150]])
for i in range(3):
    station = ''
    a = []

    for j in range(12):
        if not coord[j]['northing'] or not coord[j]['easting']:
            continue
        #try:
        #    X = data.get("items").get("northing",[])
        #except AttributeError:
        #    continue
        else:
            northing = int(coord[j]['northing'])
            easting = int(coord[j]['easting'])
            #print((easting - E_N[i, 0])**2 + (northing - E_N[i, 1])**2)
            distance = np.sqrt(np.abs((easting - E_N[i, 0])**2 + (northing - E_N[i, 1])**2))  
            a.append(distance)
            #a.min()
        index_min = min(range(len(a)), key=a.__getitem__)
    station_reference = coord[index_min]['notation']
    station = 'https://environment.data.gov.uk/flood-monitoring/id/measures?parameter=rainfall' + '&stationReference=' + station_reference
    print(station)
    station_data = requests.get(station)  #
    station_data = json.loads(station_data.text)
    station_value = station_data.get('latestReading')#.get('value')  ### doesnt work
    print(type(station_value))
 
#when we find the correct stations, search url and obtain 'value'
