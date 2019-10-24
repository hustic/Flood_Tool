import requests
import json
# import tool
# import geo
from math import sqrt
import numpy as np
import pandas as pd
import csv
from flask import Flask
import matplotlib.pyplot as plt

def historic_API(date):
    url = 'https://environment.data.gov.uk/flood-monitoring/archive/readings-full-' + date + '.csv'
    #print(url)
    data_csv = pd.read_csv(url)
    df=pd.DataFrame(data=data_csv)
    #print(df)
    df = df.groupby('parameter')
    df = df.get_group('rainfall')
    df = df.reset_index()
    #print(df)
    values = []
    dates = []
    stations = []
    northing = []
    easting = []
    station_list = []
    northeast = []
    for row in range(0, 10):
        historic_values = df.loc[row, 'value']
        historic_date = df.loc[row, 'dateTime']
        station = df.loc[row, 'stationReference']   
        historic_values = pd.to_numeric(historic_values, errors='coerce')

        if isinstance(historic_values, float) == False:
            continue

        if station in station_list:
            stations.append(station)
            northing.append(northing[station_list.index(station)])
            easting.append(easting[station_list.index(station)])                
        else:
            station_list.append(station)
            station_url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall&stationReference=' + str(station)
            coordinates = requests.get(station_url)
            coordinates = json.loads(coordinates.text)

            north = coordinates.get('items')[0].get('northing')
            east = coordinates.get('items')[0].get('easting')

            stations.append(station)
            northing.append(north)
            easting.append(east)

        #print(historic_date)
        values.append(historic_values)
        dates.append(historic_date)

        # if north[row] > 286822 and east[row] > 406689:
        #     northeast.append(historic_values)

        #print(values)
    historic_rain = pd.DataFrame({'dates':dates[:], 'station':stations[:], 'northing':northing[:], 'easting':easting[:], 'values':values[:]})
    historic_rain['dates'] = historic_rain['dates'].map(lambda x: x.rstrip('Z'))
    historic_rain['date'], historic_rain['time'] = historic_rain['dates'].str.split('T', 1).str

    #rain = historic_rain.sort_index()
    #historic_rain.set_index('time', drop=True, append=False, inplace=True, verify_integrity=False)
    historic_rain = historic_rain.drop('dates', axis=1).drop('date', axis=1).sort_values(by='time', ascending=True)
    #print(historic_rain)
    #print(historic_rain.dtypes)
    group = historic_rain.groupby(['station', 'northing', 'easting', 'time'], as_index=False)['values'].mean()
    #i = historic_rain.groupby(['station', 'time']).cumcount()
    historic_rain.set_index(['station']).time
    print('g', group)
    # northeast = group[]
    historic_rain = pd.DataFrame({'dates':dates[:], 'station':stations[:], 'northing':northing[:], 'easting':easting[:], 'values':values[:]})
    historic_rain['dates'] = historic_rain['dates'].map(lambda x: x.rstrip('Z'))
    historic_rain['date'], historic_rain['time'] = historic_rain['dates'].str.split('T', 1).str
    historic_rain = historic_rain.drop('dates', axis=1).drop('date', axis=1).sort_values(by='time', ascending=True)

    northeast = historic_rain.loc[(historic_rain.northing > 286822) & (historic_rain.easting > 406689)]
    print('ne', northeast)
    northeast_averageT = northeast.groupby('time')['values'].mean().reset_index()
    print('neAT', northeast_averageT)
    northeast_average = northeast['values'].mean()

    southeast = historic_rain.loc[(historic_rain.northing < 286822) & (historic_rain.easting > 406689)]
    print('se', southeast)
    southeast_average = southeast['values'].mean()
    southeast_averageT = southeast.groupby('time')['values'].mean().reset_index()
    print('seA', southeast_average)

    northwest = historic_rain.loc[(historic_rain.northing > 286822) & (historic_rain.easting < 406689)]
    print('nw', northwest)
    northwest_average = northwest['values'].mean()
    northwest_averageT = northwest.groupby('time')['values'].mean().reset_index()
    print('nwA', northwest_average)

    southwest = historic_rain.loc[(historic_rain.northing < 286822) & (historic_rain.easting < 406689)]
    print('sw', southwest)
    southwest_average = southwest['values'].mean()
    southwest_averageT = southwest.groupby('time')['values'].mean().reset_index()
    print('swA', southwest_average)

    # plt.plot(northeast['time'], northeast_average['values'])
    # print(historic_rain)
    # print(average)
    plt.figure(1)
    scale_ls = range(4)
    index_ls = ['NE', 'SE', 'NW', 'SW']
    area_data=[northeast_average, southeast_average, northwest_average, southwest_average]
    plt.xticks(scale_ls, index_ls)
    plt.xlabel('Quadrant')
    plt.ylabel('Average Rainfall (mm)')
    plt.ylim((0, 0.1))
    plt.bar(scale_ls,area_data )
    plt.show()

    plt.figure(2)
    plt.title('England Rainfall Against Time for ' + date)
    plt.subplot(2, 2, 1)
    plt.plot(northwest_averageT['time'], northwest_averageT['values'])
    plt.xlabel('Time')
    plt.xticks(rotation=30)
    plt.ylabel('Average Rainfall (mm)')
    plt.title('North West')

    plt.subplot(2, 2, 2)
    plt.plot(northeast_averageT['time'], northeast_averageT['values'])
    plt.xlabel('Time')
    plt.xticks(rotation=30)
    plt.ylabel('Average Rainfall (mm)')
    plt.title('North East')

    plt.subplot(223)
    plt.plot(southwest_averageT['time'], southwest_averageT['values'])
    plt.xlabel('Time')
    plt.xticks(rotation=30)
    plt.ylabel('Average Rainfall (mm)')
    plt.title('South West')
    
    plt.subplot(224)
    plt.plot(southeast_averageT['time'], southeast_averageT['values'])
    plt.xlabel('Time')
    plt.xticks(rotation=30)
    plt.ylabel('Average Rainfall (mm)')
    plt.title('South East')
    
    plt.subplots_adjust(left=None, bottom=-0.4, top=0.95, right=None)

    plt.show()








historic_API('2019-01-01')
app = Flask(__name__)

# @app.route('/')
# def hello():
#     return "hello"

# if __name__ == '__main__':
#     app.run()