import random

# Side is a player
# It can be a real player, a distant one, an IA, a neutral one, etc ...

from visualElement import *
from strategies import *
from utils import *
from stratmap import *
from viewfield import *


class Side:

    def __init__(self, color, game):
        self.color = color
        self.game = game
        self.elements = {}
        self._map = game._map.duplicateWithFog()

        self._lastVisibles = set()

    def updateMap(self, dt):
        #self.game._map.update(dt)
        #return

        listElement = list(self.game._map.elements)

        # get elements from ourselves
        ourElements = list(filter(lambda e: e.side == self, listElement))
        notOurElements = list(filter(lambda e: e.side != self, listElement))
        visiblePos = set()
        visibleElements = set(ourElements)

        # init the current map to fog everywhere
        for pos, e in self._map.everyElementLoop():
            e.setIsInFog()

        for curOurElem in ourElements:
            for pos in curOurElem.viewfield.getViewPos():
                visiblePos.add(pos)

        for pos in visiblePos:
            curElem = self._map.get(pos)
            self.game._map.get(pos).applyType(curElem)
            curElem.setIsInFog(False)

        self._map.elements = ourElements
        for notOurElement in notOurElements:
            if notOurElement.pos in visiblePos:
                self._map.elements.append(notOurElement)
                visibleElements.add(notOurElement)

        for toRemoveElement in self._lastVisibles - visibleElements:
            toRemoveElement.visual.remove()

        self._lastVisibles = visibleElements

        self._map.update(dt)


    def createMotherShip(self, position, **kargs):
        e = Element('mothership', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = MotherShipStrategy(**kargs),
            viewfield = ViewFieldAroundSimple(5),
        )
        self.game._map.elements.append(e)

    def createWalker(self, position, **kargs):

        way = random.choice(['left', 'right'])

        e = Element('walker', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = RunOnFloorStrategy(way = way, **kargs),
            viewfield = ViewFieldGroundBlock(5),
        )
        self.game._map.elements.append(e)

    def createDigger(self, position, **kargs):
        e = Element('digger', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            #strategy = DiggerStrategy()
            #strategy = DiggerDirectionStrategy()
            strategy = DiggerFindDirectionStrategy(**kargs),
            viewfield = ViewFieldAroundSimple(2),
        )
        self.game._map.elements.append(e)

    def createFlyer(self, position, **kargs):
        e = Element('flyer', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = FlyerFindDirectionStrategy(**kargs),
            viewfield = ViewFieldGroundBlock(10),
        )
        self.game._map.elements.append(e)

    def createMissile(self, position, **kargs):
        e = Element('missile', playmap = self.game, side = self, startPos = position,
            visual = ColorVisual(color = self.color),
            strategy = MissileStrategy(**kargs),
            viewfield = ViewFieldAroundSimple(1),
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


