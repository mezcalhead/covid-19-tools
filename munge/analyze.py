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
n_obs = 0 # observations

# OBS|POBS|LASTUPDATED|LABEL|FIPS|ADM3|ADM2|ADM1|LAT|LON|CONFIRMED|DEATHS|RECOVERED|ACTIVE|FILL|DAYN
# 1|1|01/22/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|1|0|0|-1|N|1
# 2|39|01/23/2020|Anhui, Mainland China|N/A|N/A|Anhui|Mainland China|31.8257|117.2264|9|0|0|-1|N|2

ndays = 3
label_on = None
case_n_positive = 0
died_n_positive = 0
n_pass = 0
n_fail = 0
n_nei = 0

# stats , rsqd, popt1, popt2
stats = np.zeros((3000,3))
stats[:] = np.nan # fill all as NaN

# loop
csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
data = path.abspath(path.join(basepath, '..', 'data', 'data_temporal.txt'))
with open(data, 'r') as csvfile:
	for line in csv.DictReader(csvfile, dialect='piper'):
		label = line['LABEL']
		# interested in US only
		if (line['ADM1'] == 'US'):
			# get rid of oddities 
			if (label.find('Unassigned') == -1 and label.find('Out of') == -1 and \
			label.find('Recovered') == -1 and label.find('US, US') == -1):
				# do something with buffer, because the label is new
				if (label_on != label or label_on == None):
					# arbitrary looking for 3 days where number of cases is > 0
					if (case_n_positive > 3):
						#print('=======================================')
						#print(label_on + ' -> ' + str(n_obs) + ':' + str(case_n_positive))
						#print(date_data)
						#print(case_data)
						plt, popt, rsqd, fig = cf_model.calculate(date_data, case_data, ndays, label_on, 'Cases', 'EXP', False)
						if (rsqd >= 0.70):
							if (plt != None):
								plot_img = path.abspath(path.join(basepath, '..', 'data', 'plots', label_on.replace(' ','_').replace(',','') + '.png'))
								plt.savefig(plot_img)
								plt.close(fig)
								plt = None
							stats[n_pass] = (rsqd, popt[0], popt[1])
							n_pass += 1
							#if (n_ok > 10): break
							# try:
								# print('R-Squared: ' + '{0:.3f}'.format(rsqd) + ' POPT: ' + '{0:.3f}'.format(popt[0]) + ', ' + \
								# '{0:.3f}'.format(popt[1]))
							# except:
								# print('R-Squared: ' + str(rsqd) + ' POPT: ' + str(popt))
						else:
							n_fail += 1
					else:
						n_nei += 1
					# reset after doing something above
					label_on = label
					case_n_positive = 0
					died_n_positive = 0
					n_obs = 0
					date_data = []
					case_data = []
					died_data = []
				# done every iteration
				date_data.append(datetime.strptime(line['DATE'], '%m/%d/%Y'))
				case_data.append(int(line['CONFIRMED']))
				died_data.append(int(line['DEATHS']))
				if (int(line['CONFIRMED']) > 0): case_n_positive += 1
				if (int(line['DEATHS']) > 0): died_n_positive += 1
				n_obs += 1

# stats
print('\nStatistics:')
print('Min   : ' + str(np.nanmin(stats, axis = 0)))
print('Max   : ' + str(np.nanmax(stats, axis = 0)))
print('Mean  : ' + str(np.nanmean(stats, axis = 0)))
print('Median: ' + str(np.nanmedian(stats, axis = 0)))
print('StdDev: ' + str(np.nanstd(stats, axis = 0)))

print('\n# Pass:	' + str(n_pass))
print('# Fail:	' + str(n_fail))
print('# (NI):	' + str(n_nei))

print('\nDone.')
duration = timer()-start
print('Execution Time: {:0.2f}s'.format(duration))