#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Core tools to utilize JHU's CSSE data
#
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer
from os import listdir, path
from os.path import isfile, join
from csv import reader
import csv
import sys
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter
import random

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

def checkFIPS(fips, v):
	if (fips == '60'):
		# 60010,60,010,Eastern,American Samoa,23030,65124868,349724676,-14.266280,-170.626630
		# 60020,60,020,Manu'a,American Samoa,1143,57620994,464238048,-14.219801,-169.507697
		# 60030,60,030,Rose Island,American Samoa,0,82093,147383995,-14.536530,-168.151292
		# 60040,60,040,Swains Island,American Samoa,17,2432605,149170814,-11.054436,-171.069014
		# 60050,60,050,Western,American Samoa,31329,72498510,196726220,-14.334850,-170.784105
		return '60000' # american samoa
	if (fips == '66'):
		# 66010,66,010,Guam,Guam,159358,543558310,934334983,13.438289,144.772949
		return '66010' # guam
	if (fips == '69'):
		# 69085,69,085,Northern Islands,Northern Mariana Islands,0,160057011,2939509407,18.057948,145.643752
		# 69100,69,100,Rota,Northern Mariana Islands,2527,85098741,539090851,14.152493,145.212904
		# 69110,69,110,Saipan,Northern Mariana Islands,48220,118890998,532767365,15.198095,145.777192
		# 69120,69,120,Tinian,Northern Mariana Islands,3136,108237606,632893009,14.936784,145.601021
		return '69000' # northern mariana islands
	if (fips == '72'):
		# 72001,72,001,Adjuntas Municipio,Puerto Rico Commonwealth,18525,172725728,1051790,18.181611,-66.758165
		# 72003,72,003,Aguada Municipio,Puerto Rico Commonwealth,39470,79923633,38025989,18.375681,-67.183707
		# 72005,72,005,Aguadilla Municipio,Puerto Rico Commonwealth,55722,94613892,101131781,18.480191,-67.143762
		# 72007,72,007,Aguas Buenas Municipio,Puerto Rico Commonwealth,26855,77919490,28383,18.256524,-66.128496
		# 72009,72,009,Aibonito Municipio,Puerto Rico Commonwealth,24008,81094471,71895,18.130647,-66.263974
		# 72011,72,011,Añasco Municipio,Puerto Rico Commonwealth,27892,101747426,14607646,18.286905,-67.131282
		# 72013,72,013,Arecibo Municipio,Puerto Rico Commonwealth,89550,326179591,117205831,18.433923,-66.675055
		# 72015,72,015,Arroyo Municipio,Puerto Rico Commonwealth,18504,38869489,53459916,17.972060,-66.041945
		# 72017,72,017,Barceloneta Municipio,Puerto Rico Commonwealth,24583,48421896,31649450,18.469989,-66.558230
		# 72019,72,019,Barranquitas Municipio,Puerto Rico Commonwealth,29237,88714041,77812,18.198955,-66.309833
		# 72021,72,021,Bayamón Municipio,Puerto Rico Commonwealth,188614,114816256,477626,18.350866,-66.167693
		# 72023,72,023,Cabo Rojo Municipio,Puerto Rico Commonwealth,49726,182264459,277228652,18.008873,-67.209884
		# 72025,72,025,Caguas Municipio,Puerto Rico Commonwealth,134269,151782488,1201689,18.211109,-66.050964
		# 72027,72,027,Camuy Municipio,Puerto Rico Commonwealth,32936,120058280,40430074,18.445469,-66.863134
		# 72029,72,029,Canóvanas Municipio,Puerto Rico Commonwealth,46779,85127784,364681,18.323585,-65.883206
		# 72031,72,031,Carolina Municipio,Puerto Rico Commonwealth,161684,117502258,38734577,18.396776,-65.968778
		# 72033,72,033,Cataño Municipio,Puerto Rico Commonwealth,25595,12629288,5619250,18.444614,-66.148819
		# 72035,72,035,Cayey Municipio,Puerto Rico Commonwealth,45431,134509871,68569,18.103624,-66.151667
		# 72037,72,037,Ceiba Municipio,Puerto Rico Commonwealth,12238,75201651,336178483,18.273749,-65.530895
		# 72039,72,039,Ciales Municipio,Puerto Rico Commonwealth,17325,172310206,459605,18.295913,-66.515588
		# 72041,72,041,Cidra Municipio,Puerto Rico Commonwealth,41181,93294534,1123798,18.174404,-66.161622
		# 72043,72,043,Coamo Municipio,Puerto Rico Commonwealth,39796,202052316,38061,18.103800,-66.357586
		# 72045,72,045,Comerío Municipio,Puerto Rico Commonwealth,19914,73557184,319738,18.225032,-66.219481
		# 72047,72,047,Corozal Municipio,Puerto Rico Commonwealth,34933,110248539,16284,18.303910,-66.326179
		# 72049,72,049,Culebra Municipio,Puerto Rico Commonwealth,1494,30115058,407158805,18.326599,-65.307720
		# 72051,72,051,Dorado Municipio,Puerto Rico Commonwealth,37722,59870098,79238790,18.472661,-66.259585
		# 72053,72,053,Fajardo Municipio,Puerto Rico Commonwealth,33075,77448647,195352764,18.386378,-65.588454
		# 72054,72,054,Florida Municipio,Puerto Rico Commonwealth,12140,39391498,34012,18.369006,-66.561219
		# 72055,72,055,Guánica Municipio,Puerto Rico Commonwealth,17327,95959910,109853315,17.948052,-66.922989
		# 72057,72,057,Guayama Municipio,Puerto Rico Commonwealth,42623,168328028,108327763,17.973929,-66.137468
		# 72059,72,059,Guayanilla Municipio,Puerto Rico Commonwealth,19578,109480387,56911386,18.005263,-66.798357
		# 72061,72,061,Guaynabo Municipio,Puerto Rico Commonwealth,90773,71444631,468304,18.344357,-66.114056
		# 72063,72,063,Gurabo Municipio,Puerto Rico Commonwealth,47074,72228545,1101116,18.272582,-65.981177
		# 72065,72,065,Hatillo Municipio,Puerto Rico Commonwealth,40978,108213684,43975697,18.441141,-66.798210
		# 72067,72,067,Hormigueros Municipio,Puerto Rico Commonwealth,16474,29384893,481,18.134695,-67.116199
		# 72069,72,069,Humacao Municipio,Puerto Rico Commonwealth,54736,115929990,68988203,18.135403,-65.786229
		# 72071,72,071,Isabela Municipio,Puerto Rico Commonwealth,43314,143255845,94636933,18.485170,-67.013463
		# 72073,72,073,Jayuya Municipio,Puerto Rico Commonwealth,15297,115340543,3091,18.211152,-66.586870
		# 72075,72,075,Juana Díaz Municipio,Puerto Rico Commonwealth,47952,156117100,121328720,17.997974,-66.490497
		# 72077,72,077,Juncos Municipio,Puerto Rico Commonwealth,39704,68605410,327694,18.224133,-65.908542
		# 72079,72,079,Lajas Municipio,Puerto Rico Commonwealth,23893,155287823,106643202,17.978511,-67.040111
		# 72081,72,081,Lares Municipio,Puerto Rico Commonwealth,27321,159155302,485277,18.277102,-66.869645
		# 72083,72,083,Las Marías Municipio,Puerto Rico Commonwealth,8874,120071822,376224,18.227594,-66.977580
		# 72085,72,085,Las Piedras Municipio,Puerto Rico Commonwealth,38253,87748363,32509,18.187148,-65.871189
		# 72087,72,087,Loíza Municipio,Puerto Rico Commonwealth,27242,50086873,119822959,18.475039,-65.903280
		# 72089,72,089,Luquillo Municipio,Puerto Rico Commonwealth,18952,66851395,53659423,18.367996,-65.709904
		# 72091,72,091,Manatí Municipio,Puerto Rico Commonwealth,40705,116913007,66163823,18.444803,-66.493137
		# 72093,72,093,Maricao Municipio,Puerto Rico Commonwealth,6180,94851792,12487,18.173956,-66.935547
		# 72095,72,095,Maunabo Municipio,Puerto Rico Commonwealth,11297,54816722,44549509,17.999786,-65.896403
		# 72097,72,097,Mayagüez Municipio,Puerto Rico Commonwealth,79615,201174437,508705758,18.260656,-67.182623
		# 72099,72,099,Moca Municipio,Puerto Rico Commonwealth,37676,130383573,56474,18.377637,-67.079574
		# 72101,72,101,Morovis Municipio,Puerto Rico Commonwealth,31785,100676181,139537,18.319026,-66.420557
		# 72103,72,103,Naguabo Municipio,Puerto Rico Commonwealth,26584,133799723,53351781,18.211070,-65.735749
		# 72105,72,105,Naranjito Municipio,Puerto Rico Commonwealth,29112,70969180,898339,18.289927,-66.253440
		# 72107,72,107,Orocovis Municipio,Puerto Rico Commonwealth,21906,164788358,402899,18.218733,-66.436899
		# 72109,72,109,Patillas Municipio,Puerto Rico Commonwealth,17769,120695652,74074554,18.000311,-65.986643
		# 72111,72,111,Peñuelas Municipio,Puerto Rico Commonwealth,21661,115558555,60210081,18.026618,-66.728125
		# 72113,72,113,Ponce Municipio,Puerto Rico Commonwealth,148863,297688774,203748398,18.001717,-66.606663
		# 72115,72,115,Quebradillas Municipio,Puerto Rico Commonwealth,24548,58747685,30224116,18.466357,-66.927603
		# 72117,72,117,Rincón Municipio,Puerto Rico Commonwealth,14526,37005461,103924383,18.340562,-67.277302
		# 72119,72,119,Río Grande Municipio,Puerto Rico Commonwealth,51768,157008580,74876344,18.376369,-65.798434
		# 72121,72,121,Sabana Grande Municipio,Puerto Rico Commonwealth,23610,94050249,25323,18.084361,-66.947667
		# 72123,72,123,Salinas Municipio,Puerto Rico Commonwealth,29239,179660999,115910809,17.971485,-66.262252
		# 72125,72,125,San Germán Municipio,Puerto Rico Commonwealth,32937,141145018,29360,18.107800,-67.037263
		# 72127,72,127,San Juan Municipio,Puerto Rico Commonwealth,355181,124029911,75277891,18.422363,-66.068094
		# 72129,72,129,San Lorenzo Municipio,Puerto Rico Commonwealth,38689,137547974,256425,18.147107,-65.976167
		# 72131,72,131,San Sebastián Municipio,Puerto Rico Commonwealth,38970,182394904,2060666,18.331409,-66.970678
		# 72133,72,133,Santa Isabel Municipio,Puerto Rico Commonwealth,22475,88144282,111140897,17.952922,-66.387589
		# 72135,72,135,Toa Alta Municipio,Puerto Rico Commonwealth,74169,69972584,1405464,18.364556,-66.244669
		# 72137,72,137,Toa Baja Municipio,Puerto Rico Commonwealth,81905,60201690,48075984,18.456910,-66.193193
		# 72139,72,139,Trujillo Alto Municipio,Puerto Rico Commonwealth,69478,53786135,1592601,18.335387,-66.003787
		# 72141,72,141,Utuado Municipio,Puerto Rico Commonwealth,30209,294045388,3982230,18.270865,-66.702989
		# 72143,72,143,Vega Alta Municipio,Puerto Rico Commonwealth,38589,71816290,25307600,18.436163,-66.336673
		# 72145,72,145,Vega Baja Municipio,Puerto Rico Commonwealth,54754,118777657,57795017,18.455128,-66.397883
		# 72147,72,147,Vieques Municipio,Puerto Rico Commonwealth,8931,131527813,552206400,18.125418,-65.432474
		# 72149,72,149,Villalba Municipio,Puerto Rico Commonwealth,23659,92298569,3622637,18.130719,-66.472244
		# 72151,72,151,Yabucoa Municipio,Puerto Rico Commonwealth,35025,143005178,72592521,18.059858,-65.859871
		# 72153,72,153,Yauco Municipio,Puerto Rico Commonwealth,37585,175371914,1625260,18.085669,-66.857901
		return '72000' # puerto rico
	if (fips == '78'):
		# 78010,78,010,St. Croix,U.S. Virgin Islands,50601,215914994,645644841,17.735232,-64.746644
		# 78020,78,020,St. John,U.S. Virgin Islands,4170,50996518,186671948,18.330435,-64.735261
		# 78030,78,030,St. Thomas,U.S. Virgin Islands,51634,81102199,717927568,18.326748,-64.971251
		return '78000' # virgin islands
	if len(fips) == 4: fips = '0' + fips
	if fips == '': fips = '99999'
	assert len(fips) == 5, 'WARNING: FIPS != 5 Digits: ' + fips + ' | ' + str(v)
	return fips
	
