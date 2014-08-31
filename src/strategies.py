
from random import random, randint

from utils import *


class Strategy:
    """Strategy interface class"""
    def __init__(self, parent):
        self.parent = parent

    def action(self): return NotImplemented()


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

