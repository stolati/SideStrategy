

import math
# this is a hexagonal map class
# With coordinates, we can get what's on the case
# We ca


# cellsize, 

class OffsetType:
	def cube2offset(self, x, y, z): pass
	def offset2cube(self, q, r): pass

class OddROffset(OffsetType):
	pass

class EvenROffset(OffsetType):
	pass

class OddQOffset(OffsetType):
	pass

class EvenQOffset(OffsetType):
	pass


class HexaMapCoordinate:

	def __init__(self, m):
		self.q, self.r, self.m = None, None, m

	@classmethod
	def fromCube(self, x, y, z):
		res = HexaMapCoordinate()
		res.q, res.r = x, z
		return res

	def getCubeCoord(self):
		x, y, z = self.q, self.r
		y = -x-z
		return (x, y, z)


	def getAxialCoord(self):
		#convert cube to axial
		q = x



		return (self.x, self.y)




class HexaMap:
    def __init__(self, cellsize, nbrows, nbcollumns, offset):
        self.cellsize = cellsize
        self.nbrows, self.nbcollumns = nbrows, nbcollumns

    def __getitem__(self, key): pass
    def __setitem__(self, key, item): pass

    def getPoints(self, key):
        for i in range(0, 6):
            angle = 2 * math.pi / 6 * i
            x_i = center_x + size * cos(angle)
            y_i = center_y + size * sin(angle)
            if i == 0:
                moveTo(x_i, y_i)
            else:
                lineTo(x_i, y_i)


