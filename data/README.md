<h1>data_standard.txt</h1>

![image](https://user-images.githubusercontent.com/3859765/79300208-0f0dd800-7eb4-11ea-9ea1-79261aee3317.png)

...

Column 'T' is a Type Column:  C = Confirmed Case Count; D = Deaths; R = Recovered<br>
Areas are in hierarchical format:  ADM1 -> ADM2 -> ADM3<br>
Column 'Key' is a good unique hash Column<br>
FIPS is the US County FIPS code if applicable<br>
Date Columns extend to the Right<br>

<h1>data_transposed.txt</h1>

Now here: https://www.dropbox.com/sh/7z001yfzyjqtrsw/AADa9eTqTSZjozcLgjtQVV-Da?dl=0

![image](https://user-images.githubusercontent.com/3859765/79300322-5bf1ae80-7eb4-11ea-84fa-2dac336606fd.png)

...

Columns Confirmed, Deaths, and Recovered exist for each date.<br>
Areas are in hierarchical format:  ADM1 -> ADM2 -> ADM3<br>
Column 'Key'+'Date' combined is a good unique hash Column<br>
FIPS is the US County FIPS code if applicable<br>
Date Columns extend to the Bottom<br>

<h1>data_covid.shp</h1>

ESRI Shapefile Format version of Data_Standard.txt which is now here:

https://www.dropbox.com/sh/7z001yfzyjqtrsw/AADa9eTqTSZjozcLgjtQVV-Da?dl=0

<h1>Supplemental Data</h1>

For additional data, click here:

https://www.dropbox.com/sh/7z001yfzyjqtrsw/AADa9eTqTSZjozcLgjtQVV-Da?dl=0

In that folder, the following exists:

a) US Census Bureau US Counties - 'us_counties.*' - Shapefile Format (140MB; 2017; latest release)
   with appended data from 'county_data.csv' described in 'metadata.txt'
b) Appended US Census Bureau Data - 'metadata.txt' - Directory
c) NAICS Codes Reference - 'naics.txt'
d) US Census Bureau ACS Codes Reference - 'codes.txt'
e) US Census Bureau County Business Patterns - 'business_patterns.txt'

![image](https://user-images.githubusercontent.com/3859765/79300023-8e4edc00-7eb3-11ea-9eb5-bbbf8f6958aa.png)

For more information on some of the data, use these links:

# 2017 Economic Annual Surveys: Business Patterns: County Business Patterns
https://api.census.gov/data/2017/cbp/examples.html
https://api.census.gov/data/2017/cbp/variables.html

# 2018 Small Area Income and Poverty Estimates: Small Area Income and Poverty Estimates
https://api.census.gov/data/timeseries/poverty/saipe/examples.html
https://api.census.gov/data/timeseries/poverty/saipe/variables.html

# 2018 ACS 5-Year Subject Tables
https://api.census.gov/data/2018/acs/acs5/subject/examples.html
https://api.census.gov/data/2018/acs/acs5/subject/variables.html
