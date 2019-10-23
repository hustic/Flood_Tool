import requests
import json
# import tool
# import geo
from math import sqrt
import numpy as np
import pandas as pd
import csv


def historic_API(date):
    url = 'https://environment.data.gov.uk/flood-monitoring/data/readings.csv?date=' + date
    print(url)
    data_csv = pd.read_csv(url)
    df=pd.DataFrame(data=data_csv)
    #print(df)

    values = []
    dates = []
    stations = []
    northing = []
    easting = []


    for row in range(20000,20020):
        a = 'raingauge'
        

        #print(type(df.loc[row]))
        if a in df.loc[row, 'measure']:
            historic_values = df.loc[row, 'value']
            historic_date = df.loc[row, 'dateTime']
            
            measurement = requests.get(df.loc[row, 'measure'])
            measurement = json.loads(measurement.text)
            station = measurement.get('items').get('stationReference')
            station_url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall&stationReference=' + str(station)
            coordinates = requests.get(station_url)
            coordinates = json.loads(coordinates.text)

            north = coordinates.get('items')[0].get('northing')
            east = coordinates.get('items')[0].get('easting')
            #print(northing, easting)
            stations.append(station)
            northing.append(north)
            easting.append(east)
            print(historic_date)
            values.append(historic_values)
            dates.append(historic_date)
            #print(df.loc[row, 'measure'])
            
            #print(values)
        else:
            continue
    historic_rain = pd.DataFrame({'dates':dates[:], 'station':stations[:], 'northing':northing[:], 'easting':easting[:], 'values':values[:]})
    #average = historic_rain['values'].mean()
    print(historic_rain)
    #print(average)


historic_API('2019-10-22')
