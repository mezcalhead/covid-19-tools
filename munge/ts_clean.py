#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: cleans the output from ts_merge.py by fixing historical US county entries and interpolating missing data
#
from datetime import datetime
from timeit import default_timer as timer
from os import listdir, path
from os.path import isfile, join
import glob
from csv import reader

start = timer()
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print('Starting... (' + dt_string + ' Z)')

basepath = path.dirname(__file__)
datafile = path.abspath(path.join(basepath, '..', 'data', 'data_merged.csv'))
n_obs = 0 # observations

ln = 0 # line number
for line in reader(open(datafile)):
	ln += 1
	if (ln > 1):
		# do something
		# hash US county info for cleanup later
		# TODO
		n_obs += 1

print("# obs before: " + str(n_obs))

# 1st pass - fix county references
# TODO

# 2nd pass - interpolation
# TODO

print("# obs after: " + str(n_obs))

fileout = path.abspath(path.join(basepath, '..', 'data', 'data_cleaned.csv'))
fileout = open(fileout,'w')
fileout.write('OBS|FIPS|ADM3|ADM2|ADM1|LASTUPDATED|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|LABEL|INTER\n')
# do something
fileout.close()

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))