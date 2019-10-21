import csv
import numpy as np

def get_annual_flood_risk(postcodes, probability_bands):
    probs = {'Very Low':1/1000, 'Low':1/100, 'Medium': 1/50, 'High':1/10, 'Zero':0}
    return [probs[p] for p in probability_bands]


postcodes = []
probability = []

with open('./flood_tool/tests/test_data.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        postcodes.append(row[0])
        probability.append(row[6])

postcodes = np.array(postcodes[1:])
probability = np.array(probability[1:])
print(probability)

print(get_annual_flood_risk(postcodes, probability))
