
from kivy.graphics import *
from kivy.resources import *

from strategies import *
from utils import *
from functools import reduce
import mapType

import random
import math

import os, os.path, sys
from pprint import pprint

class MapElement(object):

    _floor = 'floor'
    _air = 'air'
    _unknown = 'unknown'

    def __init__(self, my_map, my_pos):
        self.drawElement = None
        self.colorElement = None
        self.type = 'unknown'
        self.metadata = None #data added to the element, useful from the type
        self.borders = []
        self.in_fog = True

        self.my_map = my_map
        self.pos = my_pos

    def applyFrom(self, otherElement):
        if otherElement.type is not self.type or otherElement.metadata != self.metadata:
            self.my_map._changedElement(self)

        self.type = otherElement.type
        self.metadata = otherElement.metadata

    def isFloor(self): return self.type is MapElement._floor
    def setAsFloor(self, isDigged = False):
        if self.type is not MapElement._floor or self.metadata != isDigged:
            self.my_map._changedElement(self)
        self.type, self.metadata = MapElement._floor, isDigged
        return self

    def isDiggedFloor(self): return self.type is MapElement._floor and self.metadata

    def isAir(self): return self.type is MapElement._air
    def setAsAir(self):
        if self.type is not MapElement._air:
            self.my_map._changedElement(self)
        self.type = MapElement._air
        return self

    def isUnknown(self): return self.type is MapElement._unknown
    def setAsUnknown(self):
        if self.type is not MapElement._unknown:
            self.my_map._changedElement(self)
        self.type = MapElement._unknown
        self.map._changedElement(self)
        return self

    def isInFog(self): return self.in_fog
    def setIsInFog(self, in_fog = True):
        if self.in_fog != in_fog:
            self.my_map._changedElement(self)
        self.in_fog = in_fog
        return self

    def __repr__(self):
        return self.__str__(self)

    def __str__(self):
        return '<MapElement type="%s" />' % (self.type,)

class StratMap(object):

    def __init__(self, size = (40, 20), mapTypeInst = mapType.Squared(), playmap = None):
        self.playmap = playmap
        self.size = Pos(*size)
        self._map = [[MapElement(self, Pos(x, y)) for y in range(size[1])] for x in range(size[0])]
        self.elements = []
        self.starts = [] # pos of starts
        self.mapTypeInst = mapTypeInst

        # the first time, draw everythings (slow, but keep the layers in their level)
        self.modifiedElements = list(map(lambda e: e[1], self.everyElementLoop()))

    def _changedElement(self, elem):
        self.modifiedElements.append(elem)

    def duplicateWithFog(self):
        return StratMap(size = self.size, mapTypeInst = self.mapTypeInst, playmap = self.playmap)

    def everyElementLoop(self):
        for x in range(self.size.x):
            for y in range(self.size.y):
                pos = Pos(x, y)
                yield (pos, self.get(pos))

    def get(self, pos):
        try:
            return self._map[pos.x][pos.y]
        except:
            raise IndexError('index %s out of range' % (str(pos),))

    def getEach(self, positions):
        for pos in positions: yield self.get(pos)

    def set(self, pos, v):
        self._map[pos.x][pos.y] = v

    def drawMap(self):

        for e in self.modifiedElements:
            pos = e.pos
            self.drawCell(pos, e)

        self.modifiedElements = []

        #for pos, e in self.everyElementLoop():
        #    self.drawCell(pos, e)

    def drawCell(self, pos, e):
        posX, posY, sizeX, sizeY = self.playmap.id2pos(pos.x, pos.y)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        #select color
        color = None
        if e.isAir():
            color = named_colors.white
        elif e.isFloor():
            if e.isDiggedFloor():
               color = named_colors.gray
            else:
                color = named_colors.brown
        elif e.isUnknown():
            color = named_colors.black
        else:
            raise Exception('type of %s not known' % e)

        if e.isInFog():
            color.t = .5

        if e.drawElement is None:
            e.colorElement = color()
            e.drawElement = Rectangle(pos = pos, size = size)
        else:
            e.colorElement.r = color.r
            e.colorElement.g = color.g
            e.colorElement.b = color.b
            e.colorElement.a = color.t
            e.drawElement.pos = pos
            e.drawElement.size = size


    def updateElements(self, dt):
        for e in self.elements: e.tick()

    def update(self, dt):

        #first draw the map so it will be first
        self.drawMap()

        for e in self.elements:
            e.draw(dt)


    def findElement(self, trueFunction):
        """Find an element in the map to which the function return true
            return the (pos, element) for valid matches"""
        res = []
        for pos, e in self.everyElementLoop():
            if trueFunction(e):
                res.append((pos, e))
        return res

    def findOnPos(self, pos, except_me = None):
        for e in self.elements:
            if e is not except_me and e.pos == pos: yield e

    def isValid(self, pos):
        return 0 <= pos.x < self.size.x \
            and 0 <= pos.y < self.size.y

    def getAround(self, pos):
        """Return position around this one
        Begin the hexa part"""

        return list(filter(self.isValid, self.mapTypeInst.getAround(pos)))

    def getRadius(self, pos, radius):
        """Return every elements from a radius
        and also every movable element"""
        # for hexagonal map, only int are allowed
        # for squared map, we can have 1.5 elements

        return filter(self.isValid, self.mapTypeInst.getRadius(pos, radius))




