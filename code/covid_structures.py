#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Core class structures for JHU CSSE's Time Series Data Files
#
import numpy as np
from datetime import datetime
from datetime import timedelta

class Error(Exception):
	"""Base class for exceptions in this module."""
	pass
	
class UsageError(Error):
	"""Exception raised for errors in using the framework.
	
	Attributes:
		expression -- input expression in which the error occurred
		message -- explanation of the error
	"""
	
	def __init__(self, expression, message = ''):
		self.expression = expression
		self.message = message

# basic lat/lon attributes
class Place:
	
	def __init__(self, lat, lon):
		self.a = {} # attributes
		self.a['lat'] = round(lat, 6)
		self.a['lon'] = round(lon, 6)
	
	def lat(self):
		return self.a['lat']
		
	def lon(self):
		return self.a['lat']
	
	def __str__(self):
		return self.a['lat'] + ',' + self.a['lon']

# workhorse used for ADM1, ADM2, ADM3, ...
class Area(Place):
	
	def __init__(self, parent, name, lat=0.0, lon=0.0):
		super().__init__(lat, lon)
		self.__parent = parent # parent obj
		self.a['name'] = name
		self.a['level'] = -1 # -1 is undefined and unset
		self.a['key'] = name
		self.a['adm1'] = 'N/A'
		self.a['adm2'] = 'N/A'
		self.a['adm3'] = 'N/A'
		self.a['fips'] = 'N/A'
		self.__s = {} # subordinate areas; no dupes possible
		self.__t = {} # total data for data type, includes self and subordinates
	
	def areaFactory(self, name, lat=0.0, lon=0.0): 
		# factory class
		if (name in self.__s): return self.__s[name]
		ar = Area(self, name, lat, lon)
		if (type(ar) != Area): raise TypeError('Area added not of type \'Area\'')
		if (self.a['level'] == -1): raise UsageError('Parent level not set.')
		ar.a['level'] = self.a['level'] + 1
		ar.world = self.world
		if (ar.a['level'] > 1): ar.a['key'] = name + ', ' + self.a['key']
		self.__s[ar.name()] = ar
		return ar
		
	def areas(self):
		for k in sorted(self.__s.keys()):
			yield self.__s.get(k)
	
	def debug(self):
		for k in self.a:
			print('A' + str(self.a['level']) + ': ' + str(k) + ':' + str(self.a[k]))
		for k in self.__s:
			print('S' + str(self.a['level']) + ': ' + str(k) + ':' + str(self.__s[k]))
	
	def getArea(self, name):
		if (name in self.__s): return self.__s[name]
		return None
	
	def getAreas(self):
		return self.__s
	
	def getData(self, label, recalculate = False):
		#print('=================')
		#print('s.getData()', self.a['name'], label, self.world.lenData())
		#self.debug()
		#print('=================')
		if (label not in self.__t or recalculate):
			self.__t[label] = np.zeros(self.world.lenData(), dtype = int)
			if (label in self.a): self.__t[label] += self.a[label]
			for a in self.areas(): # next level, e.g. 2 or 3, if it exists
				temp = a.getData(label, recalculate)
				#print('>>>', temp)
				if (type(temp) == np.ndarray): self.__t[label] += temp
				#a.debug()
				#print('-------------------------------------')
		return self.__t[label]
	
	def getParent(self):
		return self.__parent
	
	def hasAreas(self):
		if (len(self.__s) > 0): return True
		return False
	
	def hasData(self, label):
		if (label in self.a): return True
		return False
	
	def key(self):
		return self.a['key']
	
	def level(self):
		return self.a['level']
	
	def name(self):
		return self.a['name']
	
	def numAreas(self):
		return len(self.__s)
	
	def __str__(self):
		s = self.a['name'] + '[' + str(self.a['level']) + ':' + str(len(self.__s)) + ']'
		return s
	
	def setData(self, label, data):
		self.a[label] = data

