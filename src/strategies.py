
from random import random, randint, choice

from utils import *
from visualElement import *


class Strategy:
    """Strategy interface class"""
    def __init__(self, parent = None):
        self.parent = parent

    def action(self):
        pass #by default do nothing
        print('action ?!')

    def advanceOneStepAndBounce(self, way, pos):
        """advance one step of x and return the x value
        which can change if the element bounce of the wall"""

        maxX = self.parent.playmap.cellx
        pos = self.parent.pos + Pos(way, 0)
        if pos.x >= maxX or pos.x < 0:
            way = -way
            pos = self.parent.pos + Pos(way, 0)

        return way, pos

    def putOnFloor(self, pos):

        #try now to find the floor from that
        m = self.parent.playmap._map
        curElem = m.get(pos)
        if curElem.isFloor():
            #we are on floor
            while m.get(pos).isFloor():
                pos = pos + Pos(0, 1)

        else:
            #we are not on floor
            while not m.get(pos).isFloor():
                pos = pos + Pos(0, -1)
            pos = pos + Pos(0, 1) #return to the last no-floor element

        return pos


class GoEastStrategy(Strategy):

    def action(self):
        maxX = self.parent.playmap.cellx

        pos = self.parent.pos + Pos(1, 0)
        if pos.x >= maxX: pos = Pos(0, pos.y) 
        self.parent.pos = pos


class RandomStrategy(Strategy):

    def action(self):
        maxX = self.parent.playmap.cellx
        maxY = self.parent.playmap.celly

        self.parent.pos = Pos(randint(0, maxX), randint(0, maxY))

class BounceStrategy(Strategy):

    def __init__(self, parent, initspeed = Pos(1, 1)):
        super(BounceStrategy, self).__init__(parent)
        self.speed = initspeed

    def action(self):
        maxX = self.parent.playmap.cellx
        maxY = self.parent.playmap.celly

        oldPos = self.parent.pos
        newPos = self.parent.pos + self.speed

        if newPos.x < 0 or newPos.x >= maxX:
            self.speed = Pos(-self.speed.x, self.speed.y)
            newPos = self.parent.pos + self.speed

        if newPos.y < 0 or newPos.y >= maxY:
            self.speed = Pos(self.speed.x, -self.speed.y)
            newPos = self.parent.pos + self.speed

        if self.parent.playmap._map.get(newPos).isFloor():
            self.speed = Pos(-self.speed.x, -self.speed.y)
            newPos = self.parent.pos + self.speed

        self.parent.pos = newPos


class PoopFloorStrategy(GoEastStrategy):
    """Poop floor element and jump on the top floor"""

    def action(self):
        #put poop on the last place we have been on
        self.parent.playmap._map.get(self.parent.pos).setAsFloor()

        super(PoopFloorStrategy, self).action()

        #try to jump on the top poop part
        while self.parent.playmap._map.get(self.parent.pos).isFloor():
            self.parent.pos = self.parent.pos + Pos(0, 1)


class MotherShipStrategy(Strategy):

    def __init__(self, speed = 15, *args, **kargs):
        super(MotherShipStrategy, self).__init__(*args, **kargs)
        self.count = 0
        self.life = 10
        self.speed = speed

    def action(self):
        self.count += 1
        if self.count % self.speed != 0: return
        #each 15 actions, pop a sibling
        playmap = self.parent.playmap
        visualMine = ColorVisual(color = self.parent.visual.color)        
        way = choice(['left', 'right'])
        e = Element(playmap, visual = visualMine, strategy = RunOnFloorStrategy(way), startPos = self.parent.pos)

        playmap._map.elements.append(e)


class RunOnFloorStrategy(Strategy):

    def __init__(self, way, *args, **kargs):
        super(RunOnFloorStrategy, self).__init__(*args, **kargs)
        """way can be 'left' or 'right'"""
        self.way = way
        if way == 'left': self.way = -1
        if way == 'right': self.way = 1

        self.count = 0

    def action(self):
        self.count += 1
        if self.count % 2 != 0: return

        self.way, pos = self.advanceOneStepAndBounce(self.way, self.parent.pos)
        pos = self.putOnFloor(pos)

        self.parent.pos = pos

        #hack for now, get current color
        selfCol = self.parent.visual.color
        for e in self.parent.playmap._map.findOnPos(pos):
            if e is self.parent: continue #TODO do a helper for this loop
            if e.visual.color == selfCol: continue #TODO replace that by side

            # we are encounting a enemy, getting the stategy to know what it is
            # TODO instead do a life count
            curStrat = e.strategy.__class__
            if curStrat == RunOnFloorStrategy:
                # both are destroyed
                self.parent.deleteMe()
                e.deleteMe()

            if curStrat == MotherShipStrategy:
                self.parent.deleteMe()

                e.strategy.life -= 1
                if e.strategy.life == 0:
                    e.deleteMe()

                # todo do a stuff to the mothership

            print(curStrat)

        #if encounter another element
        #if encounter the mothership

