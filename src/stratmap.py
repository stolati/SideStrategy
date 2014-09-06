
from kivy.graphics import *
from kivy.resources import *

from strategies import *
from utils import *
from functools import reduce

import random
import math

import os, os.path, sys

class MapElement:
    def __init__(self):
        self.drawElement = None
        self.colorElement = None
        self.type = None
        self.metadata = None #data added to the element, useful from the type
        self.borders = []

    def isFloor(self): return self.type == 'floor'
    def setAsFloor(self):
        self.type = 'floor'
        return self

    def isAir(self): return self.type == 'air'
    def setAsAir(self):
        self.type = 'air'
        return self

    def isStart(self): return self.type == 'start'
    def getStartNum(self): return self.metadata
    def setAsStart(self, num):
        self.type, self.metadata = 'start', num
        return self


class StratMap:

    def __init__(self, size = (40, 20), playmap = None):
        self.playmap = playmap
        self.size = Pos(*size)
        self._map = [[MapElement() for y in range(size[1])] for x in range(size[0])]
        self.elements = []

    def everyElementLoop(self):
        for x in range(self.size.x):
            for y in range(self.size.y):
                pos = Pos(x, y)
                yield (pos, self.get(pos))

    def get(self, pos):
        return self._map[pos.x][pos.y]

    def set(self, pos, v):
        self._map[pos.x][pos.y] = v

    def drawMapPreparation(self):
        if self._preparation_done: return
        posX, posY, sizeX, sizeY = self.playmap.id2pos(x, y)
        size = Pos(sizeX, sizeY)

        for pos, e in self.everyElementLoop():
            pass 

    def drawMap(self):
        for pos, e in self.everyElementLoop():
            self.drawCell(pos, e)

    def drawCell(self, pos, e):
        posX, posY, sizeX, sizeY = self.playmap.id2pos(pos.x, pos.y)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        #select color
        color = named_colors.purple #default one
        if e.type is None:
            color = named_colors.gray
        elif e.isAir():
            color = named_colors.white
        elif e.isFloor():
            color = named_colors.black
        elif e.isStart():
            color = named_colors.blue
        #TODO put an exception when type not known instead of default one

        if e.drawElement is None:
            e.colorElement = color()
            e.drawElement = Rectangle(pos = pos, size = size)
        else:
            e.colorElement.r = color.r
            e.colorElement.g = color.g
            e.colorElement.b = color.b
            e.drawElement.pos = pos
            e.drawElement.size = size


    def update(self, dt):
        for e in self.elements:
            e.strategy.action()

        #first draw the map so it will be first
        self.drawMap()

        for e in self.elements:
            e.visual.update(dt)


    def findElement(self, trueFunction):
        """Find an element in the map to which the function return true
            return the (pos, element) for valid matches"""
        res = []
        for pos, e in self.everyElementLoop():
            if trueFunction(e):
                res.append((pos, e))
        return res

    def findOnPos(self, pos):
        for e in self.elements:
            if e.pos == pos: yield e


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


def generateMap(size = Pos(100, 50)):


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

    map_res = StratMap(size)

    start1posx = size.x // 10 # the green is at 10% start of map
    start1pos = Pos(start1posx, abs(elevations[start1posx]) + 1)

    start2posx = size.x - (size.x // 10) # the red is at 10% end of map
    start2pos = Pos(start2posx, abs(elevations[start2posx]) + 1)

    # Fill the map
    for x, elevation in enumerate(elevations):
        for y in range(size.y):
            cur_pos = Pos(x, y)
            if cur_pos == start1pos:
                map_res.get(cur_pos).setAsStart(1)
            elif cur_pos == start2pos:
                map_res.get(cur_pos).setAsStart(2)
            elif y > elevation:
                map_res.get(cur_pos).setAsAir()
            else:
                map_res.get(cur_pos).setAsFloor()

    return map_res
