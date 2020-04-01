#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: cleans the output from ts_merge.py by fixing historical US county entries; primarily normalizes
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
state_geo = {}
stateabbr = path.abspath(path.join(basepath, '..', 'data', 'states.csv'))
for line in reader(open(stateabbr)):
	state2abbr[line[0]] = line[1]
	abbr2state[line[1]] = line[0]
	state_geo[line[1]] = {}
	state_geo[line[1]]['LAT'] = line[2]
	state_geo[line[1]]['LON'] = line[3]
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

# fileout = path.abspath(path.join(basepath, '..', 'data', 'data_diamond.txt'))
# fileout = open(fileout,'w')
		
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
		# Wuhan Evacuee
		if (line['LABEL'].upper().find('WUHAN EVACUEE') >= 0): continue
		# U.S. Virgin Islands
		if (line['ADM1'] == 'US' and (line['ADM2'] == 'United States Virgin Islands' or \
			line['ADM2'] == 'Virgin Islands, U.S.' or line['ADM2'] == 'Virgin Islands')):
			line['ADM2'] = 'U.S. Virgin Islands'
			line['FIPS'] = '78000'
			line['LABEL'] = line['ADM3'] + ', ' + line['ADM2'] + ', US'
			key = line['LABEL']
		# cook county, IL (Chicago correction)
		if (line['ADM1'] == 'US' and line['LABEL'].find('Chicago') >= 0):
			line['ADM2'] = 'Illinois'
			line['ADM3'] = 'Cook'
			line['FIPS'] = '17031'
			line['LABEL'] = line['ADM3'] + ', ' + line['ADM2'] + ', US'
			key = line['LABEL']
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
			key = line['LABEL']
		# Out of [State] condition
		if ((line['ADM3'].startswith('Out of') or line['ADM3'].startswith('Out-of') or line['ADM3'].startswith('Unknown')) and \
			line['ADM1'] == 'US'):
			line['ADM3'] = 'Unassigned'
			line['LABEL'] = line['ADM3'] + ', ' + line['ADM2'] + ', US'
			key = line['LABEL']
		# ms zaandam cruise ship
		if (line['LABEL'].upper().find('MS ZAANDAM') >= 0):
			line['ADM3'] = 'Unassigned'
			line['ADM2'] = 'MS Zaandam'
			line['FIPS'] = 'ZAANDM'
			line['LABEL'] = line['ADM2'] + ', ' + line['ADM1']
			line['LAT'] = '9.38743' # Currently Panamal Canal
			line['LON'] = '-79.91863'
			key = line['LABEL']
		# grand princess or line['ADM2'].startswith('Grand Princess Cruise Ship')
		if (line['ADM1'].upper().find('GRAND PRINCESS') >= 0 or line['LABEL'].upper().find('GRAND PRINCESS') >= 0):
			#print('>>>' + line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'] + '|' + line['FIPS'])
			line['ADM2'] = 'Unassigned'
			line['ADM3'] = 'Grand Princess'
			if (line['ADM1'] == 'US'):
				line['FIPS'] = 'GRAPR'
			else:
				line['FIPS'] = 'N/A'
			line['LABEL'] = line['ADM2'] + ', ' + line['ADM1'] # could be other nationalities on this one
			line['LAT'] = '37.807054' # San Fran Pier
			line['LON'] = '-122.405770'
			#print('>>>' + line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'] + '|' + line['FIPS'])
			key = line['LABEL']
		# diamond princess conditions
		elif (line['LABEL'].upper().find('DIAMOND') >= 0 or line['LABEL'].upper().find('CRUISE') >= 0 or line['LABEL'].upper().find('SHIP') >= 0):
			#print('>>>' + line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'] + '|' + line['FIPS'])
			#fileout.write(line['LABEL'] + '\t' + line['ADM1'] + '\t' + line['ADM2'] + '\t' + line['ADM3'] + '\t' + line['FIPS'] + '\n')
			if (line['ADM1'] == 'Cruise Ship' or line['ADM1'] == 'Diamond Princess'):
				line['ADM1'] = 'Others'
			if (line['ADM1'] == 'Others' or line['ADM1'] != 'US'):
				line['ADM2'] = 'Diamond Princess'
				line['ADM3'] = 'N/A'
				line['FIPS'] = 'DIAMD'
				line['LABEL'] = line['ADM2'] + ', ' + line['ADM1']
				line['LAT'] = '35.456676' # Daikoku Pier Cruise Terminal
				line['LON'] = '139.679919'
				key = line['LABEL']
			if (line['ADM1'] == 'US'):
				line['FIPS'] = 'DIAMD'
				if (line['ADM2'].startswith('Unassigned') or line['ADM2'].startswith('Diamond Princess')):
					line['ADM2'] = 'Unassigned'
				else:
					temp_state = line['ADM2'].split(',')[1][0:3]
					line['ADM2'] = abbr2state.get(temp_state.strip())
				line['ADM3'] = 'Diamond Princess'
				line['LABEL'] = line['ADM3'] + ', ' + line['ADM2'] + ', US'
				key = line['LABEL']
			#fileout.write(line['LABEL'] + '\t' + line['ADM1'] + '\t' + line['ADM2'] + '\t' + line['ADM3'] + '\t' + line['FIPS'] + '\n')
			#print('  ' + line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'] + '|' + line['FIPS'])
		# DC, Washington DC.
		if (line['LABEL'].find('D.C.') != -1 or line['LABEL'].find('District of Columbia') != -1):
			# print(line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'])
			line['ADM3'] = 'District of Columbia'
			line['ADM2'] = 'District of Columbia'
			line['ADM1'] = 'US' # should be
			line['LABEL'] = 'District of Columbia, District of Columbia, US'
			key = line['LABEL']
			# print('	' + line['LABEL'] + '|' + line['ADM1'] + '|' + line['ADM2'] + '|' + line['ADM3'])
		else:
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
		if (line['ADM3'].find('Doña Ana') != -1):
			continue # these are redundant 
		if (line['ADM3'] == 'Desoto'):
			line['ADM3'] = 'DeSoto'
			line['LABEL'] = line['LABEL'].replace('Desoto','DeSoto')
			key = key.replace('Desoto','DeSoto')
		if (line['LABEL'].find('occupied Palestinian') != -1):
			line['LABEL'] = 'Occupied Palestinian Territory, Israel'
			line['ADM1'] = 'Israel'
			line['ADM2'] = 'Occupied Palestinian Territory'
			key = line['LABEL']
		# comma spacing
		line['LABEL'] = line['LABEL'].replace(', ', ',')
		line['LABEL'] = line['LABEL'].replace(',', ', ')
		key = key.replace(', ', ',')
		key = key.replace(',', ', ')
		# starting commas
		if (line['LABEL'].startswith(', , ') == True):
			line['LABEL'] = line['LABEL'][4:]
			key = line['LABEL']
		if (line['LABEL'].startswith(', ') == True):
			line['LABEL'] = line['LABEL'][2:]
			key = line['LABEL']
		# set hash
		# print(key)
		keyterm = key + '_' + line['LASTUPDATED']
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
		# store data in HASH
		hash[keyterm] = line
		n_obs += 1

