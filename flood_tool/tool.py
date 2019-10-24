"""Locator functions to interact with geographic data"""
import numpy as np
import pandas as pd
from scipy.spatial import distance
from flood_tool import geo

__all__ = ['Tool']

class Tool(object):
    """Class to interact with a postcode database file."""

    def __init__(self, postcode_file=None, risk_file=None, values_file=None):
        """

        Reads postcode and flood risk files and provides a postcode locator service.

        Parameters
        ---------

        postcode_file : str, optional
            Filename of a .csv file containing geographic location data for postcodes.
        risk_file : str, optional
            Filename of a .csv file containing flood risk data.
        postcode_file : str, optional
            Filename of a .csv file containing property value data for postcodes.
        """
        self.dfp = pd.read_csv(postcode_file)
        self.dff = pd.read_csv(risk_file)
        self.dfc = pd.read_csv(values_file)
        self.dfc['Postcode'] = self.dfc['Postcode'].str.replace(" ", "")
        self.dfp['Postcode'] = self.dfp['Postcode'].str.replace(" ", "")


        lat, lon = geo.WGS84toOSGB36(self.dfp.loc[:, 'Latitude'], self.dfp.loc[:, 'Longitude'])
        easting, northing = geo.get_easting_northing_from_lat_long(lat, lon)
        self.dfp['Easting'] = easting
        self.dfp['Northing'] = northing
        #print(self.dfp.head(10))
        #print(self.dff.head(10))
        self.dfp = self.dfp.merge(self.dfc[['Postcode', 'Total Value']], how='left', left_on='Postcode', right_on='Postcode').fillna(0)
        self.dff['Numerical Risk'] = self.dff['prob_4band'].replace(['High', 'Medium', 'Low', 'Very Low'], [4, 3, 2, 1])
        self.dff = self.dff.sort_values(by=['Numerical Risk'], ascending=True)
        self.dfp['Postcode'] = self.dfp['Postcode'].apply(lambda x: x[0:3] + " " + x[3:6] if len(x) == 6 else x)
        self.dfp['Postcode'] = self.dfp['Postcode'].apply(lambda x: x[0:2] + "  " + x[4:6] if len(x) == 5 else x)
        #self.dfp['Probability Band'] = self.get_easting_northing_flood_probability(self.dfp['Easting'], self.dfp['Northing'])
        #print(self.dfp.head(10))

    def get_lat_long(self, postcodes):
        """Get an array of WGS84 (latitude, longitude) pairs from a list of postcodes.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of N postcode strings

        Returns
        -------
       
        ndarray
            Array of Nx2 (latitude, longitdue) pairs for the input postcodes.
            Invalid postcodes return [`numpy.nan`, `numpy.nan`].
        """
        fp_data = self.dfp.loc[(self.dfp['Postcode'].isin(postcodes))]
        fp_data = fp_data.set_index('Postcode')
        fp_data = fp_data.reindex(index = postcodes)
        fp_data = fp_data.reset_index()

        return np.stack((fp_data['Latitude'].values, fp_data['Longitude'].values), axis= -1)


    def get_easting_northing_flood_probability(self, easting, northing):
        """Get an array of flood risk probabilities from arrays of eastings and northings.

        Flood risk data is extracted from the Tool flood risk file. Locations
        not in a risk band circle return `Zero`, otherwise returns the name of the
        highest band it sits in.

        Parameters
        ----------

        easting: numpy.ndarray of floats
            OS Eastings of locations of interest
        northing: numpy.ndarray of floats
            OS Northings of locations of interest

        Returns
        -------
       
        numpy.ndarray of strs
            numpy array of flood probability bands corresponding to input locations.
        """
        #res = np.full((len(easting)), 'Zero')
        #for _, row in self.dff.iterrows():
            #print(index)
         #   dist = distance.cdist(np.array([[row['X'], row['Y']]]), np.vstack((easting, northing)).T)
         #   points = np.where(dist < row['radius'])

          #  if points:
           #     res[points[1]] = row['prob_4band']

        res = np.full((len(easting)), 'Zero')
        c = np.vstack((easting, northing)).T
        def get_probs(row):
            dist = distance.cdist(np.array([[row[1], row[2]]]), c)
            points = np.where(dist <= row['radius'])
            if points:
                res[points[1]] = row['prob_4band']

        #self.dff.apply(get_probs, axis=1)

        return res




    def get_sorted_flood_probability(self, postcodes):
        """Get an array of flood risk probabilities from a sequence of postcodes.

        Probability is ordered High>Medium>Low>Very low>Zero.
        Flood risk data is extracted from the `Tool` flood risk file. 

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------
       
        pandas.DataFrame
            Dataframe of flood probabilities indexed by postcode and ordered from `High` to `Zero`,
            then by lexagraphic (dictionary) order on postcode. The index is named `Postcode`, the
            data column is named `Probability Band`. Invalid postcodes and duplicates
            are removed.
        """
        a = np.array(np.unique([s.replace(" ", "").upper() for s in postcodes]))
        print(a)
        fp_data = self.dfp.loc[(self.dfp['Postcode'].str.replace(" ", "").isin (a))]
        print(fp_data['Postcode'].values)
        fp_data = fp_data.set_index('Postcode')
        #fp_data = fp_data.reindex(index = a)
        #fp_data = fp_data.reset_index()
        replace_data = self.get_easting_northing_flood_probability(fp_data['Easting'], fp_data['Northing'])
        fp_data['Probability Band'] = replace_data
        fp_data['Probability Band'] = fp_data['Probability Band'].replace(['High', 'Medium', 'Low', 'Very Low', 'Zero'], [4, 3, 2, 1, 0])
        updated = fp_data.sort_values(by = ['Probability Band','Postcode'],ascending = (False,True))
        updated['Probability Band'] = updated['Probability Band'].replace([4, 3, 2, 1, 0], ['High', 'Medium', 'Low', 'Very Low', 'Zero'])
        #print(updated['Probability Band'])
        #updated = updated.set_index('Postcode')
        final = updated.drop(['Latitude', 'Longitude', 'Total Value', 'Easting', 'Northing'], axis=1)
        return final


    def get_flood_cost(self, postcodes):
        """Get an array of estimated cost of a flood event from a sequence of postcodes.
        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes
        probability_bands: sequence of strs
            Ordered collection of flood probability bands

        Returns
        -------
       
        numpy.ndarray of floats
            array of floats for the pound sterling cost for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """

        a = postcodes
        total_value_data = self.dfp.loc[(self.dfp['Postcode'].isin (a))]
        total_value_data = total_value_data.set_index('Postcode')
        total_value_data = total_value_data.reindex(index = a)
        total_value_data = total_value_data.reset_index()
        total_value_data = total_value_data.fillna(0)
        cost_value = np.array(total_value_data['Total Value'])
        return cost_value

    def get_annual_flood_risk(self, postcodes, probability_bands):
        """Get an array of estimated annual flood risk in pounds sterling per year of a flood
        event from a sequence of postcodes and flood probabilities.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes
        probability_bands: sequence of strs
            Ordered collection of flood probabilities

        Returns
        -------
       
        numpy.ndarray
            array of floats for the annual flood risk in pounds sterling for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """
        probs = {'Very Low':1/1000, 'Low':1/100, 'Medium':1/50, 'High':1/10, 'Zero':0}
        flrk = np.zeros(len(postcodes))
        for i in range(len(postcodes)):
            if postcodes[i] in self.dfp.Postcode:
                print("ye")
                flrk[i] = probs[probability_bands[i]] * self.dfp.loc[postcodes[i], 'Total Value'] * 0.05
            else:
                flrk[i] = np.nan
        return flrk

    def get_sorted_annual_flood_risk(self, postcodes):
        """Get a sorted pandas DataFrame of flood risks.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------
       
        pandas.DataFrame
            Dataframe of flood risks indexed by (normalized) postcode and ordered by risk,
            then by lexagraphic (dictionary) order on the postcode. The index is named
            `Postcode` and the data column `Flood Risk`.
            Invalid postcodes and duplicates are removed.
        """
        a = np.array(np.unique([s.replace(" ", "").upper() for s in postcodes]))
        print(a)
        fp_data = self.dfp.loc[(self.dfp['Postcode'].str.replace(" ", "").isin (a))]
        print(fp_data['Postcode'].values)

        #fp_data = fp_data.drop_duplicates()
        fp_data = fp_data.dropna()
        #fp_data.fillna(0, inplace=True)
        fp_data = fp_data.set_index('Postcode')
        #fp_data = fp_data.reindex(index = a)
        #fp_data = fp_data.reset_index()
        probs = self.get_easting_northing_flood_probability(fp_data['Easting'], fp_data['Northing'])
        fp_data['Flood Risk'] = self.get_annual_flood_risk(fp_data.index, probs)
        updated = fp_data.sort_values(by = ['Flood Risk','Postcode'],ascending = (False,True))
        #updated = updated.set_index('Postcode')
        final = updated.drop(['Latitude', 'Longitude', 'Total Value', 'Easting', 'Northing'], axis=1)
        return final
