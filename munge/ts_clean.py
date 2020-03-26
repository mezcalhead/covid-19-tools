#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: cleans the output from ts_merge.py by fixing historical US county entries and interpolating missing data
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

start = timer()
now = datetime.now()
dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
print('Starting... (' + dt_string + ' Z)')

step_counter = 1
basepath = path.dirname(__file__)
datafile = path.abspath(path.join(basepath, '..', 'data', 'data_merged.txt'))
n_obs = 0 # observations

#OBS|FIPS|ADM3|ADM2|ADM1|LASTUPDATED|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|LABEL
#1|N/A|N/A|Anhui|Mainland China|01/22/2020|0.0|0.0|1|0|0|-1|Anhui, Mainland China
#2|N/A|N/A|Beijing|Mainland China|01/22/2020|0.0|0.0|14|0|0|-1|Beijing, Mainland China

# some reference files
print('Loading state abbreviations reference...')
state2abbr = {}
abbr2state = {}
stateabbr = path.abspath(path.join(basepath, '..', 'data', 'states.csv'))
for line in reader(open(stateabbr)):
	state2abbr[line[0]] = line[1]
	abbr2state[line[1]] = line[0]
print('Loading county data reference...')
countiesbyFIPS = {}
countiesbyLABEL = {}
county_data = path.abspath(path.join(basepath, '..', 'data', 'us_counties.csv'))
with open(county_data, 'r') as csvfile:
	for line in csv.DictReader(csvfile):
		line['KEY'] = line['\ufeffKEY']
		countiesbyFIPS[line['KEY']] = line
		if (len(line['State']) == 2):
			line['State'] = abbr2state[line['State']]
		temp = line['County'] + ', ' + line['State'] + ', US'
		# print(temp)
		countiesbyLABEL[temp] = line
		temp = line['County'] + ', ' + state2abbr[line['State']] + ', US'
		countiesbyLABEL[temp] = line
print()

# study data and hash locations
geohash = {} # labels that reference lat/lon
hash = {} # labels that reference the entire line
geo_consistent = 0 # curious if for same labels, geopoint is consistent
geo_inconsistent = 0 # curious if for same lables, geopoint changes
geo_fix = 0 # number of zero lat/lons that need fixing
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
print('Step ' + str(step_counter) + ' (General Fixes)...')
step_counter += 1
with open(datafile, 'r') as csvfile:
	for line in csv.DictReader(csvfile, dialect='piper'):
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
		# check state isn't abbreviated as there are some holes in tests above
		tok2 = line['LABEL'].split(',')
		if (len(tok2) == 3):
			if (tok2[2].strip() == 'US'):
				if (len(tok2[1].strip()) == 2):
					line['ADM2'] = abbr2state[tok2[1].strip()]
					if (line['ADM3'] != 'N/A'):
						line['LABEL'] = line['ADM3'] + ', ' + line['ADM2'] + ', US'
					else:
						line['LABEL'] = line['ADM2'] + ', US'
					key = line['LABEL']
		# mispellings/case fixes
		if (line['ADM3'] == 'Desoto'):
			line['ADM3'] = 'DeSoto'
			line['LABEL'] = line['LABEL'].replace('Desoto','DeSoto')
			key = key.replace('Desoto','DeSoto')
		# comma spacing
		line['LABEL'] = line['LABEL'].replace(', ', ',')
		line['LABEL'] = line['LABEL'].replace(',', ', ')
		key = key.replace(', ', ',')
		key = key.replace(',', ', ')
		# set hash
		# print(key)
		keyterm = line['LASTUPDATED'] + '_' + key
		#if (hash.get(keyterm) != None):
		#	print(keyterm)
		#	print('  B: ' + str(hash.get(keyterm)))
		#	print('  A: ' + str(line))
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
		#
		hash[keyterm] = line
		n_obs += 1

print('	# obs before: ' + str(n_obs))
print('	# obs intermediate: ' + str(len(hash)))
print('	# dupes removed: ' + str(n_obs-len(hash)))
print()
print('	# geohash\'s: ' + str(len(geohash)))
print('	# geo_consistent: ' + str(geo_consistent))
print('	# geo_inconsistent: ' + str(geo_inconsistent))
print('	# geo_fix: ' + str(geo_fix))
print()

