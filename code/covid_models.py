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
import statsmodels.formula.api as smf
#import math

class Error(Exception):
	# Base class for exceptions in this module.
	pass

class ModelError(Error):
	"""Exception raised for errors in using the framework.
	
	Attributes:
		expression -- input expression in which the error occurred
		message -- explanation of the error
	"""
	
	def __init__(self, expression, message = ''):
		self.expression = expression
		self.message = message

class Model:
	
	def __init__(self, type = '?'):
		self.a = {} # attributes
		self.a['type'] = type

class Model_T1(Model):
	
	def __init__(self):
		super().__init__('T1')
		self.stats_i = 0 # index
		self.resetStats(100)
	
	def calculate(self, d_data, y_data, label = 'DEFAULT', n_forecast = 0, r_thresh = 0.80, \
		y_thresh = 1, debug = False):
		# d_data: list of dates in datetime format MM/DD/YYYY, pre sorted
		# y_data: list of numbers (e.g. covid cases) of same length for each date
		# label: label to apply for stat keeping, or None to skip
		# n_forecast: number of days to forecast
		# r_thresh: >= r-squared threshhold to run calculation range and update stats
		# y_thresh: >= starting index y threshhold, e.g. 1 confirmed case
		# debug: print additional lines
		
		self.a['last_error'] = None
		# check data length
		if (len(d_data) != len(y_data)):
			raise ModelError('d_data and y_data have unequal lengths.')
		size = len(d_data)
		x_data = np.array([i for i in range(size)]) # date integer data (days since)
		
		if (debug): 
			print('d_data size:', size)
			# print('d_data:')
			# if (debug): print(d_data)
			# if (debug): print('x_data:')
			# if (debug): print(x_data)
			print('y_data:')
			print(y_data)
		
		# determine starting index where y_data >= threshhold
		si = -1
		for i in range(len(y_data)):
			if (y_data[i] >= y_thresh): 
				si = i
				break
		if (si == -1):
			# threshhold not met; return with result
			self.a['last_error'] = 'si threshhold not met'
			return None, -1, None, None, si
		if (debug): 
			print('si:', si, 'y_data[si]:', y_data[si])
			print('x_data[si:]:')
			print(x_data[si:])
			print('y_data[si:]:')
			print(y_data[si:])
			print('x_data[si:]-si:')
			print(x_data[si:]-si)
			print('y_data[si:] / y_data[si]:')
			print(y_data[si:] / y_data[si])
		
		# curve fit
		rsqd = -1
		try:
			popt, pcov, perr, rsqd = self.fitWrapper(x_data[si:]-si, y_data[si:] / y_data[si])
			if (rsqd < -1): rsqd = -1
			rsqd = round(rsqd, 3)
			if (debug): print('*', rsqd)
			
			if (rsqd > r_thresh):
				# calc ALL curve fit values for 0 thru n-day forecast -> our trajectory
				xm_data = np.array([i for i in range(size - si + 0)]) # n_forecast
				if (debug): print('lens:', len(xm_data), len(y_data[si:]))
				ym_data = Model_T1.equation(xm_data, *popt) * y_data[si]
				ym_data = np.rint(ym_data) # since we want to force integer estimates
				# update stats
				if (label != None):
					self.a[label][self.stats_i] = (rsqd, popt[0], popt[1], popt[2])
					self.stats_i += 1
					# auto expand by doubling
					if (self.stats_i == len(self.a[label])-1):
						temp = np.zeros((len(self.a[label]), 4))
						self.a[label] = np.concatenate(self.a[label], temp, axis=0)
					self.a['last_error'] = None
				if (debug): 
					print('xm_data:')
					print(xm_data)
					print('ym_data:')
					print(ym_data)
				return popt, rsqd, xm_data, ym_data, si
			else:
				return popt, rsqd, None, None, si
		
		except RuntimeError:
			self.a['last_error'] = 'RuntimeError'
			#raise
			return None, -1, None, None, si
		except TypeError:
			self.a['last_error'] = 'TypeError'
			#raise
			return None, -1, None, None, si
		except IndexError:
			self.a['last_error'] = 'IndexError'
			#raise
			return None, -1, None, None, si
	
	@staticmethod
	def equation(x, a, b, c):
		y = a * np.exp(b * x) + c
		return y
	
	def fitWrapper(self, x_data, y_data):
		popt, pcov = curve_fit(Model_T1.equation, x_data, y_data, method='dogbox', maxfev=2000)
		temp = np.diag(pcov)
		perr = None
		#if (temp.all() > 0.0001): perr = np.sqrt(np.diag(pcov))
		# residual sum of squares
		residuals = y_data - Model_T1.equation(x_data, *popt)
		ss_res = np.sum(residuals**2)
		# total sum of squares
		ss_tot = np.sum((y_data-np.mean(y_data))**2)
		# r-squared
		if (ss_tot == 0):
			rsqd = -1
		else:
			rsqd = round(1 - (ss_res / ss_tot), 4)
		return popt, pcov, perr, rsqd
	
	def resetStats(self, size_estimate = 100, label_list = ['DEFAULT']):
		self.stats_i = 0 # index
		for label in label_list:
			self.a[label] = np.zeros((size_estimate, 4)) # float / columns = rsqd, a, b, c
			self.a[label][:] = np.nan # fill all as NaN