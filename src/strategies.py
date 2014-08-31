
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
        if pos.x > maxX: pos = Pos(0, pos.y) 
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

        curX = self.parent.pos.x + self.speed.x
        if curX < 0 or curX > maxX:
            self.speed = Pos(-self.speed.x, self.speed.y)
            curX = self.parent.pos.x + self.speed.x

        curY = self.parent.pos.y + self.speed.y
        if curY < 0 or curY > maxY:
            self.speed = Pos(self.speed.x, -self.speed.y)
            curY = self.parent.pos.y + self.speed.y

        self.parent.pos = Pos(curX, curY)

