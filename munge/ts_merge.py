#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: integrates all the JHU CSSE data files for each day into one consolidated file
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

# get list of files - assumes JHU repo is cloned to same parent directory
basepath = path.dirname(__file__)
datafile_dir = path.abspath(path.join(basepath, '..', '../COVID-19/csse_covid_19_data/csse_covid_19_daily_reports'))
print('Using datafile_dir: ' + datafile_dir)
datafile_list = glob.glob(datafile_dir + '/*.csv')

n_obs = 0 # observations
fileout = path.abspath(path.join(basepath, '..', 'data', 'data_merged.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|FIPS|ADM3|ADM2|ADM1|LASTUPDATED|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|LABEL\n')

# this function processes each line
def process(header_type, fips, adm3, adm2, adm1, ts, lat, lon, confirmed, deaths, recovered, active, label):
	global n_obs
	if (fips == None or fips == ''):
		fips = 'N/A'
	if (adm3 == None or adm3 == ''):
		adm3 = 'N/A'
	if (adm2 == None or adm2 == ''):
		adm2 = 'N/A'
	# timestamps change differently than the header_types, so far here are the types detected
	# '1/22/2020 17:00' (mostly header_type = 1)
	# '1/23/20 18:00' (some header_type = 1)
	# '2020-02-21T06:53:03' (some header_type = 1)
	# '2020-02-21T06:53:03' (mostly header_type = 2)
	# '2020-03-24 23:37:31' (mostly header_type = 3)
	if (header_type == 1):
		ts = ts.replace('/20 ','/2020 ') # some occurences
		try:
			datetime_object = datetime.strptime(ts, '%m/%d/%Y %H:%M')
		except ValueError:
			datetime_object = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
	elif (header_type == 2):
		datetime_object = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
	elif (header_type == 3):
		datetime_object = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
	if (lat == None):
		lat = 0
	if (lon == None):
		lon = 0
	lat = round(float(lat), 6)
	lon = round(float(lon), 6)
	if (confirmed == ''):
		confirmed = 0
	if (deaths == ''):
		deaths = 0
	if (recovered == ''):
		recovered = 0
	if (active == None or active == ''):
		active = -1
	if (label == None or label == ''):
		label = ''
		if (adm3 != 'N/A'):
			label = adm3
		if (adm2 != 'N/A'):
			if (label != ''):
				label = label + ", " + adm2
			else:
				label = adm2
		if (label == ''):
			label = adm1
		else:
			label = label + ", " + adm1
	n_obs += 1
	fileout.write(str(n_obs) + '|' + fips.strip() + '|' + adm3.strip() + '|' + adm2.strip() + '|' + adm1.strip() + '|' + \
		str(datetime_object) + '|' + str(lat).strip() + '|' + str(lon).strip() + '|' + str(confirmed) + '|' + str(deaths) + \
		'|' + str(recovered) + '|' + str(active) + '|' + label.strip() + '\n')

# iterate the files, reading them
n_files = 1 # number of files
for datafile in datafile_list:
	#print(datafile)
	ln = 0 # line number
	for line in reader(open(datafile)):
		ln += 1
		if (ln == 1):
			line[0] = line[0].replace('\ufeff','')
			#print(line)
			# determine header_type
			if (str(line) == "['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']"):
				header_type = 1
			elif (str(line) == "['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered', 'Latitude', 'Longitude']"):
				header_type = 2
			elif (str(line) == "['FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key']"):
				header_type = 3
			else:
				header_type = 0
				print('WARNING: Unrecognized header.  Skipping...')
		elif (header_type > 0):
			if (header_type == 1):
				process(header_type, None, None, line[0], line[1], line[2], None, None, line[3], line[4], line[5], None, None)
			elif (header_type == 2):
				process(header_type, None, None, line[0], line[1], line[2], line[6], line[7], line[3], line[4], line[5], None, None)
			elif (header_type == 3):
				process(header_type, line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11])
	# for line
	n_files += 1
	print('\t' + datafile + ' > ' + str(ln-1) + ' obs...')

fileout.close()
print("# files: " + str(n_files))
print("# obs: " + str(n_obs))

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))