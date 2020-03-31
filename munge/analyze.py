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
import cf_model
import numpy as np
import copy

start = timer()
now = datetime.now()
dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
print('Starting... (' + dt_string + ' Z)')

step_counter = 1
basepath = path.dirname(__file__)

# OBS|POBS|LASTUPDATED|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN
# 1|1|01/22/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|1|0|0|-1|N|1
# 2|39|01/23/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|9|0|0|-1|N|2

label_prior = None
case_n_positive = 0
died_n_positive = 0
n_obs = 0
key_data = []
date_data = []
case_data = []
died_data = []		
		
ndays = 3 # days to project
case_n_positive = 0
died_n_positive = 0
n_cpass = 0
n_cfail = 0
n_cnei = 0
n_cinter =  0
n_dpass = 0
n_dfail = 0
n_dnei = 0
n_dinter =  0

# stats , CASES: rsqd, popt1, popt2, DIED : rsqd, popt1, popt2
statsc = np.zeros((3000,3))
statsc[:] = np.nan # fill all as NaN
statsd = np.zeros((3000,3))
statsd[:] = np.nan # fill all as NaN
statscl = [''] * 3000

def merge_hashes(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res

# study loop
hash = {}
hashp = {} # projected entries
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
data = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
with open(data, 'r') as csvfile:
	for v in csv.DictReader(csvfile, dialect='piper'):
		label = v['LABEL']
		hash[v['LABEL'] + '_' + v['DATE']] = v
		#print('? ', label, '|', label_prior)
		# get rid of oddities 
		if (label.find('Unassigned') == -1 and label.find('Out of') == -1 and \
		label.find('Recovered') == -1 and label.find('US, US') == -1):
			# do something with buffer, because the label is new
			if (label_prior != label or label_prior == None):
				#print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
				# arbitrarily looking for 3 days where number of cases is > 0
				if (case_n_positive > 3):
					#print('=======================================')
					#print(label_prior + ' : ' + str(n_obs) + ':' + str(case_n_positive))
					#print(date_data)
					#print(case_data)
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', False)
					if (rsqd >= 0.40 and v['ADM1'] == 'US' and v['FIPS'] != 'N/A'):
						statsc[n_cpass] = (rsqd, popt[0], popt[1])
						statscl[n_cpass] = label_prior
						n_cpass += 1
						# interpolate
						date_project_start = None
						for i in range(len(key_data)):
							vtemp = hash[key_data[i]]
							vtemp_date_obj = datetime.strptime(vtemp['DATE'], '%m/%d/%Y')
							if (date_project_start == None or vtemp_date_obj < date_project_start): date_project_start = vtemp_date_obj
							if (case_data[i] == -1):
								case_data[i] = str(int(round(ym_data[i],0)))
								vtemp['FLAG'] += 'C'
								vtemp['CONFIRMED'] = case_data[i]
								n_cinter += 1
						# add projection data
						# print(date_project_start)
						# print(date_data)
						# print(xm_data)
						# print(ym_data)
						# print(len(date_data),len(ym_data))
						for i in range(len(date_data), len(xm_data)):
							date_obj = date_project_start + timedelta(days=i)
							#print(i, date_obj, ym_data[i])
							keygen = key_data[0].split('_')[0] + '_' + date_obj.strftime('%m/%d/%Y')
							hashp[keygen] = copy.deepcopy(hash[key_data[0]])
							hashp[keygen]['DATE'] = date_obj.strftime('%m/%d/%Y')
							hashp[keygen]['RECOVERED'] = '-1'
							hashp[keygen]['ACTIVE'] = '-1'
							hashp[keygen]['DAYN'] = str(i+1)
							hashp[keygen]['FLAG'] = 'YP'
							hashp[keygen]['CONFIRMED'] = str(int(round(ym_data[i], 0)))
							#print(keygen, hashp[keygen])
					else:
						n_cfail += 1
					print(label_prior + ' : ' + str(n_obs) + ':' + str(case_n_positive) + ' --C--> {:0.3f}'.format(rsqd))
					#if (True): sys.exit('ok')
					#if (True): break
				else:
					n_cnei += 1
				# arbitrarily looking for 3 days where number of deaths is > 0
				if (died_n_positive > 3):
					#print('=======================================')
					#print(label_prior + ' : ' + str(n_obs) + ':' + str(died_n_positive))
					#print(date_data)
					#print(died_data)
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, died_data, \
						ndays, label_prior, 'Deaths', 'EXP', False)
					if (rsqd >= 0.80 and v['ADM1'] == 'US' and v['FIPS'] != 'N/A'):
						statsd[n_dpass] = (rsqd, popt[0], popt[1])
						n_dpass += 1
						# interpolate
						for i in range(len(key_data)):
							if (died_data[i] == -1):
								died_data[i] = str(int(round(ym_data[i],0)))
								vtemp = hash[key_data[i]]
								vtemp['FLAG'] += 'D'
								vtemp['DEATHS'] = died_data[i]
								n_dinter += 1
						for i in range(len(date_data), len(xm_data)):
							date_obj = date_project_start + timedelta(days=i)
							#print(i, date_obj, ym_data[i])
							keygen = key_data[0].split('_')[0] + '_' + date_obj.strftime('%m/%d/%Y')
							if (hashp.get(keygen) == None):
								hashp[keygen] = copy.deepcopy(hash[key_data[0]])
								hashp[keygen]['DATE'] = date_obj.strftime('%m/%d/%Y')
								hashp[keygen]['RECOVERED'] = '-1'
								hashp[keygen]['ACTIVE'] = '-1'
								hashp[keygen]['DAYN'] = str(i+1)
								hashp[keygen]['FLAG'] = 'YP'
							hashp[keygen]['DEATHS'] = str(int(round(ym_data[i], 0)))
							#print(keygen, hashp[keygen])
					else:
						n_dfail += 1
					#print(label_prior + ' : ' + str(n_obs) + ':' + str(died_n_positive) + ' --C--> {:0.3f}'.format(rsqd))
					#if (True): sys.exit('ok')
				else:
					n_dnei += 1
				# reset after doing something above
				label_prior = label
				case_n_positive = 0
				died_n_positive = 0
				n_obs = 0
				key_data = []
				date_data = []
				case_data = []
				died_data = []
			# done every iteration
			key_data.append(v['LABEL'] + '_' + v['DATE'])
			date_data.append(datetime.strptime(v['DATE'], '%m/%d/%Y'))
			case_data.append(int(v['CONFIRMED']))
			died_data.append(int(v['DEATHS']))
			if (int(v['CONFIRMED']) > 0): case_n_positive += 1
			if (int(v['DEATHS']) > 0): died_n_positive += 1
			n_obs += 1
			#print(v['LABEL'] + '_' + v['DATE'] + ' >>> ' + v['CONFIRMED'] + ' ' + str(n_obs))