# world root area, which has no parent
class World(Area):
	
	def __init__(self, name='World', lat=0.0, lon=0.0):
		super().__init__(None, name, lat, lon)
		self.a['level'] = 0
		self.a['fips'] = 'N/A'
		self.__dates = [] # date data
		self.world = self
	
	def exportStandard(self, filename):
		print('Exporting (Standard) World [' + filename + ']...')
		fileout = open(filename,'w')
		n = 0
		d = {} # data
		d['DA'] = self.getDates()
		s = 'N|FIPS|ADM3|ADM2|ADM1|KEY|LAT|LON|T'
		for i in range(self.lenData()):
			s += '|' + d['DA'][i].strftime('%m/%d/%Y')
		fileout.write(s + '\n')
		d['C'] = self.getData('CONFIRMED')
		d['D'] = self.getData('DEATHS')
		d['R'] = self.getData('RECOVERED')
		for t in ['C','D','R']:
			n += 1
			s = str(n) + '|' + self.a['fips'] + '|N/A|N/A|N/A|' + self.a['key'] + '|' + str(self.a['lat']) + '|' + \
				str(self.a['lon']) + '|' + t
			for i in range(self.lenData()):
				n += 1
				s += '|' + str(d[t][i])
			fileout.write(s + '\n')
		for s1 in self.areas():
			d['C'] = s1.getData('CONFIRMED')
			d['D'] = s1.getData('DEATHS')
			d['R'] = s1.getData('RECOVERED')
			for t in ['C','D','R']:
				n += 1
				s = str(n) + '|' + s1.a['fips'] + '|' + s1.a['adm3'] + '|' + s1.a['adm2'] + '|' + s1.a['adm1'] + '|' + \
					s1.a['key'] + '|' + str(s1.a['lat']) + '|' + str(s1.a['lon']) + '|' + t
				for i in range(self.lenData()):
					n += 1
					s += '|' + str(d[t][i])
				fileout.write(s + '\n')
			for s2 in s1.areas():
				d['C'] = s2.getData('CONFIRMED')
				d['D'] = s2.getData('DEATHS')
				d['R'] = s2.getData('RECOVERED')
				for t in ['C','D','R']:
					n += 1
					s = str(n) + '|' + s2.a['fips'] + '|' + s2.a['adm3'] + '|' + s2.a['adm2'] + '|' + s2.a['adm1'] + '|' + \
						s2.a['key'] + '|' + str(s2.a['lat']) + '|' + str(s2.a['lon']) + '|' + t
					for i in range(self.lenData()):
						n += 1
						s += '|' + str(d[t][i])
					fileout.write(s + '\n')
				for s3 in s2.areas():
					d['C'] = s3.getData('CONFIRMED')
					d['D'] = s3.getData('DEATHS')
					d['R'] = s3.getData('RECOVERED')
					for t in ['C','D','R']:
						n += 1
						s = str(n) + '|' + s3.a['fips'] + '|' + s3.a['adm3'] + '|' + s3.a['adm2'] + '|' + s3.a['adm1'] + '|' + \
							s3.a['key'] + '|' + str(s3.a['lat']) + '|' + str(s3.a['lon']) + '|' + t
						for i in range(self.lenData()):
							n += 1
							s += '|' + str(d[t][i])
						fileout.write(s + '\n')
		fileout.close()
	
	def exportTransposed(self, filename):
		print('Exporting (Transposed) World [' + filename + ']...')
		fileout = open(filename,'w')
		n = 0
		d = {} # data
		d['DA'] = self.getDates()
		fileout.write('N|FIPS|ADM3|ADM2|ADM1|DATE|KEY|LAT|LON|CONFIRMED|DEATHS|RECOVERED\n')
		d['C'] = self.getData('CONFIRMED')
		d['D'] = self.getData('DEATHS')
		d['R'] = self.getData('RECOVERED')
		for i in range(self.lenData()):
			n += 1
			s = str(n) + '|' + self.a['fips'] + '|N/A|N/A|N/A|' + d['DA'][i].strftime('%m/%d/%Y') + '|' + self.a['key'] + \
				'|' + str(self.a['lat']) + '|' + str(self.a['lon']) + '|' + str(d['C'][i]) + '|' + str(d['D'][i]) + \
				'|' + str(d['R'][i])
			fileout.write(s + '\n')
		for s1 in self.areas():
			d['C'] = s1.getData('CONFIRMED')
			d['D'] = s1.getData('DEATHS')
			d['R'] = s1.getData('RECOVERED')
			for i in range(self.lenData()):
				n += 1
				s = str(n) + '|' + s1.a['fips'] + '|' + s1.a['adm3'] + '|' + s1.a['adm2'] + '|' + s1.a['adm1'] + \
					'|' + d['DA'][i].strftime('%m/%d/%Y') + '|' + s1.a['key'] + '|' + \
					str(s1.a['lat']) + '|' + str(s1.a['lon']) + '|' + str(d['C'][i]) + '|' + str(d['D'][i]) + '|' + str(d['R'][i])
				fileout.write(s + '\n')
			for s2 in s1.areas():
				d['C'] = s2.getData('CONFIRMED')
				d['D'] = s2.getData('DEATHS')
				d['R'] = s2.getData('RECOVERED')
				for i in range(self.lenData()):
					n += 1
					s = str(n) + '|' + s2.a['fips'] + '|' + s2.a['adm3'] + '|' + s2.a['adm2'] + '|' + s2.a['adm1'] + \
						'|' + d['DA'][i].strftime('%m/%d/%Y') + '|' + s2.a['key'] + '|' + \
						str(s2.a['lat']) + '|' + str(s2.a['lon']) + '|' + str(d['C'][i]) + '|' + str(d['D'][i]) + '|' + str(d['R'][i])
					fileout.write(s + '\n')
				for s3 in s2.areas():
					d['C'] = s3.getData('CONFIRMED')
					d['D'] = s3.getData('DEATHS')
					d['R'] = s3.getData('RECOVERED')
					for i in range(self.lenData()):
						n += 1
						s = str(n) + '|' + s3.a['fips'] + '|' + s3.a['adm3'] + '|' + s3.a['adm2'] + '|' + s3.a['adm1'] + \
							'|' + d['DA'][i].strftime('%m/%d/%Y') + '|' + s3.a['key'] + '|' + \
							str(s3.a['lat']) + '|' + str(s3.a['lon']) + '|' + str(d['C'][i]) + '|' + str(d['D'][i]) + '|' + str(d['R'][i])
						fileout.write(s + '\n')
		fileout.close()
	
	def getDates(self):
		return self.__dates
	
	def lenData(self):
		return len(self.__dates)
	
	def setDates(self, startDate, length):
		self.__dates = [datetime.now() for i in range(length)]
		self.__dates[0] = startDate
		for i in range(1, length):
			self.__dates[i] = self.__dates[i-1] + timedelta(days=1)

