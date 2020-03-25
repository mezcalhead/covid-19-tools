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
import csv
from csv import reader

start = timer()
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print('Starting... (' + dt_string + ' Z)')

basepath = path.dirname(__file__)
datafile = path.abspath(path.join(basepath, '..', 'data', 'data_merged.txt'))
n_obs = 0 # observations

#OBS|FIPS|ADM3|ADM2|ADM1|LASTUPDATED|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|LABEL
#1|N/A|N/A|Anhui|Mainland China|2020-01-22 17:00:00|0.0|0.0|1|0|0|-1|Anhui, Mainland China
#2|N/A|N/A|Beijing|Mainland China|2020-01-22 17:00:00|0.0|0.0|14|0|0|-1|Beijing, Mainland China

# load state abbreviations reference
state2abbr = {}
abbr2state = {}
stateabbr = path.abspath(path.join(basepath, '..', 'data', 'states.csv'))
for line in reader(open(stateabbr)):
	state2abbr[line[0]] = line[1]
	abbr2state[line[1]] = line[0]

geohash = {} # labels that reference lat/lon
hash = {} # labels that reference the entire line
geo_consistent = 0 # curious if for same labels, geopoint is consistent
geo_inconsistent = 0 # curious if for same lables, geopoint changes
geo_fix = 0 # number of zero lat/lons that need fixing
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
ln = 0 # line number
with open(datafile, "r") as csvfile:
	for line in csv.DictReader(csvfile, dialect='piper'):
		ln += 1
		if (ln > 1):
			# do something
			key = None
			# hash US county info for cleanup later
			#
			# { Elko County, Walla Walla County } wierd condition
			if (line['ADM3'].find('County') > 0):
				# print(line['ADM3'] + '-' + line['ADM2'])
				line['ADM3'] = line['ADM3'].replace('County', '').strip()
				key = line['ADM3'] + ', ' + line['ADM2'] + ', US'
			if (line['ADM2'].find('County') > 0):
				# print(line['ADM2'])
				tok = line['ADM2'].split(',')
				key = tok[0].replace('County', '').strip() + ', ' + abbr2state[tok[1].strip()] + ', US'
			if (key == None):
				# TODO: decide on approach
				key = line['LABEL']
			# set hash
			# print(key)
			keyterm = line['LASTUPDATED'] + '_' + key
			#if (hash.get(keyterm) != None):
			#	print(keyterm)
			#	print("  B: " + str(hash.get(keyterm)))
			#	print("  A: " + str(line))
			if (float(line['LAT']) != 0 and float(line['LON']) != 0):
				if (geohash.get(key) == None):
					geohash[key] = [line['LAT'], line['LON']]
				else:
					temp = geohash.get(key)
					if (float(temp[0]) == float(line['LAT']) and float(temp[1]) == float(line['LON'])):
						geo_consistent += 1
					else:
						geo_inconsistent += 1
						#print(key + '>' + str(float(temp[0])) + ',' + str(float(line['LAT'])) + '  ' + str(float(temp[1])) + \
						#',' + str(float(line['LON'])))
						# note this strategy will overwrite and we could assume most recent is most accurate, which will 
						# adjust geo_consistent/geo_inconsistent counts going forward
						geohash[key] = [line['LAT'], line['LON']]
			else:
				geo_fix += 1
			hash[keyterm] = line
			n_obs += 1

print("# obs before: " + str(n_obs))
print("# obs intermediate: " + str(len(hash)))
print("# dupes removed: " + str(n_obs-len(hash)))
print()
print("# geohash's: " + str(len(geohash)))
print("# geo_consistent: " + str(geo_consistent))
print("# geo_inconsistent: " + str(geo_inconsistent))
print("# geo_fix: " + str(geo_fix))
print()

# fix lat/lons if we find entries in the geohash -> EASY
# we'll assume the more recent keys are more accurate, since they are the latest updates
geo_fixed = 0
geo_cannot_fix = 0
for i, (key, v) in enumerate(hash.items()):
	#print(key.split('_')[1], v['LAT'], v['LON'])
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[1])
		if (temp != None):
			v['LAT'] = temp[0]
			v['LON'] = temp[1]
			geo_fixed += 1
		else:
			geo_cannot_fix += 1
print("# geo_fixed: " + str(geo_fixed))
print("# geo_cannot_fix: " + str(geo_cannot_fix))
print("# TOTAL: " + str(geo_fixed + geo_cannot_fix))
print()

# 2nd pass - WRITE OUT THOSE THAT NEED FIXED
flag = {} # only want to write once per unique key
fileout = path.abspath(path.join(basepath, '..', 'data', 'geo_issues.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|POBS|LASTUPDATED|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE\n')
for i, (key, v) in enumerate(hash.items()):
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[1])
		if (temp == None and flag.get(key.split('_')[1]) == None):
			v.get(key)
			flag[key.split('_')[1]] = True
			line = v['OBS'] + '|' + v['LASTUPDATED'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + \
			v['ADM2'] + '|' + v['ADM1'] + '|' + v['LAT'] + '|' + v['LON'] + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
			v['ACTIVE']
			#print(line)
			fileout.write(line + '\n')
fileout.close()

# 1st pass - fix county references
#for i, (key, v) in enumerate(hash.items()):
#	print(v)

# 2nd pass - interpolation
# TODO
for key in sorted(hash.keys()):
	v = hash.get(key)
	v['INTER'] = 'N'

print("# obs after: " + str(len(hash)))

fileout = path.abspath(path.join(basepath, '..', 'data', 'data_cleaned.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|POBS|LASTUPDATED|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|INTER\n')
obs = 1
for key in sorted(hash.keys()):
	v = hash.get(key)
	line = str(obs) + '|' + v['OBS'] + '|' + v['LASTUPDATED'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + \
	v['ADM2'] + '|' + v['ADM1'] + '|' + v['LAT'] + '|' + v['LON'] + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
	v['ACTIVE'] + '|' + v['INTER']
	#print(line)
	fileout.write(line + '\n')
	obs += 1
fileout.close()

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))