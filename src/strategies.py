
from random import random, randint, choice
from pprint import pprint

from utils import *
from visualElement import *



class Strategy(object):
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
                if not m.isValid(pos):
                    self.parent.deleteMe()
                    return None

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
            if to not in foundPaths:
                break #TODO correct shortest path code
            weight, path = foundPaths[to]
            if posFrom in path: break
            to = choice(path)
            res.append(to)

        res.reverse()
        return res


class Speed(object):

    def __init__(self, speed = 1):
        self.speed = speed #1 mean everytimes, more means waiting
        self.count = 0

    def moveStep(self):
        if self.speed is None: return 0 #None as speed mean immobile
        if self.speed < 0: return -self.speed # minus 0 mean multiples times per ticks
        if self.speed == 0: return 1

        if self.count >= self.speed:
            self.count = 0
            return 1

        self.count += 1
        return 0


class DoNothingStrategy(Strategy):
    def action(self): pass


class MotherShipStrategy(Strategy):

    def __init__(self, speed = 15, *args, **kargs):
        super(MotherShipStrategy, self).__init__(*args, **kargs)
        self.count = 0
        self.life = 10
        self.speed = Speed(speed)
        self.first = True
        self.qteWalker = 0

    def action(self):

        self.parent.pos = self.putOnFloor(self.parent.pos)

        for i in range(self.speed.moveStep()):
            #each 15 actions, pop a sibling

            if self.first:
                self.parent.side.createDigger(self.parent.pos + Pos(0, -1)) 
                #self.parent.side.createFlyer(self.parent.pos + Pos(0, 1)) 
            else :
                if self.qteWalker < 10:
                    #self.parent.side.createWalker(self.parent.pos)
                    self.qteWalker += 1

            self.first = False


class RunOnFloorStrategy(Strategy):

    def __init__(self, way, *args, **kargs):
        super(RunOnFloorStrategy, self).__init__(*args, **kargs)
        """way can be 'left' or 'right'"""
        if way is 'choose':
            way = random.choice(['left', 'right'])

        self.way = way
        if way == 'left': self.way = -1
        if way == 'right': self.way = 1

        self.count = 0

    def move(self):

        self.way, pos = self.advanceOneStepAndBounce(self.way, self.parent.pos)
        pos = self.putOnFloor(pos)
        if pos is None: return # in case of missing floo<p></p>r
        self.parent.pos = pos


    def action(self):
        for i in range(self.parent.speed.moveStep()):
            self.move()

        pos = self.parent.pos
        if self.parent.pos is None:
            # in case of missing floor
            e.deleteMe()
            return

        #hack for now, get current color
        selfCol = self.parent.visual.color
        for e in self.parent.playmap._map.findOnPos(pos, self.parent):
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



class DiggerDirectionStrategy(Strategy):
    """Given a direction path, go throught that"""

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


    def move(self):
        m = self.parent.playmap._map

        if not m.get(self.parent.pos).isFloor():
            floor = self.putOnFloor(self.parent.pos)
            if floor is None: return
            self.parent.pos = floor + Pos(0, -1)

        if self.paths is None: self._fillPath()

        m.get(self.parent.pos).setAsFloor(True)

        if not self.paths:
            self.parent.endStrategy()
            return

        nextOne = self.paths.pop(0)
        if nextOne not in m.getAround(self.parent.pos):
            # special case, I don't want to deal that now
            self.parent.endStrategy()
            return

        assert nextOne in m.getAround(self.parent.pos)

        self.parent.pos = nextOne
        if self.parent.pos == self.direction:
            self.parent.endStrategy()

    def action(self):
        for i in range(self.parent.speed.moveStep()):
            self.move()


class DiggerFindDirectionStrategy(Strategy):

    def action(self):
        m = self.parent.playmap._map

        if not m.get(self.parent.pos).isFloor():
            self.parent.pos = self.putOnFloor(self.parent.pos) + Pos(0, -1)

        elements = list(m.findElement(lambda e: e.isFloor()))
        p, e = choice(elements)

        self.parent.setStrategy(DiggerDirectionStrategy(p))



class FlyerDirectionStrategy(Strategy):

    def __init__(self, direction, *args, **kargs):
        super(FlyerDirectionStrategy, self).__init__(*args, **kargs)
        self.direction = direction
        self.paths = None

    def _fillPath(self):

        def isGood(pos, elem):
            if elem.isAir(): return 1
            return None

        m = self.parent.playmap._map
        self.paths = self.shortestPath(isGood, self.direction)


    def move(self):
        if self.paths is None: self._fillPath()

        m = self.parent.playmap._map

        if not self.paths:
            self.parent.endStrategy()
            return

        nextOne = self.paths.pop(0)
        if nextOne not in m.getAround(self.parent.pos):
            # special case, I don't want to deal that now
            self.parent.endStrategy()
            return

        assert nextOne in m.getAround(self.parent.pos)

        self.parent.pos = nextOne
        if self.parent.pos == self.direction:
            self.parent.endStrategy()

    def action(self):
        for i in range(self.parent.speed.moveStep()):
            self.move()


class FlyerFindDirectionStrategy(Strategy):

    def action(self):
        self.parent.side.createMissile(self.parent.pos + Pos(0, -1)) 

        m = self.parent.playmap._map
        elements = list(m.findElement(lambda e: e.isAir()))
        p, e = choice(elements)

        self.parent.setStrategy(FlyerDirectionStrategy(p))

class MissileStrategy(Strategy):
    """Go strait down and when it ground,
    do a dig on it"""

    def __init__(self, *args, **kargs):
        super(MissileStrategy, self).__init__(*args, **kargs)

    def explode(self):

        m = self.parent.playmap._map
        for pos in m.getRadius(self.parent.pos, 2):
            m.get(pos).setAsAir()

            for e in m.findOnPos(pos, self.parent):
                if e.side == self.parent.side: continue
                e.deleteMe() #we are destroying everything

        # find every element from a radius
        # then destroy them

        # find also 


    def move(self):
        m = self.parent.playmap._map

        self.parent.pos += Pos(0, -1)

        if not m.isValid(self.parent.pos):
            self.parent.deleteMe()
        elif m.get(self.parent.pos).isFloor():
            self.parent.deleteMe()
            self.explode()


    def action(self):
        for i in range(self.parent.speed.moveStep()):
            self.move()

