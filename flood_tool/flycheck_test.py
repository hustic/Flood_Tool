import csv
import numpy as np
import pandas as pd
import geo
from scipy.spatial import distance
from tool import Tool


print(geo.get_easting_northing_from_lat_long(51.197065, 1.385194))
tool = Tool('./resources/postcodes.csv', './resources/flood_probability.csv', './resources/property_value.csv')
tool.get_sorted_annual_flood_risk(['ME157QU', 'TN2 3PA', 'TN173HD', 'CT117DG', 'TN104RU', 'CT1 3LA',
                                   'CT1 1SF', 'DA2 6AA', 'TN159AP', 'BR8 7TZ', 'ME174RB',
       'ME123GF', 'ME9 0SJ', 'CT1 1AX', 'ME157QN'])
'''
def get_annual_flood_risk(postcodes, probability_bands):
    probs = {'Very Low':1/1000, 'Low':1/100, 'Medium': 1/50, 'High':1/10, 'Zero':0}
    return [probs[p] for p in probability_bands]


postcodes = []
probability = []

with open('./tests/test_data.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        postcodes.append(row[0])
        probability.append(row[6])

postcodes = np.array(postcodes[1:])
probability = np.array(probability[1:])
#print(probability)

dfp = pd.read_csv('./resources/postcodes.csv')
dff = pd.read_csv('./resources/flood_probability.csv')
dfc = pd.read_csv('./resources/property_value.csv')


#print(dfp.loc[:, 'Longitude'])


easting, northing = geo.get_easting_northing_from_lat_long(dfp.loc[:,'Latitude'], dfp.loc[:, 'Longitude'])
dfp['Easting'] = easting
dfp['Northing'] = northing
dfp = pd.merge(dfp, dfc[['Postcode', 'Total Value']], on='Postcode')

dff['Numerical Risk'] = dff['prob_4band'].replace(['High', 'Medium', 'Low', 'Very Low', 'Zero'],[4,3,2,1,0])
dff = dff.sort_values(by=['Numerical Risk'], ascending=True)
dfp['Probability Band'] = 'Zero'

print(dff)
print(dfp['Probability Band'][10])
#print(dfp.loc[: ,"Easting"])
for index, row in dff.iterrows():
    #print(np.array([dfp['Easting'], dfp['Northing']]))
    dist = distance.cdist(np.array([[row['X'], row['Y']]]), np.vstack((dfp['Easting'], dfp['Northing'])).T)
    points = np.where(dist < row['radius'] * 1000)

    #print(row['prob_4band'])
    if points:#print(points[1])
        dfp.loc[points[1], 'Probability Band'] = row['prob_4band']

print(dfp.head())
#print(dfp)

        #print(row['Total Value'])
#print(dfp[dfc['Postcode', 2]])
'''

#print(dfp.head())
#print(dff.head())
#print(dfc.head())
#print(get_annual_flood_risk(postcodes, probability))
