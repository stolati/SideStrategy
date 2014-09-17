

from utils import *


# This file is referency maps with there own algorythms
# Most of the algo come from http://www.redblobgames.com/grids/hexagons/#rings 

class MapType:

    def getAround(self, pos): return self.getRadius(pos, 1)
    def pixel2pos(self, pixelPos, sizeCellWidth, sizeCellHeight): raise NotImplemented()
    def pos2pixel(self, pos, sizeCellWidth, sizeCellHeight): raise NotImplemented()

    def getRadius(self, pos, radius): raise NotImplemented()


class Squared(MapType):

    def getAround(self, pos):
        around = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0)]
        for delta in around:
            yield pos + delta

    def getRadius(self, pos, radius):
        for x in range(pos.x - radius, pos.x + radius + 1):
            for y in range(pos.y - radius, pos.y + radius + 1):
                yield Pos(x, y)

    def pixel2pos(self, pixelPos, sizeCellWidth, sizeCellHeight):

        xres = pixelPos.x // sizeCellWidth
        yres = pixelPos.y // sizeCellHeight
        return Pos(int(xres), int(yres))


    def pos2pixel(self, pos, sizeCellWidth, sizeCellHeight):
        return (pos.x * sizeCellWidth, pos.y * sizeCellHeight)


class Hexagonal(MapType):

    def RQ2XYZ(self, r, q): raise NotImplemented()
    def XYZ2RQ(self, x, y, z): raise NotImplemented()

    def getAround(self, pos):
        """Should work but don't"""
        neighbors = [
            (+1, -1,  0), (+1,  0, -1), ( 0, +1, -1),
            (-1, +1,  0), (-1,  0, +1), ( 0, -1, +1)
        ]

        res = []
        for x, y, z in neighbors:
            r, q = self.XYZ2RQ(x, y, z)
            yield pos + Pos(r, q)


class OddQ(Hexagonal):

    def RQ2XYZ(self, r, q):
        x = q
        z = r - (q - (q&1)) // 2
        y = -x-z
        return (x, y, z)

    def XYZ2RQ(self, x, y, z):
        q = x
        r = z + (x - (x&1)) // 2
        return (q, r)


    def getAround(self, pos):

        neighbors = [ # for odd-q, because start of sceen is bottom
            [ (+1,  0), (+1, -1), ( 0, -1), (-1, -1), (-1,  0), ( 0, +1) ],
            [ (+1, +1), (+1,  0), ( 0, -1), (-1,  0), (-1, +1), ( 0, +1) ],
        ]

        parity = pos.x % 2
        for q, r in neighbors[parity]:
            yield pos + Pos(q, r)

    def pixel2pos(self, pixelPos, sizeCellWidth, sizeCellHeight):
        """sizeCellWidth and sizeCellHeight can be float values"""

        xres = pixelPos.x // sizeCellWidth
        if xres % 2 == 0:
            yres = pixelPos.y // sizeCellHeight
        else:
            yres = (pixelPos.y - (sizeCellHeight / 2)) // sizeCellHeight

        return Pos(int(xres), int(yres))
    
    def pos2pixel(self, pos, sizeCellWidth, sizeCellHeight):
        if pos.x % 2 == 0:
            x, y = pos.x * sizeCellWidth, pos.y * sizeCellHeight
        else:
            x, y = pos.x * sizeCellWidth, (pos.y * sizeCellHeight) + (sizeCellHeight / 2)

        return x, y

    def getRadius(self, pos, radius):

        for deltaX in range(-radius, radius + 1):
            for deltaY in range( max(-radius, -deltaX-radius), min(radius, -deltaX+radius) + 1):
                deltaZ = -deltaX - deltaY
                yield Pos(deltaX, deltaZ) + pos

# For future
#class OddR(Hexagonal):
#   pass
#
#class EvenR(Hexagonal):
#   pass
#
#class OddQ(Hexagonal):
#   pass
