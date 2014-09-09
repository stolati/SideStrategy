
from random import random, randint, choice
from pprint import pprint

from utils import *
from visualElement import *



class Strategy:
    """Strategy interface class"""
    def __init__(self, parent = None, side = None):
        self.parent, self.side = parent, side
        self.nextStrat = None #when this strategy is finished (if the strategy can be finished) 

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

    def shortestPath(self, fctWeight, posTo, posFrom = None):
        if posFrom is None: posFrom = self.parent.pos
        if posFrom == posTo: return []
        m = self.parent.playmap._map

        foundPaths = {posFrom : (0, [None])}
        curPos, nextPos = [posFrom], []

        while len(curPos): #continue until they are case to process

            for pos in curPos:
                curWeight = foundPaths[pos][0]
                for around in m.getAround(pos):
                    tmpWeight = fctWeight(around, m.get(around))
                    if tmpWeight is None: continue
                    weight = tmpWeight + curWeight
                    #replace case
                    if around not in foundPaths:
                        foundPaths[around] = (weight, [pos])
                        nextPos.append(around)
                    else:
                        oldWeight, oldPaths = foundPaths[around]
                        if oldWeight == weight:
                            oldPaths.append(pos)
                        elif oldWeight > weight:
                            foundPaths[around] = (weight, [pos])
                        else:
                            pass

            curPos, nextPos = nextPos, []

        # simple decompilation of path
        to, res = posTo, [posTo]
        while True:
            weight, path = foundPaths[to]
            if posFrom in path: break
            to = choice(path)
            res.append(to)

        res.reverse()
        return res


class DoNothing(Strategy):
    def action(self): pass


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
        self.first = True

    def action(self):
        self.count += 1
        if self.count % self.speed != 0: return
        #each 15 actions, pop a sibling

        if self.first:
            self.parent.side.createDigger(self.parent.pos + Pos(0, -1)) 
        else :
            self.parent.side.createWalker(self.parent.pos)

        self.first = False


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
            if e.category == 'walker':
                # both are destroyed
                self.parent.deleteMe()
                e.deleteMe()

            if e.category == 'mothership':
                self.parent.deleteMe()

                e.current_strategy.life -= 1
                if e.current_strategy.life == 0:
                    e.deleteMe()

        #if encounter another element
        #if encounter the mothership


class DiggerStrategy(Strategy):

    def action(self):
        # try to go one of 6 ways
        # change thoses ways into digged floor
        m = self.parent.playmap._map

        m.get(self.parent.pos).setAsFloor(True)
        possiblesPos = m.getAround(self.parent.pos)

        # filter the floors on possiblePos
        around_floor = list(filter(lambda p: m.get(p).isFloor(), possiblesPos))

        around_floor_digged = filter(lambda p: m.get(p).isDiggedFloor(), around_floor)
        around_floor_undigged = filter(lambda p: not m.get(p).isDiggedFloor(), around_floor)
        around_floor_undigged = list(around_floor_undigged)

        if len(around_floor_undigged) != 0:
            nextpos = choice(around_floor_undigged)
        else:
            around_floor_digged = list(around_floor_digged)
            nextpos = choice(around_floor_digged)

        #nextpos = possiblesPosFloor[0]
        self.parent.pos = nextpos


class DiggerDirectionStrategy(Strategy):

    def __init__(self, direction, *args, **kargs):
        super(DiggerDirectionStrategy, self).__init__(*args, **kargs)
        self.direction = direction
        self.paths = None

    def _fillPath(self):

        def isGood(pos, elem):
            if elem.isFloor():
                if elem.isDiggedFloor(): return 1
                return 2
            return None

        m = self.parent.playmap._map
        self.paths = self.shortestPath(isGood, self.direction)


    def action(self):
        if self.paths is None: self._fillPath()

        m = self.parent.playmap._map
        m.get(self.parent.pos).setAsFloor(True)

        nextOne = self.paths.pop(0)
        if nextOne not in m.getAround(self.parent.pos):
            # special case, I don't want to deal that now
            self.parent.endStrategy()
            return

        assert nextOne in m.getAround(self.parent.pos)

        self.parent.pos = nextOne
        if self.parent.pos == self.direction:
            self.parent.endStrategy()


class DiggerFindDirectionStrategy(Strategy):

    def action(self):
        m = self.parent.playmap._map
        elements = list(m.findElement(lambda e: e.isFloor()))
        p, e = choice(elements)

        self.parent.setStrategy(DiggerDirectionStrategy(p))
