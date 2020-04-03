class image:
	file = None
	
	def __init__(self, v, filename, type, p, rsqd, rerr):
		self.v = v # dictionary of record properties
		self.filename = filename
		self.type = type
		self.p = p
		self.rsqd = rsqd
		self.rerr = rerr