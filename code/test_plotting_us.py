#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Plotting the top 10 states...
#
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer

import os
from os import listdir, path
from os.path import isfile, join
import numpy as np
import sys

import covid_structures as cs
import covid_tools as ct
import covid_models as cm

def dictionary(): 
	key_value ={}
	key_value[2] = 56
	key_value[1] = 2
	key_value[5] = 12
	key_value[4] = 24
	key_value[6] = 18
	key_value[3] = 323
	print(sorted(key_value.items(), key = lambda kv:(kv[1], kv[0])))

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	# ingest (assumes JHU's COVID-19 is installed under the root directory as COVID-19-TOOLS)
	basepath = path.abspath(path.join(path.dirname(__file__), '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'))
	world = ct.ingestData(basepath)
	
	print('++++++++++++++++++++++++++++++++++++++++++++')
	
	basepath = path.abspath(path.join(path.dirname(__file__), '..', 'tmp',))
	if not os.path.exists(basepath):
		os.makedirs(basepath)
	
	# plot individual areas
	set = {}
	sort_set = {}
	v_thresh = 20 # threshhold for starting particular plots
	
	c = world.getArea('US')
	for area in c.areas():
		# delete if exists - not necessary but can be useful
		filename = path.abspath(path.join(basepath, area.a['name'].replace(' ','_').replace(',','') + '.png'))
		if os.path.isfile(filename):
			os.remove(filename)
		# filter out more affected areas
		if max(area.getData('CONFIRMED')) > 5000:
			set[area.name()] = area
			sort_set[area.name()] = int(area.getData('CONFIRMED')[-1]) # last value
			xaxis_label = 'Days (since ' + str(v_thresh) + '+ occurences) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y')
			ct.simplePlot(area, area.a['name'], filename, v_thresh, xaxis = xaxis_label)
	
	# work with the top 10 subset
	bag = {}
	i = 0
	for k, v in sorted(sort_set.items(), key = lambda kv:(kv[1], kv[0]), reverse = True):
		print(k, v)
		bag[k] = set[k]
		i += 1
		if (i > 10): break
	
	# plot top 10 subset
	print('++++++++++++++++++++++++++++++++++++++++++++')
	filename = path.abspath(path.join(basepath, 'multiplot_us_c.png'))
	ct.multiPlot(bag, 'CONFIRMED', 'Confirmed', filename, v_thresh, \
		xaxis='Days (since ' + str(v_thresh) + '+ cases) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])
	filename = path.abspath(path.join(basepath, 'multiplot_us_d.png'))
	ct.multiPlot(bag, 'DEATHS', 'Deaths', filename, v_thresh, \
		xaxis='Days (since ' + str(v_thresh) + '+ deaths) thru ' + area.world.getDates()[-1].strftime('%m/%d/%Y'), overlay=['avg'])
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
