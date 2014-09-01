
from kivy.graphics import *
from kivy.resources import *

from strategies import *
from utils import *
from functools import reduce

import os, os.path, sys

class MapElement:
    def __init__(self):
        self.drawElement = None
        self.colorElement = None
        self.type = None

    def setAsFloor(self): self.type = 'floor'
    def isFloor(self): return self.type == 'floor'

    def setAsAir(self): self.type = 'air'
    def isAir(self): return self.type == 'air'




class StratMap:

    def __init__(self, size, playmap = None):
        self.playmap = playmap
        self.size = Pos(*size)
        self._map = [[MapElement() for y in range(size[1])] for x in range(size[0])]
        self.elements = []

    def get(self, pos):
        return self._map[pos.x][pos.y]

    def set(self, pos, v):
        self._map[pos.x][pos.y] = v

    def drawMap(self):
        for x in range(self.size.x):
            for y in range(self.size.y):
                self.drawCell(x, y)

    def drawCell(self, x, y):
        posX, posY, sizeX, sizeY = self.playmap.id2pos(x, y)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        elem = self._map[x][y]
        #select color
        color = named_colors.purple #default one
        if elem.type is None:
            color = named_colors.gray
        elif elem.type == 'floor':
            color = named_colors.black

        if elem.drawElement is None:
            elem.colorElement = color()
            elem.drawElement = Rectangle(pos = pos, size = size)
        else:
            elem.colorElement.r = color.r
            elem.colorElement.g = color.g
            elem.colorElement.b = color.b
            elem.drawElement.pos = pos
            elem.drawElement.size = size


    def update(self, dt):
        for e in self.elements:
            e.strategy.action()

        #first draw the map so it will be first
        self.drawMap()

        for e in self.elements:
            e.update(dt)



def loadMapFromFile(fileName):

	def loadCharToElement(element, char):
		if char == '.':
			element.setAsAir()
		elif char == '0':
			element.setAsFloor()
		else:
			raise NotImplemented("%s not known" % char)

	fileName = '%s.map' % fileName
	content = []
	with open(resource_find(fileName)) as mapFile:
		for line in mapFile:
			if line.endswith('\n'): line = line[:-1]
			line = line.replace(' ', '')
			content.append(line)

	content.reverse()
	#clean empty lines at beggining
	while not content[0]: content.pop(0)
	# clean the empty lines at the end
	while not content[-1]: content.pop()

	sizeY = len(content)
	sizeX = 0
	for line in content:
		sizeX = max(sizeX, len(line))

	size = Pos(sizeX, sizeY)

	res = StratMap(size)

	for y, line in enumerate(content):
		for x, char in enumerate(line):
			loadCharToElement(res.get(Pos(x, y)), char)

	return res


def addMapDirIntoRessources():
	map_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map')
	print(map_dir)
	resource_add_path(map_dir)

addMapDirIntoRessources()

