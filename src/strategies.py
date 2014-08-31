
from random import random, randint

from utils import *


class Strategy:
    """Strategy interface class"""
    def __init__(self, parent):
        self.parent = parent

    def action(self): return NotImplemented()


class GoEastStrategy(Strategy):

    def action(self):
        pos = self.parent.pos + Pos(1, 0)
        if pos.x > 20: pos = Pos(0, pos.y) 
        self.parent.pos = pos


class RandomStrategy(Strategy):

    def action(self):
        self.parent.pos = Pos(randint(0, 20), randint(0, 20))


