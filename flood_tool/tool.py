"""Locator functions to interact with geographic data"""
import numpy as np
import pandas as pd
from scipy.spatial import distance

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
        dff = pd.read_csv(risk_file)
        dfc = pd.read_csv(values_file)

        easting, northing = geo.get_easting_nothing_from_lat_long(dfp.loc[:, 'Latitude'], dfp.loc[:, 'Longitude'])
        self.dfp['Easting'] = easting
        self.dfp['Northing'] = northing
        self.dfp = pd.merge(dfp, dfc[['Postcode', 'Total Value']], on='Postcode')

        dff['Numerical Risk'] = dff['prob_4band'].replace(['High', 'Medium', 'Low', 'Very Low'], [4, 3, 2, 1])
        dff = dff.sort_values(by=['Numerical Risk'], ascending=True)
        self.dfp['Probability Band'] = 'Zero'

        for index, row in dff.iterrows():
            dist = distance.cdist(np.array([[row['X'], row['Y']]]), np.vstack((dfp['Easting'], dfp['Northing'])).T)
            points = np.where(dist < row['radius'] * 1000)

            if points:
                self.dfp.loc[points[1], 'Probability Band'] = row['prob_4band']


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

        raise NotImplementedError


    def get_easting_northing_flood_probability_band(self, easting, northing):
        """Get an array of flood risk probabilities from arrays of eastings and northings.

        Flood risk data is extracted from the Tool flood risk file. Locations
        not in a risk band circle return `Zero`, otherwise returns the name of the
        highest band it sits in.

        Parameters
        ----------

        easting: numpy.ndarray of floats
            OS Eastings of locations of interest
        northing: numpy.ndarray of floats
            Ordered sequence of postcodes

        Returns
        -------
       
        numpy.ndarray of strs
            numpy array of flood probability bands corresponding to input locations.
        """
        raise NotImplementedError


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
        raise NotImplementedError


    def get_flood_cost(self, postcodes, probability_bands):
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
        raise NotImplementedError


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
        raise NotImplementedError

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
        raise NotImplementedError
