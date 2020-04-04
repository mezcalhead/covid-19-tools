import numpy as np

class Place:
	def __init__(self, name, lat, lon):
		self.__a = {} # attributes
		self.__a['lat'] = round(lat, 6)
		self.__a['lon'] = round(lon, 6)
	
	def lat(self):
		return self.__a['lat']
		
	def lon(self):
		return self.__a['lat']
	
	def __str__(self):
		return self.__a['lat'] + ',' + self.__a['lon']

class Country(Place):
	__hash = {} # all countries; no dupes possible
	__len = 0 # the length of the data to expect
	
	def __init__(self, name, lat, lon):
		super().__init__(self, lat, lon)
		self.__a = {} # attributes
		self.__a['name'] = name
		self.__a['level'] = 1
		self.__s = {} # subordinate areas; no dupes possible
		Country.__hash[name] = self
	
	def addSub(self, sub):
		if (type(sub) != Subdivision): raise TypeError()
		sub.cascade(2)
		self.__s[sub.name()] = sub
	
	@staticmethod
	def create(name, lat, lon): 
		# factory class
		if (name in Country.__hash):
			return Country.__hash[name]
		else:
			c = Country(name, lat, lon)
			return c
	
	@staticmethod
	def getCountry(name):
		if (name in Country.__hash):
			return Country.__hash[name]
		else:
			return None
	
	def getData(self, label):
		self.totalData = np.zeros(__len)
		for s1 in self.subs():
			temp = s1.getData(label)
			if (temp != None): self.totalData += temp
			for s2 in s1.subs():
				temp = s2.getData(label)
				if (temp != None): self.totalData += temp
		return self.totalData
	
	def hasSubs(self):
		if (len(self.__s) == 0):
			return False
		else:
			return True
	
	@staticmethod
	def lenData(self):
		return self.__len
	
	def level(self):
		return self.__a['level']
	
	def name(self):
		return self.__a['name']
	
	@staticmethod
	def numCountries():
		return len(Country.__hash)
	
	def numSubs(self):
		return len(self.__s)
	
	def setData(label, data):
		self.__s[label] = data
	
	@staticmethod
	def setLenData(length):
		self.__len = length
	
	def __str__(self):
		return self.__a['name']
	
	def subs(self):
		for k in sorted(self.__s.keys()):
			yield self.__s.get(k)
	
	@staticmethod
	def all():
		for k in sorted(Country.__hash.keys()):
			yield Country.__hash.get(k)

class Subdivision(Place):
	
	def __init__(self, name, lat, lon):
		super().__init__(self, lat, lon)
		self.__a = {} # attributes
		self.__a['name'] = name
		self.__a['level'] = 0 # unset
		self.__s = {} # subordinate areas; no dupes possible
	
	def addSub(self, sub):
		if (type(sub) != Subdivision): raise TypeError()
		sub.__a['level'] = self.__a['level'] + 1
		self.__s[sub.name] = sub
	
	def cascade(self, level):
		self.__a['level'] = level
		for v in self.__s.items():
			v.__cascade(self, level+1)
	
	def getData(label):
		if (label not in self.__s): self.__s[label] = None
		return self.__s[label]
	
	def level(self):
		return self.__a['level']
	
	def name(self):
		return self.__a['name']
	
	def setData(label, data):
		self.__s[label] = data
	
	def __str__(self):
		return self.__a['name']
	
	def subs(self):
		for k in sorted(self.__s.keys()):
			yield self.__s.get(k)

if __name__ == '__main__':
	c = Country('Australia', 25.2744, 133.7751)
	print(c)
	print(c.name())
	print(c.numSubs())
	s = Subdivision('Tasmania', -41.4545, 145.9707)
	print(s, s.name(), s.lat())
	c.addSub(s)
	print('#####')
	print(c.numSubs())
	s = Subdivision('Victoria', -37.8136, 144.9631)
	c.addSub(s)
	print(c.numSubs())
	print(c.lat())
	print('=====')
	for s in c.subs():
		print(s)
	print('=====')
	for x in c.all():
		print(x)
	c2 = Country('Canada', 53.9333, -116.5765)
	s = Subdivision('Alberta', 53.9333, -116.5765)
	c2.addSub(s)
	for x in Country.all():
		print(x)
		for s in x.subs():
			print('	' + str(s) + ' ' + str(s.level()))
	