# state roll up & national US
# st_data = {}
# for key in sorted(hash.keys()):
	# v = hash.get(key)
	# if (v['FIPS'] != 'N/A' and v['ADM2'] != 'Grand Princess'):
		# state = v['ADM2']
		# if (st_data.get(state) == None):
			# st_data[state] = {}
		# if (st_data[state].get(v['FIPS']) == None):
			# st_data[state][v['FIPS']] = {}
		# if (st_data[state][v['FIPS']].get(v['DATE']) == None):
			# st_data[state][v['FIPS']][v['DATE']] = key
		# else:
			# print(st_data[state][v['FIPS']][v['DATE']])
			# sys.exit('Invalid Key: ' + key + ' >>> ' + str(v))
# for st in st_data:
	# print(st)
	# for fips in st_data[st]:
		# print('	' + fips)
		# for date in st_data[st][fips]:
			# print('		' + date)
			
# interpolations
#if (True): sys.exit('Ok')
print('\nWriting Interpolated Temporal File...')
fileout = path.abspath(path.join(basepath, '..', 'data', 'data_temporal_i.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|DATE|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN\n')
n_obs = 1
for key in sorted(hash.keys()):
	v = hash.get(key)
	line = v['OBS'] + '|' + v['DATE'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + v['ADM2'] + '|' + \
	v['ADM1'] + '|' + v['LAT'] + '|' + v['LON'] + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
	v['ACTIVE'] + '|' + v['FLAG'] + '|' + v['DAYN']
	fileout.write(line + '\n')
	n_obs += 1
fileout.close()
print(str(n_obs) + ' records.')

# projections
hash2 = merge_hashes(hash, hashp)
print('\nProjections: ' + str(len(hashp)))
print('\nWriting Projected Temporal File...')
fileout = path.abspath(path.join(basepath, '..', 'data', 'data_temporal_p.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|DATE|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN\n')
n_obs = 1
for key in sorted(hash2.keys()):
	v = hash2.get(key)
	#print(key, v)
	line = str(n_obs) + '|' + v['DATE'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + v['ADM2'] + '|' + \
	v['ADM1'] + '|' + v['LAT'] + '|' + v['LON'] + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
	v['ACTIVE'] + '|' + v['FLAG'] + '|' + v['DAYN']
	fileout.write(line + '\n')
	n_obs += 1
fileout.close()
print(str(n_obs) + ' records.')

# stats
print('\nCase Statistics:')
print('Min   : ' + str(np.nanmin(statsc, axis = 0)))
print('Max   : ' + str(np.nanmax(statsc, axis = 0)))
print('Mean  : ' + str(np.nanmean(statsc, axis = 0)))
print('Median: ' + str(np.nanmedian(statsc, axis = 0)))
print('StdDev: ' + str(np.nanstd(statsc, axis = 0)))

print('\n# Pass:  ' + str(n_cpass))
print('# Fail:  ' + str(n_cfail))
print('# (NI):  ' + str(n_cnei))
print('# Inter: ' + str(n_cinter))

print('\nDied Statistics:')
print('Min   : ' + str(np.nanmin(statsd, axis = 0)))
print('Max   : ' + str(np.nanmax(statsd, axis = 0)))
print('Mean  : ' + str(np.nanmean(statsd, axis = 0)))
print('Median: ' + str(np.nanmedian(statsd, axis = 0)))
print('StdDev: ' + str(np.nanstd(statsd, axis = 0)))

print('\n# Pass:  ' + str(n_dpass))
print('# Fail:  ' + str(n_dfail))
print('# (NI):  ' + str(n_dnei))
print('# Inter: ' + str(n_dinter))

# set deviation/average coefficients (US only would need US only filter above)
dev = np.zeros((2,6))
dev[0][2] = np.nanmean(statsc, axis = 0)[1] # average a
dev[0][3] = np.nanmean(statsc, axis = 0)[2] # average b
dev[1][2] = np.nanmean(statsd, axis = 0)[1] # average a
dev[1][3] = np.nanmean(statsd, axis = 0)[2] # average b
dev[0][0] = dev[0][2] + np.nanstd(statsc, axis = 0)[1] # 1st stddev above a
dev[0][1] = dev[0][3] + np.nanstd(statsc, axis = 0)[2] # 1st stddev above b
dev[0][4] = dev[0][2] - np.nanstd(statsc, axis = 0)[1] # 1st stddev below a
dev[0][5] = dev[0][3] - np.nanstd(statsc, axis = 0)[2] # 1st stddev below b
#print(dev)

# for i in range(1010): # SHOULD NOT HAPPEN; LEAVE HERE FOR DEBUGGING
	# if (statsc[i][2] < 0): 
		# print(str(i) + ' ' + statscl[i] + ' {0:.3f}'.format(statsc[i][0]) + ' ' + '{0:.3f}'.format(statsc[i][1]) + ' ' + '{0:.3f}'.format(statsc[i][2]))

# plot loop
label_prior = label
case_n_positive = 0
died_n_positive = 0
n_obs = 0
key_data = []
date_data = []
case_data = []
died_data = []
print()
hash = {}
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
data = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
with open(data, 'r') as csvfile:
	for v in csv.DictReader(csvfile, dialect='piper'):
		label = v['LABEL']
		hash[v['LABEL'] + '_' + v['DATE']] = v
		# interested in US counties only
		if (v['ADM1'] != 'US'): continue
		if (v['FIPS'] == 'N/A'): continue
		#print('? ', label, '|', label_prior)
		# get rid of oddities 
		if (label.find('Unassigned') == -1 and label.find('Out of') == -1 and \
		label.find('Recovered') == -1 and label.find('US, US') == -1):
			# do something with buffer, because the label is new
			if (label_prior != label or label_prior == None):
				#print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
				# arbitrary looking for 3 days where number of cases is > 0
				if (case_n_positive > 3):
					#print('=======================================')
					#print(label_prior + ' --C--> ')
					#print(date_data)
					#print(case_data)
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', False)
					if (rsqd >= 0.80):
						#if (plt != None):
						#y_avg_data = np.zeros(len(xm_data))
						# for i in range(len(xm_data)):
							# #y_avg_data[0][i] = cf_model.model_exp(xm_data[i], dev[0][0], dev[0][1])
						y_avg_data = cf_model.model_exp(xm_data, dev[0][2], dev[0][3]) 
						y_avg_data = y_avg_data / y_avg_data[0]

						si = -1 # starting index where ym_data >= 1
						for i in range(len(ym_data)):
							if (ym_data[i] >= 1.0): 
								si = i
								break
						if (si == -1):
							sys.exit('zero value ym_data', ym_data)
							
						y_avg_data = y_avg_data * ym_data[si]
						plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', True, y_avg_data, 'U.S. County Average', yscale = 'LOG')
						
						plot_img = path.abspath(path.join(basepath, '..', 'plots', \
						label_prior.replace(' ','_').replace(',','') + '_C.png'))
						plt.savefig(plot_img)
						plt.close(fig)
						plt = None
						fig = None
						print(label_prior + ' --C--> {:0.3f}'.format(rsqd))
					#if (True): sys.exit('ok')
				# arbitrary looking for 3 days where number of deaths is > 0
				if (died_n_positive > 3):
					#print(label_prior + ' --D--> ')
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, died_data, \
						ndays, label_prior, 'Deaths', 'EXP', False)
					if (rsqd >= 0.80):
						#if (plt != None):
						#y_avg_data = np.zeros(len(xm_data))
						# for i in range(len(xm_data)):
							# #y_avg_data[0][i] = cf_model.model_exp(xm_data[i], dev[0][0], dev[0][1])
						y_avg_data = cf_model.model_exp(xm_data, dev[1][2], dev[1][3]) 
						y_avg_data = y_avg_data / y_avg_data[0]
						
						# print(xm_data)
						# print(ym_data)
						# print(y_avg_data)
						# print(y_avg_data / y_avg_data[0])
						# if (True): sys.exit('Stopping...')

						si = -1 # starting index where ym_data >= 1
						for i in range(len(ym_data)):
							if (ym_data[i] >= 1.0): 
								si = i
								break
						if (si == -1):
							sys.exit('zero value ym_data', ym_data)
							
						y_avg_data = y_avg_data * ym_data[si]
						plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, died_data, \
						ndays, label_prior, 'Deaths', 'EXP', True, y_avg_data, 'U.S. County Average', yscale = 'LOG')
						
						plot_img = path.abspath(path.join(basepath, '..', 'plots', \
						label_prior.replace(' ','_').replace(',','') + '_D.png'))
						plt.savefig(plot_img)
						plt.close(fig)
						plt = None
						fig = None
						print(label_prior + ' --D--> {:0.3f}'.format(rsqd))
					#if (True): sys.exit('ok')
				# reset after doing something above
				label_prior = label
				case_n_positive = 0
				died_n_positive = 0
				n_obs = 0
				key_data = []
				date_data = []
				case_data = []
				died_data = []
			# done every iteration
			key_data.append(v['LABEL'] + '_' + v['DATE'])
			date_data.append(datetime.strptime(v['DATE'], '%m/%d/%Y'))
			case_data.append(int(v['CONFIRMED']))
			died_data.append(int(v['DEATHS']))
			if (int(v['CONFIRMED']) > 0): case_n_positive += 1
			if (int(v['DEATHS']) > 0): died_n_positive += 1
			n_obs += 1
			#print(v['LABEL'] + '_' + v['DATE'] + ' >>> ' + v['CONFIRMED'] + ' ' + str(n_obs))

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))