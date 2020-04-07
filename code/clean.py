#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Import JHU CSSE's Time Series Data Files, Merge, Normalize, and Prepare
#
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer
from os import listdir, path
from os.path import isfile, join

import covid_structures as cs
import covid_tools as ct

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	# export both types
	basepath = path.abspath(path.join(path.dirname(__file__), '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'))
	world = ct.ingestData(basepath)
	world.exportStandard(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'cleaned_standard.txt')))
	world.exportTransposed(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'cleaned_transposed.txt')))
	
	print('============================================')
	print('US')
	c = world.getArea('US')
	data = c.getData('CONFIRMED')
	print('\nTOTAL:\n', data)
	data = c.getData('DEATHS')
	print('\nTOTAL:\n', data)
	
	print('============================================')
	print('World')
	data = world.getData('CONFIRMED')
	print('\nTOTAL:\n', data)
	data = world.getData('DEATHS')
	print('\nTOTAL:\n', data)
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
