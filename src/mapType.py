

from utils import *
from math import hypot


# This file is referency maps with there own algorythms
# Most of the algo come from http://www.redblobgames.com/grids/hexagons/#rings 

class Squared:

    _radiusElements = {}

    def getAround(self, pos, withPonderation = False):
        if withPonderation:
            aroundNear = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0)]
            for delta in aroundNear:
                yield (pos + delta, 1)

            aroundFar = [Pos(1, 1), Pos(1, -1), Pos(-1, 1), Pos(-1, -1)]
            for delta in aroundFar:
                yield (pos + delta, 1.41)
        else:
            around = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0),
                    Pos(1, 1), Pos(1, -1), Pos(-1, 1), Pos(-1, -1)]
            for delta in around:
                yield pos + delta

    def getRadius(self, pos, radius):
        radius = int(radius)

        if radius not in Squared._radiusElements:
            elements = []
            for x in range(- radius, radius + 1):
                for y in range(- radius, radius + 1):
                    dist = hypot(x, y)
                    if dist <= radius + 0.5:
                        elements.append(Pos(x, y))

            Squared._radiusElements[int(radius)] = elements

        for deltaPos in Squared._radiusElements[radius]:
            yield pos + deltaPos


    def pixel2pos(self, pixelPos, sizeCellWidth, sizeCellHeight):

        xres = pixelPos.x // sizeCellWidth
        yres = pixelPos.y // sizeCellHeight
        return Pos(int(xres), int(yres))


    def pos2pixel(self, pos, sizeCellWidth, sizeCellHeight):
        return (pos.x * sizeCellWidth, pos.y * sizeCellHeight)