#if (True): sys.exit('Halted')
# fileout.close()

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
geo_fixed_by_state_geo = 0
geo_cannot_fix = 0
print('Step ' + str(step_counter) + ' (Geo Fix)...')
step_counter += 1
for i, (key, v) in enumerate(hash.items()):
	#print(key.split('_')[1], v['LAT'], v['LON'])
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[0]) # the key term (the label piece not the date)
		if (temp != None):
			v['LAT'] = temp[0]
			v['LON'] = temp[1]
			geo_fixed += 1
		else:
			# lets see if we can fix from state_geo hash
			if (v['ADM3'] == 'Unassigned' and v['ADM1'] == 'US'):
				try:
					v['LAT'] = state_geo.get(state2abbr.get(v['ADM2']))['LAT']
					v['LON'] = state_geo.get(state2abbr.get(v['ADM2']))['LON']
					geo_fixed_by_state_geo += 1
				except:
					print('	WARNING: can\'t fix geo: ' + v['LABEL'])
					geo_cannot_fix += 1
			else:
				# lets see if we can fix from the 'geo_corrections' hash
				temp = geo_corrections.get(key.split('_')[0])
				if (temp != None):
					v['LAT'] = temp[0]
					v['LON'] = temp[1]
					geo_fixed_by_correction_file += 1
				else:
					v['LAT'] = '0.0'
					v['LON'] = '0.0'
					print('	WARNING: can\'t fix geo: ' + v['LABEL'])
					geo_cannot_fix += 1
print('	# geo_fixed: ' + str(geo_fixed))
print('	# geo_fixed_by_correction_file: ' + str(geo_fixed_by_correction_file))
print('	# geo_fixed_by_state_geo: ' + str(geo_fixed_by_state_geo))
print('	# geo_cannot_fix: ' + str(geo_cannot_fix))
print('	# TOTAL: ' + str(geo_fixed + geo_fixed_by_correction_file + geo_fixed_by_state_geo + geo_cannot_fix))
print()

# WRITE OUT THOSE THAT NEED FIXED, UNSORTED
flag = {} # only want to write once per unique key
fileout = path.abspath(path.join(basepath, '..', 'data', 'geo_issues.txt'))
fileout = open(fileout,'w')
fileout.write('LABEL|LAT|LON\n')
num_to_fix = 0
for i, (key, v) in enumerate(hash.items()):
	if (float(v['LAT']) == 0 or float(v['LON']) == 0):
		temp = geohash.get(key.split('_')[0])
		if (temp == None and flag.get(key.split('_')[0]) == None):
			v.get(key)
			flag[key.split('_')[0]] = True
			line = v['LABEL'] + '|' + v['LAT'] + '|' + v['LON']
			#print(line)
			num_to_fix += 1
			fileout.write(line + '\n')
fileout.close()
print('Step ' + str(step_counter) + ' (Geo Issues File)...\n	Generated geolocation fix file (# entries: ' + str(num_to_fix) + ')\n')
step_counter += 1