def checkGlobalData(world, n_rows):
	print('Checking Global Data...')
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

# return array of indices from the array provided, e.g. [0, 1, 2, 3, 4...]
def getIndexR(data, shift = 0):
	# eg shift = 1, means array will start with 1 e.g. [1, 2, 3, 4...] but be of same length
	temp = np.array([i for i in range(len(data))])
	if shift == 0: return temp
	temp += shift
	return temp

# this will ingest the JHU 'CONFIRMED' time series file into the data structure
def ingestGlobalData(world, basepath, smooth = True):
	print('Ingesting Global Data...')
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
					s.setData(label, data, smooth)
					s.a['adm1'] = v[1]
					s.a['adm2'] = v[0]
				else:
					if (v[1] != 'US'): # skip US because it will be handled in the national pull
						c.setData(label, data, smooth)
			i += 1
		n_rows = i-1
		n_row_max = max(n_row_max, n_rows)
		print('    # Rows (' + label + '): ' + str(n_rows))
		print('    # Countries (' + label + '): ' + str(world.numAreas()))
	return n_row_max

# US only
def ingestNationalData(world, basepath, smooth = True):
	crDB = loadCountyReference()
	srDB = loadStateReference()
	print('Ingesting National Data...')
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
		geoAdjusts = 0
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
					s.setData(label, data, smooth)
				else: # county or ADM3
					s = s.areaFactory(v[5], float(v[8]), float(v[9])) # factory (get or create)
					s.setData(label, data, smooth)
					s.a['adm1'] = v[7] # 'US'
					s.a['adm2'] = v[6]
					s.a['adm3'] = v[5]
				# check FIPS
				s.a['fips'] = checkFIPS(v[4].replace('.0',''), v)
				# check LAT/LON; snap to US county reference which is better or fall back to US state
				cr = crDB.get(s.a['fips'])
				if cr == None:
					if s.a['key'].startswith('Unassigned, ') or s.a['key'].startswith('Out of '):
						# eg 'Out of RI, Rhode Island, US'
						# eg 'Unassigned, Wisconsin, US'
						temp = s.a['key'].split(',')[1].strip()
						sr = srDB[2].get(temp)
						assert sr != None, 'State ' + temp + ' unrecognized!'
						geoAdjusts += 1
						s.a['lat'] = round(float(sr['LAT']), 6)
						s.a['lon'] = round(float(sr['LON']), 6)
					else:
						# check state reference (guam, virgin islands, etc... where county is not disclosed)
						temp = s.a['key'].split(',')[0].strip()
						sr = srDB[2].get(temp)
						if sr != None:
							geoAdjusts += 1
							s.a['lat'] = round(float(sr['LAT']), 6)
							s.a['lon'] = round(float(sr['LON']), 6)
						else:
							print('      CR WARNING: ' + s.a['fips'] + ':' + s.a['key'])
							s.a['lat'] = 0.0
							s.a['lon'] = 0.0
				else:
					if (s.a['lat'] != cr['Lat'] or s.a['lon'] != cr['Lon']): geoAdjusts += 1
					s.a['lat'] = round(float(cr['Lat']), 6)
					s.a['lon'] = round(float(cr['Lon']), 6)
			i += 1
		n_rows = i-1
		print('    # Geo Adjustments (' + label + '): ' + str(geoAdjusts))
		print('    # Rows (' + label + '): ' + str(n_rows))
		print('    # Countries (' + label + '): ' + str(world.numAreas()))
	return n_rows