def loadMapFromFile(fileName):

    def loadCharToElement(element, char):
        if char == '.':
            element.setAsAir()
        elif char == '0':
            element.setAsFloor()
        elif char in '123456789':
            element.setAsStart(int(char))
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


def generateFullFloorMap(size = Pos(100, 50)):
    map_res = StratMap(size)
    for pos, e in map_res.everyElementLoop():
        e.setAsFloor()
    return map_res


def generateFullAirMap(size = Pos(100, 50)):
    map_res = StratMap(size)
    for pos, e in map_res.everyElementLoop():
        e.setAsAir()
    return map_res



def generateMap(size = Pos(100, 50), mapTypeInst = mapType.Squared()):


    plansize, rangeelevation_percent = 5, 15 # determining the generation
    rangeelevation = (rangeelevation_percent * size.y) // 100

    randTenPercent = lambda:random.randrange(-rangeelevation, rangeelevation)

    def getNextCurrent(current):
        new_current = current + randTenPercent()
        if new_current >= size.y: # we don't want to go too up
            new_current = current - (2 * abs(randTenPercent()))
        elif new_current < 0 : # we don't want to go too down
            new_current = current + (2 * abs(randTenPercent()))
        if new_current > size.y or new_current < 0: # if the previous code failed
            new_current = (size.y // 2)
        return new_current

    elevations = []


    current = (size.y // 2) + randTenPercent() # begin the elevalion at the middle (sort of)
    next_current = getNextCurrent(current)
    stepfromcurrent = 0
    for i in range(size.x):
        if stepfromcurrent == plansize:
            current, next_current = next_current, getNextCurrent(next_current)
            stepfromcurrent = 0
            cur_ele = current
        else:
            report = stepfromcurrent / plansize 
            cur_ele = (next_current - current) * report + current
        stepfromcurrent += 1

        elevations.append(cur_ele)

    map_res = StratMap(size, mapTypeInst)

    start1posx = size.x // 10 # the green is at 10% start of map
    start1pos = Pos(start1posx, abs(elevations[start1posx]) + 1)

    start2posx = size.x - (size.x // 10) # the red is at 10% end of map
    start2pos = Pos(start2posx, abs(elevations[start2posx]) + 1)

    map_res.starts = [start1pos, start2pos]

    # Fill the map
    for x, elevation in enumerate(elevations):
        for y in range(size.y):
            cur_pos = Pos(x, y)
            if y > elevation:
                map_res.get(cur_pos).setAsAir()
            else:
                map_res.get(cur_pos).setAsFloor()

    assert map_res.get(start1pos).isAir()
    assert map_res.get(start2pos).isAir()

    return map_res
