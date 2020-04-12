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

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	world = ct.fetchWorld()
	
	basepath = path.abspath(path.join(path.dirname(__file__), '..', 'tmp',))
	if not os.path.exists(basepath): os.makedirs(basepath)
	
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
			set[area.key()] = area
			sort_set[area.key()] = int(area.getData('CONFIRMED')[-1]) # last value
			print('Plotting ' + area.name() + '...')
			ct.simplePlot(area, area.a['name'], filename, v_thresh)
	
	# work with the top 10 subset
	print('++++++++++++++++++++++++++++++++++++++++++++')
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
	ct.multiPlot(bag, 'Confirmed', filename, 'CONFIRMED', v_thresh)
	filename = path.abspath(path.join(basepath, 'multiplot_us_d.png'))
	ct.multiPlot(bag, 'Deaths', filename, 'DEATHS', v_thresh, overlay=['avg'])
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