def ingestData(basepath, name = 'World'):
	# ingest data
	world = cs.World(name) # root object for data hierarchy
	try:
		n_rows = ingestGlobalData(world, basepath) # ingest the latest global time series data
		checkGlobalData(world, n_rows) # check data structure
		ingestNationalData(world, basepath) # ingest the latest US time series data
		# will refresh and cascade subtotals
		for label in ['CONFIRMED', 'DEATHS', 'RECOVERED']:
			world.getData(label, True)
	except FormatError:
		print('Ingestion Problems...  Halting.')
		sys.exit(1)
	# return world
	return world

def loadCountyReference():
	print('Loading County Reference CSV Resource...')
	db = {}
	datafile = path.abspath(path.join(path.dirname(__file__), '../data/resources/us_counties.csv'))
	n = 0
	with open(datafile, 'r', encoding='utf-8-sig') as csvfile:
		for line in csv.DictReader(csvfile):
			db[line['KEY']] = line
	print('  # Counties: ' + str(len(db)))
	return db

def loadStateReference():
	print('Loading State Reference CSV Resource...')
	db = [{}, {}, {}] # by FIPS, by STATE ABBR, by STATE NAME
	datafile = path.abspath(path.join(path.dirname(__file__), '../data/resources/states.csv'))
	n = 0
	with open(datafile, 'r', encoding='utf-8-sig') as csvfile:
		for line in csv.DictReader(csvfile):
			db[0][line['KEY']] = line
			db[1][line['ABBR']] = line
			db[2][line['STATE']] = line
	print('  # States and Territories: ' + str(len(db[0])))
	return db

