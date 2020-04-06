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

class Error(Exception):
	"""Base class for exceptions in this module."""
	pass
	
class FormatError(Error):
	"""Exception raised for errors in the JHU CSSE formatting.
	
	Attributes:
		expression -- input expression in which the error occurred
		message -- explanation of the error
	"""
	
	def __init__(self, expression, message = ''):
		self.expression = expression
		self.message = messa

# this will ingest the JHU 'CONFIRMED' time series file into the data structure
def ingest_data_global():
	print('Ingesting Global Data...')
	temp = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'
	#temp = ''
	basepath = path.abspath(path.join(path.dirname(__file__), temp))
	print('  Directory: ' + basepath)
	filehash = {}
	#filehash['CONFIRMED'] = 'testdata_g.txt'
	filehash['CONFIRMED'] = 'time_series_covid19_confirmed_global.csv'
	filehash['DEATHS'] = 'time_series_covid19_deaths_global.csv'
	filehash['RECOVERED'] = 'time_series_covid19_recovered_global.csv'
	date_col = {}
	date_col['CONFIRMED'] = 4
	date_col['DEATHS'] = 4
	date_col['RECOVERED'] = 4
	n_row_max = 0
	n_dates = 0
	for k, (label, filename) in enumerate(filehash.items()):
		datafile = path.abspath(path.join(basepath, filename))
		print('  File: ' + filename)
		i = 0
		for v in reader(open(datafile)):
			#print(i, v)
			if (i == 0): # header row (first record)
				temp = len(v)-date_col[label] # number of dates determined
				if (n_dates == 0): n_dates = temp
				if (n_dates != temp): 
					raise FormatError('Unequal Date Ranges (T1)! (' + str(n_dates) + '!=' + str(temp) + ')')
				if (world.lenData() == 0): 
					print('  Data Length: ' + str(n_dates))
					date = v[date_col['CONFIRMED']] + '20'
					world.setDates(datetime.strptime(date, '%m/%d/%Y'), n_dates)
				else: 
					if (n_dates != world.lenData()):
						raise FormatError('Unequal Date Ranges (T2)! (' + str(n_dates) + '!=' + str(world.lenData()) + ')')
			else:
				c = world.areaFactory(v[1], float(v[2]), float(v[3])) # factory (get or create)
				c.a['adm1'] = v[1]
				data = np.zeros(n_dates, dtype = int) # gather data
				for j in range(n_dates): 
					data[j] = v[j+date_col[label]]
				# print(data)
				if (v[0] != ''):
					s = c.areaFactory(v[0], float(v[2]), float(v[3])) # factory (get or create)
					s.setData(label, data)
					s.a['adm1'] = v[1]
					s.a['adm2'] = v[0]
				else:
					if (v[1] != 'US'): # skip US because it will be handled in the national pull
						c.setData(label, data)
			i += 1
		n_rows = i-1
		n_row_max = max(n_row_max, n_rows)
		print('    # Rows (' + label + '): ' + str(n_rows))
		print('    # Countries (' + label + '): ' + str(world.numAreas()))
	return n_row_max

def ingest_data_national():
	print('Ingesting National Data...')
	temp = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'
	#temp = ''
	basepath = path.abspath(path.join(path.dirname(__file__), temp))
	print('  Directory: ' + basepath)
	filehash = {}
	#filehash['CONFIRMED'] = 'testdata_n.txt'
	filehash['CONFIRMED'] = 'time_series_covid19_confirmed_US.csv'
	filehash['DEATHS'] = 'time_series_covid19_deaths_US.csv'
	date_col = {}
	date_col['CONFIRMED'] = 11
	date_col['DEATHS'] = 12
	n_dates = 0
	for k, (label, filename) in enumerate(filehash.items()):
		datafile = path.abspath(path.join(basepath, filename))
		print('  File: ' + filename)
		i = 0
		for v in reader(open(datafile)):
			#print(i, v)
			if (i == 0): # header row (first record)
				temp = len(v)-date_col[label] # number of dates determined
				if (n_dates == 0): n_dates = temp
				if (n_dates != temp): 
					raise FormatError('Unequal Date Ranges (T3)! (' + str(n_dates) + '!=' + str(temp) + ')')
				if (world.lenData() == 0): 
					world.setLenData(n_dates)
				else: 
					if (n_dates != world.lenData()):
						raise FormatError('Unequal Date Ranges (T4)! (' + str(n_dates) + '!=' + str(world.lenData()) + ')')
			else:
				c = world.areaFactory(v[7], float(v[8]), float(v[9])) # factory (get or create)
				c.a['adm1'] = v[7] # 'US'
				data = np.zeros(n_dates, dtype = int) # gather data
				for j in range(n_dates): 
					data[j] = v[j+date_col[label]]
				# print(data)
				if (v[6] == ''):
					raise FormatError('Expected US ADM2! (Line ' + str(i+1) + ')')
				s = c.areaFactory(v[6], float(v[8]), float(v[9])) # factory (get or create)
				s.a['adm1'] = v[7] # 'US'
				s.a['adm2'] = v[6]
				if (v[5] == ''): # state with no counties, e.g. PR, VI, GU, AS
					s.setData(label, data)
				else: # county or ADM3
					s = s.areaFactory(v[5], float(v[8]), float(v[9])) # factory (get or create)
					s.setData(label, data)
					s.a['adm1'] = v[7] # 'US'
					s.a['adm2'] = v[6]
					s.a['adm3'] = v[5]
				s.a['fips'] = v[4].replace('.0','')
			i += 1
		n_rows = i-1
		print('    # Rows (' + label + '): ' + str(n_rows))
		print('    # Countries (' + label + '): ' + str(world.numAreas()))
	return n_rows

def check_data_global(n_rows):
	print('Checking Data...')
	i = 0
	for c in world.areas():
		if (c.hasAreas() and c.hasData('CONFIRMED')):
			#print(str(c) + '***')
			i += 1
		#else:
			#print(str(c))
		if (c.name() != 'US' and c.hasAreas()):
			for s in c.areas():
				#print('	' + str(s))
				#if (s.name() == c.name()):
				#	print(str(c) + ' = ' + str(s))
				i += 1
		else:
			i += 1
	if (i == n_rows):
		print('  # Rows (Structure Check): ' + str(i) + ' (PASS)')
	else:
		print('  # Rows (Structure Check): ' + str(i) + ' (FAIL)')
		sys.exit(3)

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	# ingest data
	world = cs.World() # root object for data hierarchy
	try:
		n_rows = ingest_data_global() # ingest the latest global time series data
		check_data_global(n_rows) # check data structure
		ingest_data_national() # ingest the latest US time series data
		# will refresh and cascade subtotals
		for label in ['CONFIRMED', 'DEATHS', 'RECOVERED']:
			world.getData(label, True)
	except FormatError:
		print('Ingestion Problems...  Halting.')
		sys.exit(1)
	
	# do something
	filename = path.abspath(path.join(path.dirname(__file__), '..', 'data', 'cleaned.txt'))
	world.export(filename)
	
	# c = world.getArea('US')
	# data = c.getData('CONFIRMED')
	# print('\nTOTAL:\n', data)
	# data = c.getData('DEATHS')
	# print('\nTOTAL:\n', data)
	
	# data = world.getData('CONFIRMED')
	# print('\nTOTAL:\n', data)
	# data = world.getData('DEATHS')
	# print('\nTOTAL:\n', data)
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
