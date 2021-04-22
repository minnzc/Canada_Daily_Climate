## Canada average climate conditions by Census subdivisions and Census divisions data sets

Climate conditions variables are recorded daily with a 2-3 day lag by weather stations. I take the mean of all non-null weather stations climate variable readings contained within a Census subdivision. Then, I take the weighted mean of all Census subdivisions with non-null climate variable values within a Census division. Weights are frequency weights using 2018-2020 Census subdivision population estimates. 2020 population estimates are used for weighing 2021 climate variables. Null values means no readings are recorded from weather stations.

Data is being updated every Monday.

## Final data sets

- **Census subdivisions data set**: daily_sd_climate_YYYY.csv
- **Census divisions data set**:    daily_cd_climate_YYYY.csv

## Variables

- **PRUID**: 2-digit Province code
- **PRNAME**: Province name
- **PRCODE**: 2-letter Province code
- **CDUID**: 4-digit Census division code (2-digit province code and 2-digit unique Census division code)
- **CDNAME**: Census division name
- **CSDUID**: 7-digit Census subdivisions code (2-digit province code, 2-digit Census division code, 3-digit Census subdivision code)
- **CSDNAME**: Census subdivision name
- **LOCAL_DATE**: date formatted YYYY-MM-DD
- **LOCAL_YEAR**: year, integer 2018 to 2021
- **LOCAL_MONTH**: month, integer 1 to 12
- **LOCAL_DAY**: day, integer 1 to 31
- **MEAN_TEMPERATURE**: average temperature in degrees Celsius (°C)
- **MIN_TEMPERATURE**: average minimum temperature in degrees Celsius (°C)
- **MAX_TEMPERATURE**: average maximum temperature in degrees Celsius (°C)
- **TOTAL_PRECIPITATION**: average sum of the total rainfall and the water equivalent of the total snowfall in millimetres (mm)
- **TOTAL_RAIN**: average total rainfall, or amount of all liquid precipitation in millimetres (mm) such as rain, drizzle, freezing rain, and hail
- **TOTAL_SNOW**: average total total snowfall, or amount of frozen (solid) precipitation in centimetres (cm), such as snow and ice pellets
- **SNOW_ON_GROUND**: average depth of snow in centimetres (cm) on the ground
- **DIRECTION_MAX_GUST**: average direction of the maximum gust (true or geographic, not magnetic) from which the wind blows. Expressed in tens of degrees (10's deg), 9 means 90 degrees true or an east wind, and 36 means 360 degrees true or a wind blowing from the geographic North Pole. (NOTE: weather stations only report this value if the maximum gust speed for the day exceeds 29 km/h)
- **SPEED_MAX_GUST**: average speed in kilometres per hour (km/h) of the maximum wind gust during the day (NOTE: weather stations do not report if this value if less than 31 km/h)
- **MIN_REL_HUMIDITY**: average minimum relative humidity (%)
- **MAX_REL_HUMIDITY**: average maximum relative humidity (%)

## Data sources

- **Census divisions and subdivisions boundary data**: [https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-2016-eng.cfm](https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-2016-eng.cfm)
- **Daily climate conditions data**: [https://climate-change.canada.ca/climate-data/#/daily-climate-data](https://climate-change.canada.ca/climate-data/#/daily-climate-data)
- **Census subdivisions population estimates**: [https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710014201](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710014201)

## Analysis code

Key elements of the analysis code are as follows:
- **getCDAvgs.py**: a Python script run once daily to update climate contained in the DATA folder and calculate averages
- **functions.py**: a Python script containing all defined functions called upon by getCDAverages.py

## Contact
Minnie Cui
minniehcui@gmail.com
