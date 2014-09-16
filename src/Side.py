import random

# Side is a player
# It can be a real player, a distant one, an IA, a neutral one, etc ...

from visualElement import *
from strategies import *
from utils import *


class Side:

    def __init__(self, color, game):
        self.color = color
        self.game = game
        self.elements = {}

    def createMotherShip(self, position, **kargs):
        e = Element('mothership', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = MotherShipStrategy(**kargs)
        )
        self.game._map.elements.append(e)

    def createWalker(self, position, **kargs):

        way = random.choice(['left', 'right'])

        e = Element('walker', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = RunOnFloorStrategy(way = way, **kargs)
        )
        self.game._map.elements.append(e)

    def createDigger(self, position, **kargs):
        e = Element('digger', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            #strategy = DiggerStrategy()
            #strategy = DiggerDirectionStrategy()
            strategy = DiggerFindDirectionStrategy(**kargs)
        )
        self.game._map.elements.append(e)

    def createFlyer(self, position, **kargs):
        e = Element('flyer', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = FlyerFindDirectionStrategy(**kargs)
        )
        self.game._map.elements.append(e)

    def createMissile(self, position, **kargs):
        e = Element('missile', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = MissileStrategy(**kargs)
        )
        self.game._map.elements.append(e)


    def command_touch(self, pos):

        elem = self.game._map.get(pos)
        if elem.isFloor():

            #find the digger from us side
            def isGood(e):
                return e.category == 'digger' and e.side == self

            goods = list(filter(isGood, self.game._map.elements))
            assert len(goods) == 1
            good = goods[0]

            # replace the current strategy
            good.setStrategy(DiggerDirectionStrategy(direction = pos))

        if elem.isAir():

            #find the digger from us side
            def isGood(e):
                return e.category == 'flyer' and e.side == self

            goods = list(filter(isGood, self.game._map.elements))
            assert len(goods) == 1
            good = goods[0]

            # replace the current strategy
            good.setStrategy(FlyerDirectionStrategy(direction = pos))


