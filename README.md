<h2>COVID-19 Tracker Tools Project</h2>

This site is public to assist with data analysis tools and scripts on the JHU SSE Covid feed.  The code is NumPy/SciPy friendly so that the data is ready to go for analysis.  We credit Johns Hopkins for their data to make our project possible.  Other data sets may be added at a later time.<br>

One line of code ingests the JHU data while performing some basic cleanups:

```python
world = ct.ingestData('some-path-to-JHU-CSSE-dir')
```

The <b>code</b> directory has the core python code, classes, and utilities.<br>

The <b>data</b> directory is where output files are placed, as well as reference files.<br>

Here is a simple code example:

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

There are also some simple plotting functions.

```python
ct.simplePlot(area, 'some title', filename, 20, xaxis = 'Days')
```

Here's a simple loop to print several states in the US after creating a SET and sending to multiPlot:

```python
	# plot individual areas
	set = {}
	v_thresh = 10 # threshhold for starting particular plots
	
	set = {}
	area = world.getArea('US')
	set[area.name()] = area
	area = world.getArea('Italy')
	set[area.name()] = area
	area = world.getArea('US').getArea('New York')
	set[area.name()] = area
	area = world.getArea('US').getArea('New Jersey')
	set[area.name()] = area
	area = world.getArea('US').getArea('Michigan')
	set[area.name()] = area
	area = world.getArea('US').getArea('Louisiana')
	set[area.name()] = area
	area = world.getArea('Germany')
	set[area.name()] = area
	area = world.getArea('United Kingdom')
	set[area.name()] = area
	
	filename = path.abspath(path.join(basepath, 'multiplot_mix_c.png'))
	ct.multiPlot(set, 'CONFIRMED', 'Confirmed', filename, v_thresh, \
		xaxis='Days (since ' + str(v_thresh) + '+ cases) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])
	filename = path.abspath(path.join(basepath, 'multiplot_mix_d.png'))
	ct.multiPlot(set, 'DEATHS', 'Deaths', filename, v_thresh, \
		xaxis='Days (since ' + str(v_thresh) + '+ deaths) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
```
