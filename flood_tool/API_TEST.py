import requests
import json
import tool
import geo
from math import sqrt
import numpy as np

#lat_long = tool.Tool.get_lat_long(postcodes)
#E_N = geo.get_easting_northing_from_lat_long(lat_long[:, 0], lat_long[:, 1])
E_N = np.array([geo.get_easting_northing_from_lat_long(91.28419, 5.29875)])
url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall'

resp = requests.get(url)#, params=settings)
print(E_N)
#retrieve data
# data = resp.json()
data = json.loads(resp.text)
coord = data.get('items')
#print(coord)

#E_N = np.array([[467950, 315350], [428150, 376850], [460850, 379150]])

for i in range(1):
    station = ''
    a = []
    # lat = lat_long[i, 0]
    # long =lat_long[i, 1]
    lat = 91.28419
    long = 5.29875

    prox_url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall' + '&lat=' + str(lat) + '&long=' + str(long) + '&dist=10000'
    prox = requests.get(prox_url)
    prox_data = json.loads(prox.text)
    prox_stations = prox_data.get('items')
    length = len(prox_data.get('items'))
    for j in range(0, length, 1):
        if coord[j].get('northing') == None:
            continue
        if coord[j].get('easting') == None:
            continue

        else:
            northing = int(coord[j]['northing'])
            easting = int(coord[j]['easting'])
            distance = np.sqrt(np.abs((easting - E_N[i, 0])**2 + (northing - E_N[i, 1])**2))  
            a.append(distance)
            index_min = min(range(len(a)), key=a.__getitem__)
    station_reference = coord[index_min]['notation']
    station = 'https://environment.data.gov.uk/flood-monitoring/id/measures?parameter=rainfall' + '&stationReference=' + station_reference
    print(station)
    station_data = requests.get(station)
    station_data = json.loads(station_data.text)
    if station_data.get('items')[0].get('latestReading') == None:
        print('Station', station_reference, 'has no value. Assume 0 rain.')
    else:
        station_value = station_data.get('items')[0].get('latestReading').get('value')
        print('Station', station_reference, ':', station_value, 'mm of rain.')
        if 2 <        station_value < 3:
            print('Yellow warning, medium risk')
        elif 3 < station_value:
            print('Red warning, high risk')

