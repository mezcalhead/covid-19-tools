<h2>COVID-19 Tools Project</h2>

This site and code's purpose is to assist with data analysis tools and scripts on the JHU SSE Covid feed.  The code is NumPy/SciPy friendly so that the data is ready to go for performant analysis.  We credit Johns Hopkins for their data to make our project possible.  Other data sets may be added at a later time.<br>

The <b>code</b> directory has the core python code, classes, and utilities.<br>
The <b>data</b> directory is where output files are placed, as well as reference files.<br>
Large data files are here: https://www.dropbox.com/sh/7z001yfzyjqtrsw/AADa9eTqTSZjozcLgjtQVV-Da?dl=0<br>
<b>See README.md in the data directory for more information about the data files.</b>

2 lines of code ingests the JHU data while performing some basic cleanups:

```python
import covid_tools as ct
world = ct.ingestData('some-path-to-JHU-CSSE-dir')
```
Or take advantage of our nightly serialized world object, so your data initializes blazingly fast. You don't need to sync directly with JHU's GitHub leveraging our serialized cache!

```python
import covid_tools as ct
world = ct.fetchWorld()
```
 
![image](https://user-images.githubusercontent.com/3859765/79037459-3ce6da00-7b9f-11ea-9a20-e96a9dc5de82.png)

Below is a simple code example that reports on the US confirmed cases and deaths, iterates all the countries, then iterates all the counties in VA.  All geographic hierarchies descend from the base class 'Area' in covid-structures.py:

```python
import covid_tools as ct
from datetime import datetime
import os
from os import listdir, path
from os.path import isfile, join

# this populates the world hierarchy
basepath = path.abspath(path.join(path.dirname(__file__), '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'))
world = ct.ingestData(basepath)

# get the US
c = world.getArea('US')
data = c.getData('CONFIRMED')
print('US TOTAL CASES:\n', data)
data = c.getData('DEATHS')
print('US TOTAL DEATHS:\n', data)

# iterate
for c in world.areas():
  print(c.name())
 
# iterate VA counties
for area in c.getArea('Virginia').areas():
  data = area.getData('DEATHS')
  print(area.name() + ' has ' + data[-1] + ' deaths as of ' + area.world.getDates()[-1].strftime('%m/%d/%Y') + '...')
```

There are also some basic plotting functions such as this.  Just give it an area (a county, nation, state, etc...):

```python
ct.simplePlot(area, 'some title', filename, 20, xaxis = 'Days')
```

Here's a loop to plot several US states and countries in a single multiPlot trend.  We use the set {} hash to store the mix of areas we identified and sent to the multiPlot function calls - one for confirmed cases and one for deaths - after those areas relatively crossed a threshhold of 10 cases and 10 deaths.

![image](https://user-images.githubusercontent.com/3859765/79036481-a0b8d500-7b96-11ea-90b9-3f2747973fb7.png)

Here's the code snipplet for the above image:

```python
# plot individual areas
set = {}
v_thresh = 10 # threshhold for starting particular plots

set = {}
for key in ['US', 'Italy', 'Germany', 'United Kingdom']:
  area = world.getArea(key)
  set[area.name()] = area
for key in ['New York', 'New Jersey', 'Michigan', 'Louisiana']:
  area = world.getArea('US').getArea(key)
  set[area.name()] = area

filename = path.abspath(path.join(basepath, 'multiplot_mix_c.png'))
ct.multiPlot(set, 'CONFIRMED', 'Confirmed', filename, v_thresh, \
  xaxis='Days (since ' + str(v_thresh) + '+ cases) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])
filename = path.abspath(path.join(basepath, 'multiplot_mix_d.png'))
ct.multiPlot(set, 'DEATHS', 'Deaths', filename, v_thresh, \
  axis='Days (since ' + str(v_thresh) + '+ deaths) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))
```

![image](https://user-images.githubusercontent.com/3859765/79036463-79620800-7b96-11ea-8d02-ddc6de2aa4d7.png)

Here is the code snipplet for the above image:

```python
# plot individual areas
set = {}
sort_set = {}
v_thresh = 20 # threshhold for starting particular plots

for area in world.areas():
  # delete if exists - not necessary but can be useful
  filename = path.abspath(path.join(basepath, area.a['name'].replace(' ','_').replace(',','') + '.png'))
  if os.path.isfile(filename):
    os.remove(filename)
  # filter out more affected areas
  if max(area.getData('CONFIRMED')) > 1000:
    set[area.name()] = area
    sort_set[area.name()] = int(area.getData('CONFIRMED')[-1]) # last value
    xaxis_label = 'Days (since ' + str(v_thresh) + '+ occurences) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y')
    print('Plotting ' + area.name() + '...')
    ct.simplePlot(area, area.a['name'], filename, v_thresh, xaxis = xaxis_label)

# work with the top 30 subset
print('++++++++++++++++++++++++++++++++++++++++++++')
bag = {}
i = 0
for k, v in sorted(sort_set.items(), key = lambda kv:(kv[1], kv[0]), reverse = True):
  print(k, v)
  bag[k] = set[k]
  i += 1
  if (i > 30): break

# plot top 30 subset
print('++++++++++++++++++++++++++++++++++++++++++++')
filename = path.abspath(path.join(basepath, 'multiplot_g_c.png'))
ct.multiPlot(bag, 'CONFIRMED', 'Confirmed', filename, v_thresh, \
  xaxis='Days (since ' + str(v_thresh) + '+ cases) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), in_h = 8)
filename = path.abspath(path.join(basepath, 'multiplot_g_d.png'))
ct.multiPlot(bag, 'DEATHS', 'Deaths', filename, v_thresh, \
  xaxis='Days (since ' + str(v_thresh) + '+ deaths) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), in_h = 10, in_w = 6.5)
```

This project has been generously sponsored, in part, by Culmen International (www.culmen.com).

![image](https://user-images.githubusercontent.com/3859765/79036532-03aa6c00-7b97-11ea-947a-72fa3008a4c5.png)
