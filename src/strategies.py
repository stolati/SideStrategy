
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


