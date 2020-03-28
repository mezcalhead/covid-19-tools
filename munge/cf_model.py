#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# curve fit model and graphics support
#
import numpy as np
from scipy.optimize import curve_fit 
import sys
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import time

class Error(Exception):
	# Base class for exceptions in this module.
	pass

def model(x, a, b): 
	return a*np.exp(b*x)

def fit(x_data, y_data):
	p0 = [1,1] # on day 1, 1 case -> hint for the curve fit
	popt, pcov = curve_fit(model, x_data, y_data, p0)
	perr = np.sqrt(np.diag(pcov))
	# residual sum of squares
	residuals = y_data - model(x_data, popt[0], popt[1])
	ss_res = np.sum(residuals**2)
	# total sum of squares
	ss_tot = np.sum((y_data-np.mean(y_data))**2)
	# r-squared
	rsqd = round(1 - (ss_res / ss_tot), 4)
	return popt, pcov, perr, rsqd

def calculate(d_data, y_data, n_forecast, title, label):
	# d_data: list of dates in datetime format, sorted
	# y_data: list of numbers (e.g. covid cases) of same length for each date
	# n_forecast: number of days to forecast
	# label: eg 'cases'
	if (len(d_data) != len(y_data)):
		raise Error('d_data and y_data have unequal lengths.')
	size = len(d_data)
	x_data = np.array([i for i in range(size)]) # date integer data

	# print('y_data:')
	# print(y_data)
	# print('d_data:')
	# print(d_data)

	# generate derivative clone without missing values
	xd_data = np.copy(x_data)
	yd_data = np.copy(y_data)
	removal_list = []
	for i in range(size):
		if (y_data[i] == -1):
			removal_list.append(i)
	xd_data = np.delete(xd_data, removal_list)
	yd_data = np.delete(yd_data, removal_list)
	
	# curve fit
	popt, pcov, perr, rsqd = fit(xd_data, yd_data)
	
	# calc ALL curve fit values for 0 thru n-day forecast -> our trajectory
	xf_data = np.array([i for i in range(size + n_forecast)])
	yf_data = model(xf_data, popt[0], popt[1])
	
	# set curve fit values for missing data; useful for visualization
	xm_data = np.copy(xf_data)
	ym_data = np.copy(yf_data)
	removal_list = []
	for i in range(size):
		if (y_data[i] != -1):
			removal_list.append(i)
	xm_data = np.delete(xm_data, removal_list)
	ym_data = np.delete(ym_data, removal_list)
	
	# set curve fit values for projected data; useful for visualization
	xp_data = np.copy(xf_data)
	yp_data = np.copy(yf_data)
	removal_list = []
	for i in range(size):
		if (i < size):
			removal_list.append(i)
	xp_data = np.delete(xp_data, removal_list)
	yp_data = np.delete(yp_data, removal_list)
	
	# generate range of dates
	df_data = np.array([d_data[0] + timedelta(days=i) for i in range(size + n_forecast)])
	
	# generate plot
	fig, ax = plt.subplots()
	#ax = fig.add_subplot(111)
	ax.set_ylim(0,(np.amax(yf_data)*1.07))
	ax.plot(xf_data, yf_data, '--', color ='darkgrey', label ='Model (r^2 = ' + str(rsqd) + ')')
	ax.plot(xd_data, yd_data, 'o', color ='red', label ='Reported Open ' + label)
	ax.plot(xm_data, ym_data, 'o', color ='black', label ='Historical Estimate') 
	ax.plot(xp_data, yp_data, 'o', color ='blue', label ='Projected Estimate') 
	ax.legend()
	ax.set_title(title, fontsize=18, horizontalalignment='center')
	ax.set_xlabel('# Days + ' + d_data[0].strftime('%m/%d/%Y'), fontsize=12)
	ax.set_ylabel('# ' + label, fontsize=12)
	ax.grid(color='gray', linestyle='dotted', linewidth=0.5)
	for i,j in zip(xm_data,ym_data):
		c = 'black'
		if (i >= (size-1)):
			c = 'blue'
		ax.text(i-0.1, j+3, str(int(round(j, 0))), fontsize=8, \
		horizontalalignment='right', color=c)
	# initial value
	if (y_data[0] != -1):
		ax.text(xd_data[0]-0.1, yd_data[0]+3, str(int(round(yd_data[0], 0))), fontsize=8, \
		horizontalalignment='right', color='red')
	else:
		ax.text(xm_data[0]-0.1, ym_data[0]+3, str(int(round(ym_data[0], 0))), fontsize=8, \
		horizontalalignment='right', color='black')
	#ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
	#ax2.set_xlim(df_data[0], df_data[size])
	# x_data = mdates.date2num(dates)
	#fig.tight_layout()
	return plt, popt, rsqd