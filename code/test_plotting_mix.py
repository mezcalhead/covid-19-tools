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
	if not os.path.exists(basepath):
		os.makedirs(basepath)
	
	# plot individual areas
	set = {}
	v_thresh = 10 # threshhold for starting particular plots (# cases, # deaths)
	
	set = {}
	for key in ['US', 'Italy', 'Germany', 'United Kingdom']:
		area = world.getArea(key)
		set[area.key()] = area
	for key in ['New York', 'New Jersey', 'Michigan', 'Louisiana']:
		area = world.getArea('US').getArea(key)
		set[area.key()] = area
	
	print('Plotting...')
	print('++++++++++++++++++++++++++++++++++++++++++++')
	filename = path.abspath(path.join(basepath, 'multiplot_m_c.png'))
	ct.multiPlot(set, 'Confirmed', filename, 'CONFIRMED', v_thresh)
	filename = path.abspath(path.join(basepath, 'multiplot_m_d.png'))
	ct.multiPlot(set, 'Deaths', filename, 'DEATHS', v_thresh, overlay=['avg'])
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
