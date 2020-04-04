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
import glob
import csv
from csv import reader
import sys
import numpy as np
import copy
import covid_structures as cs

start = timer()
now = datetime.now()
dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
print('Starting... (' + dt_string + ' Z)')

step_counter = 1
basepath = path.dirname(__file__)
datafile = path.abspath(path.join(basepath, \
	'../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'))

i = 0
for v in reader(open(datafile)):
	#print(i, v)
	if (i == 0): # header
		n_dates = len(v) - 4 # dates determined
		#for j in range(n_dates): print(v[j+4]) # example loop
	else:
		c = cs.Country.create(v[1], float(v[2]), float(v[3]))
		if (v[0] != ''):
			s = cs.Subdivision(v[0], float(v[2]), float(v[3]))
			print(s.name() + ', ' + c.name())
			c.addSub(s)
		else:
			print(c.name())
		#print('>>>' + str(c))
	i += 1
print('# Records: ' + str(i))

print('# Countries: ' + str(cs.Country.numCountries()))
i = 0
for c in cs.Country.all():
	#print(c)
	if (c.hasSubs()):
		for s in c.subs():
			#print('	' + str(s) + ' ' + str(s.level()))
			if (s.name() == c.name()):
				#print(str(c) + ' = ' + str(s))
			i += 1
	else:
		i += 1
print('# Records: ' + str(i))

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))