# LOAD DATA FROM geo_corrections.txt and apply them to whatever remains
# LABEL|LAT|LON|COMMENT
geo_corrections = {}
try:
	geo_corrections_datafile = path.abspath(path.join(basepath, '..', 'data', 'geo_corrections.txt'))
	with open(geo_corrections_datafile, 'r') as geo_corrections_fileptr:
		for line in csv.DictReader(geo_corrections_fileptr, dialect='piper'):
			#print(line)
			geo_corrections[line['LABEL'].strip()] = [line['LAT'].strip(), line['LON'].strip()]
	print('	Loaded ' + str(len(geo_corrections)) + ' geo_corrections...')
except FileNotFoundError:
	print('	No geo_corrections file...')
except:
	print("Unexpected error:", sys.exc_info()[0])
print()

# fix lat/lons if we find entries in the geohash -> EASY
# we'll assume the more recent keys are more accurate, since they are the latest updates
geo_fixed = 0
geo_fixed_by_correction_file = 0
geo_cannot_fix = 0
print('Step ' + str(step_counter) + ' (Geo Fix)...')
step_counter += 1
for i, (key, v) in enumerate(hash.items()):
	#print(key.split('_')[1], v['LAT'], v['LON'])
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[1])
		if (temp != None):
			v['LAT'] = temp[0]
			v['LON'] = temp[1]
			geo_fixed += 1
		else:
			# lets see if we can fix from the 'geo_corrections' hash
			temp = geo_corrections.get(key.split('_')[1])
			if (temp != None):
				v['LAT'] = temp[0]
				v['LON'] = temp[1]
				geo_fixed_by_correction_file += 1
			else:
				print('	WARNING: can\'t fix geo: ' + v['LABEL'])
				geo_cannot_fix += 1
print('	# geo_fixed: ' + str(geo_fixed))
print('	# geo_fixed_by_correction_file: ' + str(geo_fixed_by_correction_file))
print('	# geo_cannot_fix: ' + str(geo_cannot_fix))
print('	# TOTAL: ' + str(geo_fixed + geo_cannot_fix))
print()

# WRITE OUT THOSE THAT NEED FIXED, UNSORTED
flag = {} # only want to write once per unique key
fileout = path.abspath(path.join(basepath, '..', 'data', 'geo_issues.txt'))
fileout = open(fileout,'w')
fileout.write('LABEL|LAT|LON\n')
num_to_fix = 0
for i, (key, v) in enumerate(hash.items()):
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[1])
		if (temp == None and flag.get(key.split('_')[1]) == None):
			v.get(key)
			flag[key.split('_')[1]] = True
			line = v['LABEL'] + '|' + v['LAT'] + '|' + v['LON']
			#print(line)
			num_to_fix += 1
			fileout.write(line + '\n')
fileout.close()
print('Step ' + str(step_counter) + ' (Geo Issues File)...\n	Generated geolocation fix file (# entries: ' + str(num_to_fix) + ')\n')
step_counter += 1

# # fix legacy county references
# num_fixed = 0
# for i, (key, v) in enumerate(hash.items()):
	# if (v['ADM1'] == 'US' and v['LABEL'].find('County') > 0 and v['ADM3'] == 'N/A' and (len(v['ADM2']) - v['ADM2'].find(', ') == 4)):
		# # print(v)
		# v['ADM3'] = v['ADM2'][:v['ADM2'].find(' County')]
		# state = v['ADM2'][v['ADM2'].find(', ') + 2:]
		# v['ADM2'] = abbr2state.get(state)
		# # v['LABEL'] = v['ADM3'] + ', ' + v['ADM2'] + ', US'
		# num_fixed += 1
		# # print(v)
# print('Step ' + str(step_counter) + '...\n	# Legacy County References Fixed: ' + str(num_fixed) + '\n')
# step_counter += 1

# assign county FIPs if N/A
print('Step ' + str(step_counter) + ' (County Labels)...')
step_counter += 1
# num_fixed = 0
# fipslookup_hash = {}
# for i, (key, v) in enumerate(hash.items()):
	# if (v['FIPS'] != 'N/A'):
		# fipslookup_hash[v['LABEL']] = v['FIPS']
