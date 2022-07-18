# -*- coding: utf-8 -*-
"""
This script pulls daily updates of temperatures and precipitation data from all 
operational Canadian weather stations, generates average climate variables by 
Census subdivision, then generates weighted 2016 Census divisions averages by 
Census subdivision population estimates to create a daily Census division 
climate variables data set. 

Author:       Minnie Cui
Date written: 20 April 2021
Last updated: 18 July 2022
"""
###############################################################################
# DEFINE REQUIRED VARIABLES

# Project directory
directory = "C:/Users/minni/Research/COVID_CAN/Canada_Daily_Climate/DATA"

# Census subdivisions file (acquired from StatsCan)
census_sd = "census_subdivisions"

# Census subdivisions population estimates file (created by cleanPop.do)
pop_sd = "subdivisions_pop"

# Operational weather stations geo-data (as of July 18, 2022)
stations_file = "climate_station_list.csv"

###############################################################################
# IMPORT REQUIRED PACKAGES
import os
import pandas as pd
from datetime import date
from functions import getSD
import shapefile as sf

# CHANGE PROJECT DIRECTORY
os.chdir(directory)
print("\nProject directory successfully set to: " + directory)

###############################################################################
# PULL TODAY'S DATA
print("\nGetting latest climate data...")

# Generate today's date and first day to pull variables
#today = date(2021, 12, 31)
today = date.today()
this_year = today.year
start = date(this_year, 1, 1)
todayfile = "daily_climate_" + str(start) + "_to_" + str(today) + ".csv"
outputfile_cd = "daily_cd_climate_" + str(this_year) + ".csv"
outputfile_sd = "daily_csd_climate_" + str(this_year) + ".csv"

# Remove old master data if in daily_climate folder
if len(os.listdir("./daily_climate")) != 0 and todayfile not in os.listdir("./daily_climate"):
    for file in os.listdir("./daily_climate"):
        if "daily_climate_" + str(this_year) in file:
            remove_file = file
            os.remove("./daily_climate/" + remove_file)

# Update master data with today's data if it hasn't been pulled already
if todayfile not in os.listdir("./daily_climate"):
    url = "https://api.weather.gc.ca/collections/climate-daily/items?datetime=" + str(start) + "%2000:00:00/" + str(today) + "%2000:00:00&sortby=PROVINCE_CODE,CLIMATE_IDENTIFIER,LOCAL_DATE&f=csv&limit=500000&startindex=0"
    master = pd.read_csv(url, parse_dates = ["LOCAL_DATE"], dtype = str)
        
    # Save new master to directory
    master.to_csv("./daily_climate/" + todayfile, index = False) 
    print("\nRaw daily climate data has been updated in folder.")
else:
    master = pd.read_csv("./daily_climate/" + todayfile, parse_dates = ["LOCAL_DATE"], dtype = str)
    print("\nToday's climate data update is already in folder.")

# Change variable type for columns that are float or int
float_cols = [v for v in master if "_FLAG" not in v]
int_cols = ["LOCAL_YEAR", "LOCAL_MONTH", "LOCAL_DAY"]
for v in ["CLIMATE_IDENTIFIER", "STATION_NAME", "PROVINCE_CODE", "LOCAL_DATE", "ID"] + int_cols:
    float_cols.remove(v)
dtypes = {}
for v in float_cols:
    dtypes[v] = float
for v in int_cols:
    dtypes[v] = int
for col, col_type in dtypes.items():
    master[col] = master[col].astype(col_type)
    
# Ask user if want to update file with 
update_sd = input("Do you want to update the operational weather stations merge with Census subdivisions? (y/n) \n")

# Read in subdivisions shapefile data
subdivisions = sf.Reader("./" + census_sd + "/" + census_sd, encoding="latin1")
records = subdivisions.records()
print("\nSubdivisions boundary data loaded.")

# If user says yes, then update
if update_sd.lower() == 'y':
    #url_sts = "https://dd.weather.gc.ca/climate/observations/" + stations_file
    #stations = pd.read_csv(url_sts)
    #stations = pd.read_csv("./stations/" + stations_file)
    #stations = stations.rename(columns={'Longitude': 'x', 'Latitude': 'y', 'Climate ID': 'CLIMATE_IDENTIFIER'})
    #stations_sd = getSD(stations, subdivisions).drop_duplicates()
    stations_sd = getSD(master, subdivisions).drop_duplicates()
    stations_sd.reset_index(drop=True, inplace=True)
    stations_sd.to_csv("./stations/stations_sd.csv", index = False)