# add 2 numpy arrays, b into a, preserving a's length
def addArrays(a, b):
	for i in range(len(b)):
		if i > len(a): break
		a[i] += b[i]
	return a

# sum 2 numpy arrays with the result having the longest length
def sumArrays(a, b):
	if len(a) < len(b):
		c = b.copy()
		c[:len(a)] += a
	else:
		c = a.copy()
		c[:len(b)] += b
	return c

def simplePlot(area, title, filename, v_thresh = 0, yscale = 'log', xaxis = 'Day'):
	fig, ax = plt.subplots()
	# custom x labels
	if (False):
		custom_labels = []
		for i in range(len(xm_data)):
			custom_labels.append((d_data[0] + timedelta(days=i)).strftime('%m/%d')) # + ' (+' + str(i) + ')')
		plt.xticks(xm_data, custom_labels, rotation='vertical')
	ax.margins(0.08)
	plt.subplots_adjust(bottom=0.20, left=0.30)
	# footer
	plt.text(1, -0.28,'Data: JHU CSSE - https://bit.ly/2wP8tQY\nCode: COVID-19-TOOLS - https://bit.ly/3bJDxQT', fontsize=8, \
		horizontalalignment='right', color='gray', transform=ax.transAxes)
	plt.text(-0.2, -0.28, 'Generated: ' + datetime.now().strftime('%m/%d/%Y %H:%M EST') + '\nLicense: CC Zero v1.0 Universal', fontsize=8, \
		horizontalalignment='left', color='gray', transform=ax.transAxes)
	# axis prep
	ax.set_yscale(yscale)
	ax.yaxis.set_major_formatter(ScalarFormatter()) # override log formatter
	ax.set_xticks(np.arange(1, (getIndexR(area.getData('CONFIRMED', v_thresh), 1)[-1]+3), step=5))
	ax.grid(color='gray', linestyle='dotted', linewidth=0.5)
	# lines
	ax.plot(getIndexR(area.getData('CONFIRMED', v_thresh), 1), area.getData('CONFIRMED', v_thresh), '-', color ='blue', label ='Confirmed')
	ax.plot(getIndexR(area.getData('CONFIRMED', v_thresh), 1)[-1], area.getData('CONFIRMED', v_thresh)[-1], 'o', color = 'blue')
	ax.plot(getIndexR(area.getData('DEATHS', v_thresh), 1), area.getData('DEATHS', v_thresh), '-', color ='red', label ='Deaths')
	ax.plot(getIndexR(area.getData('DEATHS', v_thresh), 1)[-1], area.getData('DEATHS', v_thresh)[-1], 'o', color = 'red')
	# annotate # area.world.getDates()[-1].strftime('%m/%d/%Y')
	ax.annotate(area.getData('CONFIRMED', v_thresh)[-1], xy=(getIndexR(area.getData('CONFIRMED', v_thresh), 1)[-1], \
		area.getData('CONFIRMED', v_thresh)[-1]), xycoords='data', xytext=(-3,4), textcoords='offset points', \
		fontsize=8, horizontalalignment='right', color='blue')
	ax.annotate(area.getData('DEATHS', v_thresh)[-1], xy=(getIndexR(area.getData('DEATHS', v_thresh), 1)[-1], \
		area.getData('DEATHS', v_thresh)[-1]), xycoords='data', xytext=(-3,4), textcoords='offset points', \
		fontsize=8, horizontalalignment='right', color='red')
	# labels
	ax.legend()
	ax.set_title(title, fontsize=14, horizontalalignment='center')
	ax.set_xlabel(xaxis, fontsize=10)
	ax.set_ylabel('# ' + 'People', fontsize=10)
	# save
	plt.savefig(filename)
	plt.close(fig)
	