# assign county FIPs if N/A
print('Step ' + str(step_counter) + ' (County Labels)...')
step_counter += 1

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

# temporal sort
print('\nStep ' + str(step_counter) + ' (Temporal Sort)...')
step_counter += 1
date_start_obj = datetime.strptime('1/1/2100', '%m/%d/%Y')
date_stop_obj = datetime.strptime('1/1/1900', '%m/%d/%Y')
for k in hash.keys():
	date_temp = k.split('_')[1] # date part
	date_temp_obj = datetime.strptime(date_temp, '%m/%d/%Y')
	if (date_temp_obj > date_stop_obj):
		date_stop_obj = date_temp_obj
	if (date_temp_obj < date_start_obj):
		date_start_obj = date_temp_obj
print('	date range: ' + date_start_obj.strftime('%m/%d/%Y') + '-' + date_stop_obj.strftime('%m/%d/%Y'))

fileout = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|POBS|DATE|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN\n')
obs = 1
flag1 = {} # flag hash if key is seen (flag)
for key in sorted(hash.keys()):
	v = hash.get(key)
	#print(key, str(v)[len('OrderedDict('):len('OrderedDict(')+20])
	date = key.split('_')[1]
	date_obj = datetime.strptime(date, '%m/%d/%Y')
	label = key.split('_')[0]
	if (flag1.get(label) != None):
		continue
	#print(date,label,str(v))
	if (date != v['LASTUPDATED']):
		print('WARNING: ' + date + ',' + v['LASTUPDATED'])
	if (label != v['LABEL']):
		print('WARNING: [' + label + '=' + v['LABEL'] + ']')
	date_on = date_start_obj
	# roll dates forward
	line = None
	bv = None
	# consistent lat/lon
	tv = None
	date_check = date_stop_obj
	while (tv == None):
		keygen = label + '_' + date_check.strftime('%m/%d/%Y')
		tv = hash.get(keygen)
		date_check = date_check + timedelta(days=-1)
		if (tv != None):
			fLat = tv['LAT']
			fLon = tv['LON']
	while (date_on <= date_stop_obj):
		keygen = label + '_' + date_on.strftime('%m/%d/%Y')
		v = hash.get(keygen)
		flg_write = 0
		if (v != None):
			# fileout.write(str(n) + '|' + date_on.strftime('%m/%d/%Y') + '|' + keygen + '|' + v['CONFIRMED'] + '\n')
			if (flag1.get(label) == None):
				flag1[label] = date_on
				bv = v
				n_days = 1
				line = str(obs) + '|' + v['OBS'] + '|' + date_on.strftime('%m/%d/%Y') + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + \
				v['ADM2'] + '|' + v['ADM1'] + '|' + fLat + '|' + fLon + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
				v['ACTIVE'] + '|' + 'N|1'
			else:
				n_days += 1
				line = str(obs) + '|' + v['OBS'] + '|' + date_on.strftime('%m/%d/%Y') + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + \
				v['ADM2'] + '|' + v['ADM1'] + '|' + fLat + '|' + fLon + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
				v['ACTIVE'] + '|' + 'N|' + str(n_days)
		else:
			if (flag1.get(label) != None and flag1.get(label) < date_on):
				n_days += 1
				line = str(obs) + '|' + bv['OBS'] + '|' + date_on.strftime('%m/%d/%Y') + '|' + bv['LABEL'] + '|' + bv['FIPS'] + '|' + bv['ADM3'] + '|' + \
				bv['ADM2'] + '|' + bv['ADM1'] + '|' + fLat + '|' + fLon + '|' + '-1' + '|' + '-1' + '|' + '-1' + '|' + \
				'-1' + '|' + 'Y|' + str(n_days)
		date_on = date_on + timedelta(days=1)
		if (line != None): # write record
			#print(line)
			fileout.write(line + '\n')
			line = None
			obs += 1
fileout.close()

print()
print('# data_merged # obs (before): ' + str(n_obs))
print('# data_temporal # obs: ' + str(obs))
print('# data_cleaned # obs: ' + str(len(hash)))

fileout = path.abspath(path.join(basepath, '..', 'data', 'data_cleaned.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|POBS|DATE|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE\n')
obs = 1
for key in sorted(hash.keys()):
	v = hash.get(key)
	# consistent lat/lon
	tv = None
	date_check = date_stop_obj
	while (tv == None):
		keygen = v['LABEL'] + '_' + date_check.strftime('%m/%d/%Y')
		tv = hash.get(keygen)
		date_check = date_check + timedelta(days=-1)
		if (tv != None):
			fLat = tv['LAT']
			fLon = tv['LON']
	line = str(obs) + '|' + v['OBS'] + '|' + v['LASTUPDATED'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + \
	v['ADM2'] + '|' + v['ADM1'] + '|' + fLat + '|' + fLon + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
	v['ACTIVE']
	#print(line)
	fileout.write(line + '\n')
	obs += 1
fileout.close()

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))