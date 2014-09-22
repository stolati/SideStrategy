



class ViewField(object):
	
	def __init__(self, radius = None):
		self.parent = None
		self.radius = radius # because most of algo have radius

	def getViewPos(self): raise NotImplemented()



class ViewFieldAroundSimple(ViewField):

	def getViewPos(self):
		return self.parent.side._map.getRadius(self.parent.pos, self.radius)



class ViewFieldGroundBlock(ViewField):
	"""Is a field of view with 5 distance, but is blocked by floor"""

	def posIsVisible(self, pos, elem):
		"""Sheet for this moment, just test if one of the neighborour is Air"""
		if not elem.isFloor(): return True

		m = self.parent.playmap._map

		for aroundPos in m.getAround(pos):
			if not m.get(aroundPos).isFloor():
				return True

		return False

	def getViewPos(self):
		for pos in self.parent.side._map.getRadius(self.parent.pos, self.radius):
			if self.posIsVisible(pos, self.parent.playmap._map.get(pos)):
				yield pos


