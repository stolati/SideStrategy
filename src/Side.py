import random
from functools import partial
from pprint import pprint


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
        'visual': partial(ColorWalker),
    },
    'digger':{
        'strategy': partial(DiggerFindDirectionStrategy),
        'viewfield': partial(ViewFieldAroundSimple, 2),
        'speed': partial(Speed, 5),
        'visual': partial(ColorDigger),
    },
    'flyer':{
        'strategy': partial(FlyerFindDirectionStrategy),
        'viewfield': partial(ViewFieldGroundBlock, 10),
        'speed': partial(Speed, 1),
        'visual': partial(ColorFlyer),
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
        self._lastNotFog = set()

        self._selectedElement = []

    def updateMap(self, dt):
        #self.game._map.update(dt)
        #return

        # get elements from ourselves
        ourElements, notOurElements = list(), list()
        for e in self.game._map.elements:
            if e.side == self: ourElements.append(e)
            else: notOurElements.append(e)

        visiblePos = set()
        visibleElements = set()

        ## init the current map to fog everywhere
        for pos in self._lastNotFog:
            self._map.get(pos).setIsInFog()

        for curOurElem in ourElements:
            for pos in curOurElem.viewfield.getViewPos():
                visiblePos.add(pos)

        for pos in visiblePos:
            curElem = self._map.get(pos)
            curElem.applyFrom(self.game._map.get(pos))
            curElem.setIsInFog(False)

        self._map.elements = list(ourElements)
        for notOurElement in notOurElements:
            if notOurElement.pos in visiblePos:
                self._map.elements.append(notOurElement)
                visibleElements.add(notOurElement)

        #for toRemoveElement in self._lastVisibles - visibleElements:
        #    toRemoveElement.visual.remove()

        self._lastVisibles = visibleElements
        self._lastNotFog = visiblePos

        self._map.update(dt)

    def resetMap(self):
        self._map.resetDraw()

    def __getattr__(self, name):
        if not name.startswith('create'):
            raise AttributeError("%s object has no attribute '%'\n" % (repr(self), name))
        goalName = name[len('create'):].lower()
        goalElem = conf[goalName] 

        def generatorFct(position, **kargs):
            if 'visual' in goalElem:
                visual = goalElem['visual'](color = self.color)
            else:
                visual = ColorVisual(color = self.color)


            e = Element(goalName, playmap = self.game, side = self, startPos = position,
                visual = visual,
                strategy = goalElem['strategy'](**kargs),
                viewfield = goalElem['viewfield'](),
                speed = goalElem['speed'](),
            )
            self.game._map.elements.append(e)
        return generatorFct


    def action_to(self, action, pos):
        elem = self.game._map.get(pos)

        for element in self._selectedElement:
            element.user_action(action, pos)


        if elem.isFloor():

            #find the digger from us side
            def isGood(e):
                return e.category == 'digger' and e.side == self

            for good in filter(isGood, self._selectedElement):
                good.setStrategy(DiggerDirectionStrategy(direction = pos))

        if elem.isAir():

            #find the digger from us side
            def isGood(e):
                return e.category == 'flyer' and e.side == self

            for good in filter(isGood, self._selectedElement):
                good.setStrategy(FlyerDirectionStrategy(direction = pos))


    def selection(self, positions):
        for e in self._selectedElement:
            e.unselected()

        # TODO instead of having a list
        # give the max/min of each, the loop should be faster
        element_selected = list()
        for e in self.game._map.elements:
            if e.side is not self: continue
            if e.pos in positions:
                element_selected.append(e)
                e.selected()

        self._selectedElement = element_selected
        return self._selectedElement

