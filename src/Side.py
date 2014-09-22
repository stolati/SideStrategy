import random
from functools import partial


# Side is a player
# It can be a real player, a distant one, an IA, a neutral one, etc ...

from visualElement import *
from strategies import *
from utils import *
from stratmap import *
from viewfield import *



conf = {
    'mothership':{
        'strategy': partial(MotherShipStrategy),
        'viewfield': partial(ViewFieldAroundSimple, 5),
        'speed': partial(Speed, None),
    },
    'walker':{
        'strategy': partial(RunOnFloorStrategy, way = 'choose'),
        'viewfield': partial(ViewFieldGroundBlock, 5),
        'speed': partial(Speed, 3),
    },
    'digger':{
        'strategy': partial(DiggerFindDirectionStrategy),
        'viewfield': partial(ViewFieldAroundSimple, 2),
        'speed': partial(Speed, 5),
    },
    'flyer':{
        'strategy': partial(FlyerFindDirectionStrategy),
        'viewfield': partial(ViewFieldGroundBlock, 10),
        'speed': partial(Speed, 1),
    },
    'missile':{
        'strategy': partial(MissileStrategy),
        'viewfield': partial(ViewFieldAroundSimple, 1),
        'speed': partial(Speed, -3),
    },
}



class Side(object):

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


    def __getattr__(self, name):
        if not name.startswith('create'):
            raise AttributeError("%s object has no attribute '%'\n" % (repr(self), name))
        goalName = name[len('create'):].lower()
        goalElem = conf[goalName] 

        def generatorFct(position, **kargs):
            e = Element(goalName, playmap = self.game, side = self, startPos = position,
                visual = ColorVisual(color = self.color),
                strategy = goalElem['strategy'](**kargs),
                viewfield = goalElem['viewfield'](),
                speed = goalElem['speed'](),
            )
            self.game._map.elements.append(e)
        return generatorFct


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