# tests
if __name__ == '__main__':
	w = World()
	c = w.areaFactory('Australia', 25.2744, 133.7751)
	print(c)
	print(c.name())
	print(c.numAreas())
	s = c.areaFactory('Tasmania', -41.4545, 145.9707)
	print(s, s.name(), s.lat())
	print('#####')
	print(c.numAreas())
	s = c.areaFactory('Victoria', -37.8136, 144.9631)
	print(c.numAreas())
	print(c.lat())
	print('=====')
	for s in c.areas():
		print(s)
	print('=====')
	c = w.areaFactory('Canada', 53.9333, -116.5765)
	s = c.areaFactory('Alberta', 53.9333, -116.5765)
	s = c.areaFactory('Alberta', 53.9333, -116.5765)
	s = c.areaFactory('Alberta', 53.9333, -116.5765)
	s = s.areaFactory('Smaller', 53.9333, -116.5765)
	s = s.areaFactory('Smallest', 53.9333, -116.5765)
	print('=====')
	for c in w.areas():
		print(str(c) + ' ' + c.key())
		for s1 in c.areas():
			print('1	' + str(s1) + ' ' + s1.key())
			for s2 in s1.areas():
				print('2		' + str(s2) + ' ' + s2.key())
				for s3 in s2.areas():
					print('3			' + str(s3) + ' ' + s3.key())
