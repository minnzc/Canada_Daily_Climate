# -*- coding: utf-8 -*-
"""
This script defines various functions required by the main codes to generate
a daily average climate data set for Ontario using Census divisions.

Author:       Minnie Cui
Date written: 20 April 2021
Last updated: ---
"""
###############################################################################
# IMPORT REQUIRED PACKAGES
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

###############################################################################
# FUNCTIONS REQUIRED BY getCDAvgs.py

# Define function to get a dataframe of average daily climate (temp, precipitation) by Census subdivisions
def getSD(stations_df, subdivisions_sf):
    """
    Returns master dataframe containing the Census subdivisions weather
    stations belong to. If no Census subdivision is found, the weather station
    is marked as belonging to closest Census subdivision within a 50km radius.
    
    Parameters
    ----------
    stations : dataframe
        Dataframe containing all active Canadian weather stations as of 13 April 2021.
    subdivisions : shapefile
        Shapefile containing Census subdivisions with WGS-84 coordinates.

    Returns
    -------
    dataframe
        Panel dataframe containing all weather stations in Canada and the 
        Census subdivision, Census division, and province in which each is 
        located.
    """
    records = subdivisions_sf.records()
    data = []
    stations_data = stations_df[['x', 'y', 'CLIMATE_IDENTIFIER']].copy().drop_duplicates()
    stations_data.reset_index(drop=True, inplace=True)
    col_names = ['CLIMATE_IDENTIFIER' , 'CSDUID', 'CSDNAME', 'PRUID', 'PRNAME', 'CDUID', 'CDNAME']
    for i in range(len(stations_data)):
        point = Point(stations_data.iloc[i, 0], stations_data.iloc[i, 1])
        sub_data = [stations_data['CLIMATE_IDENTIFIER'][i]]
        found = False
        j = 0
        while j < len(records) and found == False:
            polygon = Polygon(subdivisions_sf.shape(j).points)
            print("STATION:", i, ",", "SUBDIVISION:", j)
            if polygon.contains(point):
                sub_data.append(records[j]['CSDUID'])
                sub_data.append(records[j]['CSDNAME'])
                sub_data.append(records[j]['PRUID'])
                sub_data.append(records[j]['PRNAME'])
                sub_data.append(records[j]['CDUID'])
                sub_data.append(records[j]['CDNAME'])
                found = True
            j += 1
        if j == len(records):
            print("STATION:", i, ",", "FINDING CLOSEST SUBDIVISION")
            distances = list()
            for k in range(len(subdivisions_sf)):
                polygon = Polygon(subdivisions_sf.shape(k).points)
                distances.append(point.distance(polygon))
            if min(distances) < 50:
                index = distances.index(min(distances))
                sub_data.append(records[index]['CSDUID'])
                sub_data.append(records[index]['CSDNAME'])
                sub_data.append(records[index]['PRUID'])
                sub_data.append(records[index]['PRNAME'])
                sub_data.append(records[index]['CDUID'])
                sub_data.append(records[index]['CDNAME'])
        data.append(sub_data)
    return pd.DataFrame(data, columns = col_names)
