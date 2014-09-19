



class ViewField:
	
	def __init__(self):
		self.parent = None

	def getViewPos(self): raise NotImplemented()




class ViewFieldUnderground(ViewField):

	def getViewPos(self):
		# When underground, return 3 around ourselves
		# without anything else
		return self.parent.side._map.getRadius(self.parent.pos, 3)


class ViewFieldBasic(ViewField):

	def getViewPos(self):
		return self.parent.side._map.getRadius(self.parent.pos, 5)