def multiPlot(areas, label, title, filename, v_thresh = 0, yscale = 'log', xaxis = 'Day', overlay=['avg','sum']):
	fig, ax = plt.subplots()
	ax.margins(0.08)
	plt.subplots_adjust(bottom=0.20, left=0.30)
	# footer
	plt.text(1, -0.28,'Data: JHU CSSE - https://bit.ly/2wP8tQY\nCode: COVID-19-TOOLS - https://bit.ly/3bJDxQT', fontsize=8, \
		horizontalalignment='right', color='gray', transform=ax.transAxes)
	plt.text(-0.2, -0.28, 'Generated: ' + datetime.now().strftime('%m/%d/%Y %H:%M EST') + '\nLicense: CC Zero v1.0 Universal', fontsize=8, \
		horizontalalignment='left', color='gray', transform=ax.transAxes)
	# axis prep
	ax.set_yscale(yscale)
	ax.yaxis.set_major_formatter(ScalarFormatter()) # override log formatter
	ax.grid(color='gray', linestyle='dotted', linewidth=0.5)
	# compute avg or sum
	if 'avg' in overlay or 'sum' in overlay:
		sum = np.zeros(1000)
		shortest = 1000
		longest = 0
		for k, area in areas.items():
			temp = area.getData(label, v_thresh)
			sum = addArrays(sum, temp)
			if len(temp) < shortest: shortest = len(temp)
			if len(temp) > longest: longest = len(temp)
		sum = sum[:longest].copy()
		avg = sum[:shortest].copy()
		avg /= len(areas)
		if 'avg' in overlay: ax.plot(getIndexR(avg, 1), avg, '-.', color = 'black', label = 'Average')
		if 'sum' in overlay: ax.plot(getIndexR(sum, 1), sum, '--', color = 'black', label = 'Sum')
	# x-ticks
	ax.set_xticks(np.arange(1, longest+3, step=5))
	# lines
	for i, (k, area) in enumerate(areas.items()):
		#print(k + ' >> ' + str(area))
		r = random.random()
		b = random.random()
		g = random.random()
		c = (r, g, b)
		ax.plot(getIndexR(area.getData(label, v_thresh), 1), area.getData(label, v_thresh), '-', color = c, label = area.name())
		ax.plot(getIndexR(area.getData(label, v_thresh), 1)[-1], area.getData(label, v_thresh)[-1], 'o', color = c)
		# annotate highest # area.world.getDates()[-1].strftime('%m/%d/%Y')
		# if i == 0: 
			# ax.annotate(area.getData(label, v_thresh)[-1], xy=(getIndexR(area.getData(label, v_thresh), 1)[-1], \
				# area.getData(label, v_thresh)[-1]), xycoords='data', xytext=(-3,4), textcoords='offset points', \
				# fontsize=8, horizontalalignment='right', color='black')
	# labels
	ax.legend(prop={'size': 7})
	ax.set_title(title, fontsize=14, horizontalalignment='center')
	ax.set_xlabel(xaxis, fontsize=10)
	ax.set_ylabel('# ' + 'People', fontsize=10)
	# save
	plt.savefig(filename)
	plt.close(fig)

# tests
if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	# export (assumes JHU's COVID-19 is installed under the root directory as COVID-19-TOOLS)
	basepath = path.abspath(path.join(path.dirname(__file__), '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'))
	world = ingestData(basepath)
	world.exportStandard(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_standard.txt')))
	world.exportTransposed(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_transposed.txt')))
	
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