# If user says no, then read in file stations_sd.csv (i.e. historical file)
elif update_sd.lower() == 'n':
    stations_sd = pd.read_csv("./stations/stations_sd.csv").drop_duplicates()
    stations_sd.reset_index(drop=True, inplace=True)

# Merge today's climate data with stations_sd.csv
master_sd = master.merge(stations_sd, on=['CLIMATE_IDENTIFIER'], how='left')
master_sd = master_sd.rename(columns={'PROVINCE_CODE': 'PRCODE'})
print("\nClimate variables merged with Census subdivisions!")
print("Merged data has", str(len(master_sd[master_sd['CSDUID'].isnull()].copy())), "missing values.")

###############################################################################
# GENERATE AVERAGE CLIMATE VARIABLES BY SUBDIVISION
print("\nGetting subdivisions climate variable averages...")

# List of variables to take the mean of
climate_cols = ['MEAN_TEMPERATURE','MIN_TEMPERATURE','MAX_TEMPERATURE',
                'TOTAL_PRECIPITATION','TOTAL_RAIN','TOTAL_SNOW',
                'SNOW_ON_GROUND','DIRECTION_MAX_GUST','SPEED_MAX_GUST',
                'MIN_REL_HUMIDITY','MAX_REL_HUMIDITY']

# List of variables to by which to take the mean
sd_cols = ['PRUID','PRNAME','PRCODE','CDUID','CDNAME','CSDUID','CSDNAME',
              'LOCAL_DATE','LOCAL_YEAR','LOCAL_MONTH','LOCAL_DAY']

# Generate subdivisions climate averages data 
df_sd = master_sd.groupby(sd_cols, as_index = False)[climate_cols].mean()
print("\nSubdivisions averages dataset complete.")

# Change ID variable types to int
dtypes = {'CSDUID': int,
          'CDUID': int,
          'PRUID': int}
for col, col_type in dtypes.items():
    #print(col in list(df_sd))
    df_sd[col] = df_sd[col].astype(col_type)

###############################################################################
# GENERATE AVERAGE CLIMATE VARIABLES BY CENSUS DIVISION, WEIGHTED BY SUBDIVISION POPULATION
print("\nGetting divisions averages, weighted by subdivision population...")

# Read in subdivisions annual population estimates data
pop = pd.read_csv("./" + pop_sd + "/" + pop_sd + ".csv")

# Merge subdivision averages with subdivision population estimates
df_pop = df_sd.merge(pop, on = ['CSDUID', 'LOCAL_YEAR'], how = 'left')
print("\nSubdivisions averages dataset successfully merged with subdivisions population estimates.")
print("Merged data has", str(len(df_pop[df_pop['POP'].isnull()].copy())), "missing values.")

# Replace population with 1 for observations where population is 0
df_pop['POP'] = df_pop['POP'].replace(0, 1)

# Save subdivision file
df_pop = df_pop.sort_values(by = ['CSDUID', 'LOCAL_DATE'], ignore_index = True)
df_pop.to_csv("../" + outputfile_sd, index = False)
print("\nFinal subdivisions averages dataset successfully saved.")

# List of variables to by which to take the mean
cd_cols = ['PRUID','PRNAME','PRCODE','CDUID','CDNAME','LOCAL_DATE',
           'LOCAL_YEAR','LOCAL_MONTH','LOCAL_DAY']

# Ask if user wants to generate Census divisions weighted average data set
cont = input("Generate Census division weighted averages? (y/n) \n")

# If user says yes, generate divisions climate weighted averages data
if cont.lower() == 'y':
    cd_vars = list()
    for data_col in climate_cols:
        df_pop[data_col + '_timesweight'] = df_pop[data_col]*df_pop['POP']
        df_pop[data_col + '_weight'] = df_pop['POP']*pd.notnull(df_pop[data_col])
        cd_vars.append(data_col + '_timesweight')
        cd_vars.append(data_col + '_weight')
    df_cd = df_pop.groupby(cd_cols, as_index = False)[cd_vars].sum()
    for data_col in climate_cols:
        df_cd[data_col] = df_cd[data_col + '_timesweight'] / df_cd[data_col + '_weight']
    df_cd_final = df_cd[(cd_cols + climate_cols)]
    print("\nDivisions averages dataset complete.")

    # Save data set
    df_cd_final = df_cd_final.sort_values(by = ['CDUID', 'LOCAL_DATE'], ignore_index = True)
    df_cd_final.to_csv("../" + outputfile_cd, index = False)
    print("\nFinal divisions averages dataset successfully saved.")
    print("\nEnd of code.")

# If user says no, end code
else:
    print("\nEnd of code.")