# print('Hashed FIPs: ' + str(len(fipslookup_hash)))
# for i, (key, v) in enumerate(hash.items()):
	# if (v['ADM1'] == 'US' and v['LABEL'].find('County') > 0 and v['FIPS'] == 'N/A'):
		# # print(v)
		# if (len(v['ADM2']) == 2):
			# v['ADM2'] = abbr2state[v['ADM2']]
		# fips_key = v['ADM3'] + ', ' + v['ADM2'] + ', US'
		# # print(str(v) + ' >>> ' + fips_key)
		# temp = fipslookup_hash.get(fips_key)
		# if (temp != None):
			# v['LABEL'] = v['ADM3'] + ', ' + v['ADM2'] + ', US'
			# v['FIPS'] = temp
			# num_fixed += 1
# print('	# FIPs Fixed: ' + str(num_fixed))

# fix remaining county labels
num_fixed = 0
for i, (key, v) in enumerate(hash.items()):
	if (v['LABEL'].find('County') > 0):
		v['LABEL'] = v['LABEL'].replace(' County', '').strip()
		num_fixed += 1
print('	# County Labels Fixed: ' + str(num_fixed))

# data check - missing geos
# TODO: could remove these and let interpolation handle.
num_missing = 0
for i, (key, v) in enumerate(hash.items()):
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		num_missing += 1
print('\nStep ' + str(step_counter) + ' (Geo Check)...\n	Missing Geo: ' + str(num_missing) + ' (' + str(round(((num_missing * 100) / len(hash)), 1)) + '%)')
step_counter += 1

# data check - missing FIPs
num_missing = 0
num_possible = 0
num_fixed = 0
print('	Checking FIPS in Reference Hash...')
for i, (key, v) in enumerate(hash.items()):
	if (v['ADM1'] == 'US' and (v['ADM3'] != 'Unassigned' and v['ADM3'] != 'N/A')):
		num_possible += 1
		if (v['FIPS'] == 'N/A'):
			temp = countiesbyLABEL.get(v['LABEL'])
			#print(v['LABEL'], temp)
			if (temp != None):
				v['FIPS'] = temp['KEY']
				num_fixed += 1
			else:
				print('		' + v['LABEL'] + ':' + v['ADM1'] + '|' + v['ADM2'] + '|' + v['ADM3'])
				num_missing += 1
print('	Fixed FIPS: ' + str(num_fixed))
print('	Unresolvable FIPS: ' + str(num_missing) + ' (' + str(round(((num_missing * 100) / num_possible), 1)) + '%)')

# temporal study
print('\nStep ' + str(step_counter) + ' (Temporal Study)...')
step_counter += 1
#print(sorted(hash.keys())[0])
#print(sorted(hash.keys())[len(hash.keys())-1])
temp = sorted(hash.keys())[0]
date_start = temp[0:10]
temp = sorted(hash.keys())[len(hash.keys())-1]
date_stop = temp[0:10]
print('	date range: ' + date_start + '-' + date_stop)
date_start_obj = datetime.strptime(date_start, '%m/%d/%Y')
date_stop_obj = datetime.strptime(date_stop, '%m/%d/%Y')
print('	date range: ' + str(date_start_obj) + '-' + str(date_stop_obj))

fileout = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
fileout = open(fileout,'w')
flag = {} # flag hash if key is seen 
for key in sorted(hash.keys()):
	v = hash.get(key)
	#print(key, str(v)[len('OrderedDict('):len('OrderedDict(')+20])
	date = key[0:10]
	date_obj = datetime.strptime(date, '%m/%d/%Y')
	label = key[11:]
	#print(date,label,str(v))
	if (date != v['LASTUPDATED']):
		print('WARNING: ' + date + ',' + v['LASTUPDATED'])
	if (label != v['LABEL']):
		print('WARNING: [' + label + '=' + v['LABEL'] + ']')
	date_on = date_start_obj
	n = 1
	while (date_on <= date_stop_obj):
		keygen = date_on.strftime('%m/%d/%Y') + '_' + label
		v = hash.get(keygen)
		if (v != None):
			fileout.write(str(n) + '|' + date_on.strftime('%m/%d/%Y') + '|' + keygen + '|' + v['CONFIRMED'] + '\n')
			if (flag.get(label) == None):
				flag[label] = date_on
		else:
			if (flag.get(label) != None and flag.get(label) < date_on):
				fileout.write(str(n) + '|' + date_on.strftime('%m/%d/%Y') + '|' + keygen + '|' + 'MISSING!\n')
		n += 1
		date_on = date_on + timedelta(days=1)
fileout.close()

# TODO
for key in sorted(hash.keys()):
	v = hash.get(key)
	v['INTER'] = 'N'

print()
print('# obs after: ' + str(len(hash)))

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