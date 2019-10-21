# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:28:57 2019

@author: linga
"""
import numpy as np
import pandas as pd
test_data = pd.read_csv("C:/Users/linga/Desktop/acse-4-flood-tool-jordan/test_data.csv")
Postcode = test_data['Postcode']
Probability_Band = test_data['Probability Band'] 


def get_easting_northing_flood_probability_band(easting,northing):
    a = easting
    b = northing
    location_data = test_data.loc[(test_data.Easting == a)& (test_data.Northing == b)]
    bands = np.array(location_data['Probability Band'])
    return bands

def get_flood_cost(postcodes,probability_bands):
    a = postcodes
    b = probability_bands
    total_value_data = test_data.loc[(test_data.Postcode == a)& (test_data['Probability Band'] == b)]
    cost_value = np.array(total_value_data['Total Value'])*0.05
    return cost_value

def get_sorted_flood_probability(postcodes):
    replace_data = test_data['Probability Band'].replace('High',4)
    replace_data = replace_data.replace('Medium',3)
    replace_data = replace_data.replace('Low',2)    
    replace_data = replace_data.replace('Very Low',1)   
    replace_data = replace_data.replace('Zero',0)
    test_data['replace_data'] = replace_data
    descending_pb= test_data.sort_values(by = ['replace_data', 'Postcode'],ascending = False)
    
    
    
    
    
    
    
    
    