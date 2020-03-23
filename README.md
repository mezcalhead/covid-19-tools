# covid-19-tracker
COVID-19 Tracker at County Level

The goal of this project is to unify the reporting of the 52 'states' (counting DC and PR) into a structured unified view at the county level.  At a future time, zip code (ZCTA) could be addressed.

For speed and simplicity, the project will utilize an AirTable (www.airtable.com) repository that has been created and sponsored by Culmen International (www.culmen.com).  Registered developers will inject data into the airtable repository using the AirTable API.

Public access will be via this link: https://airtable.com/shrdzCswX95pa42qb

The format of the primary table will be:

Field Name | Type | Description
LID | String | Primary Key that is the Log ID (format described below)
Date | Date | MM/DD/YYYY format representing the date of the statistic
State | String | The State name
County | String | The County name
Cases | Int | The # of confirmed open cases
Recovered | Int | The # of confirmed recovered cases
Deaths | Int | The # of confirmed reported deaths
Contributer | String | The registered AirTable contributor
Source Name | String | The source name (e.g. VA Dept of Health)
SID | Int | Foreign Key to the Sources table representing a Source ID
CID | Int | Foreign Key to the County table representing a County ID (format is [State FIPS] + '_' + [County Fips])
Notes | Text | Additional Notes about the Entry

