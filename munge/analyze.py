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

start = timer()
now = datetime.now()
dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
print('Starting... (' + dt_string + ' Z)')

step_counter = 1
basepath = path.dirname(__file__)

# OBS|POBS|LASTUPDATED|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN
# 1|1|01/22/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|1|0|0|-1|N|1
# 2|39|01/23/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|9|0|0|-1|N|2

n_obs = 0 # observations
ndays = 3
label_prior = None
label_prior_v = None
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

# study loop
hash = {}
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
data = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
with open(data, 'r') as csvfile:
	for v in csv.DictReader(csvfile, dialect='piper'):
		label = v['LABEL']
		hash[v['LABEL'] + '_' + v['DATE']] = v
		#print('? ', label, '|', label_prior)
		# interested in US only
		if (v['ADM1'] != 'US'): continue
		# get rid of oddities 
		if (label.find('Unassigned') == -1 and label.find('Out of') == -1 and \
		label.find('Recovered') == -1 and label.find('US, US') == -1):
			# do something with buffer, because the label is new
			if (label_prior != label or label_prior == None):
				# arbitrary looking for 3 days where number of cases is > 0
				if (case_n_positive > 3):
					#print('=======================================')
					#print(label_prior + ' ----> ' + str(n_obs) + ':' + str(case_n_positive))
					#print(date_data)
					#print(case_data)
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', False)
					if (rsqd >= 0.80):
						if (plt != None):
							plot_img = path.abspath(path.join(basepath, '..', 'data', 'plots', \
							label_prior.replace(' ','_').replace(',','') + '_C.png'))
							plt.savefig(plot_img)
							plt.close(fig)
							plt = None
						statsc[n_cpass] = (rsqd, popt[0], popt[1])
						statscl[n_cpass] = label_prior
						n_cpass += 1
						#if (n_ok > 10): break
						# try:
							# print('R-Squared: ' + '{0:.3f}'.format(rsqd) + ' POPT: ' + '{0:.3f}'.format(popt[0]) + ', ' + \
							# '{0:.3f}'.format(popt[1]))
						# except:
							# print('R-Squared: ' + str(rsqd) + ' POPT: ' + str(popt))
						# interpolate
						# print('=======================================')
						# print(key_data)
						# print(case_data)
						# print(date_data)
						# print(xm_data)
						# print(ym_data)
						for i in range(len(key_data)):
							if (case_data[i] == -1):
								case_data[i] = str(int(round(ym_data[i],0)))
								vtemp = hash[key_data[i]]
								vtemp['FLAG'] += 'C'
								vtemp['CONFIRMED'] = case_data[i]
								n_cinter += 1
						fig = None
					else:
						n_cfail += 1
						if (plt != None):
							plt.close(fig)
							plt = None
				else:
					n_cnei += 1
				# arbitrary looking for 3 days where number of deaths is > 0
				if (died_n_positive > 3):
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, died_data, \
						ndays, label_prior, 'Deaths', 'EXP', False)
					if (rsqd >= 0.80):
						if (plt != None):
							plot_img = path.abspath(path.join(basepath, '..', 'data', 'plots', \
							label_prior.replace(' ','_').replace(',','') + '_D.png'))
							plt.savefig(plot_img)
							plt.close(fig)
							plt = None
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
						fig = None
					else:
						n_dfail += 1
						if (plt != None):
							plt.close(fig)
							plt = None
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

# interpolations
print('\nWriting Interpolated Temporal File...')
fileout = path.abspath(path.join(basepath, '..', 'data', 'data_temporal_i.txt'))
fileout = open(fileout,'w')
fileout.write('OBS|DATE|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FLAG|DAYN\n')
for key in sorted(hash.keys()):
	v = hash.get(key)
	line = v['OBS'] + '|' + v['DATE'] + '|' + v['LABEL'] + '|' + v['FIPS'] + '|' + v['ADM3'] + '|' + v['ADM2'] + '|' + \
	v['ADM1'] + '|' + v['LAT'] + '|' + v['LON'] + '|' + v['CONFIRMED'] + '|' + v['DEATHS'] + '|' + v['RECOVERED'] + '|' + \
	v['ACTIVE'] + '|' + v['FLAG'] + '|' + v['DAYN']
	fileout.write(line + '\n')
fileout.close()

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
dev[0][0] = dev[0][2] + np.nanstd(statsc, axis = 0)[1] # 1st stddev above a
dev[0][1] = dev[0][3] + np.nanstd(statsc, axis = 0)[2] # 1st stddev above b
dev[0][4] = dev[0][2] - np.nanstd(statsc, axis = 0)[1] # 1st stddev below a
dev[0][5] = dev[0][3] - np.nanstd(statsc, axis = 0)[2] # 1st stddev below b
#print(dev)

# for i in range(1010): # SHOULD NOT HAPPEN
	# if (statsc[i][2] < 0): 
		# print(str(i) + ' ' + statscl[i] + ' {0:.3f}'.format(statsc[i][0]) + ' ' + '{0:.3f}'.format(statsc[i][1]) + ' ' + '{0:.3f}'.format(statsc[i][2]))

# plot loop
label_prior == None
print()
hash = {}
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
data = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
with open(data, 'r') as csvfile:
	for v in csv.DictReader(csvfile, dialect='piper'):
		label = v['LABEL']
		hash[v['LABEL'] + '_' + v['DATE']] = v
		# interested in US only
		if (v['ADM1'] != 'US'): continue
		# get rid of oddities 
		if (label.find('Unassigned') == -1 and label.find('Out of') == -1 and \
		label.find('Recovered') == -1 and label.find('US, US') == -1):
			# do something with buffer, because the label is new
			if (label_prior != label):
				# arbitrary looking for 3 days where number of cases is > 0
				if (case_n_positive > 3):
					print(v['LABEL'] + ' >>> C ')
					plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', False)
					if (rsqd >= 0.80):
						#if (plt != None):
						#y_avg_data = np.zeros(len(xm_data))
						# for i in range(len(xm_data)):
							# #y_avg_data[0][i] = cf_model.model_exp(xm_data[i], dev[0][0], dev[0][1])
						y_avg_data = cf_model.model_exp(xm_data, dev[0][2], dev[0][3])
							
						# print(xm_data)
						# print(ym_data)
						# print(y_avg_data)
						
						si = -1 # starting index where ym_data >= 1
						for i in range(len(ym_data)):
							if (ym_data[i] >= 1.0): 
								si = i
								break
						if (si == -1):
							sys.exit('zero value ym_data', ym_data)
							
						#print(y_avg_data)
						y_avg_data = y_avg_data * ym_data[si]
						# print(y_avg_data)
						#if (True): sys.exit('ok')
						
						plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
						ndays, label_prior, 'Cases', 'EXP', True, y_avg_data, 'U.S. Average')
						#ax.plot(xm_data, y_avg_data, '-.', color ='lightgreen', label = "U.S. Average")
						#ax.legend()
						
						plot_img = path.abspath(path.join(basepath, '..', 'data', 'plots', \
						label_prior.replace(' ','_').replace(',','') + '_C.png'))
						plt.savefig(plot_img)
						plt.close(fig)
						plt = None
						#if (True): sys.exit('ok')
						fig = None
					# elif (plt != None):
						# plt.close(fig)
						# plt = None
				# reset after doing something above
				label_prior = label
				label_prior_v = v
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

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))