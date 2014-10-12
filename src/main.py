#!/usr/bin/kivy

import sys, os, os.path
import random
from pprint import pprint

# configure kivy
from kivy.config import Config

os.environ['KIVY_NO_CONSOLELOG'] = '1'

# http://kivy.org/docs/api-kivy.config.html#module-kivy.config
Config.set('kivy', 'show_fps', 1)
Config.set('graphics', 'fullscreen', 0)
#Config.set('graphics', 'show_cursor', 0)

#Config.write()


import kivy


#import cProfile

# http://stackoverflow.com/questions/20625312/can-i-run-a-kivy-program-from-within-pyscripter
# http://www.redblobgames.com/grids/hexagons/  => hexagon code
# http://www.hexographer.com/ => hexagon map creation
# https://docs.python.org/3/reference/datamodel.html#object.__getitem__ => python special stuff

# Things to do after :

# - click handle (left/right) with position
# - link a strategy to the element

# - bigger than 1x1 elements (so we can go to )
# - an interface with mouse to pop elements

# - we should avoid beiing to near the sky-floor limit for flyers and diggers

# - put map type into there own class


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import *
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *
import kivy.resources
from kivy.graphics.transformation import Matrix
from kivy.uix.button import *
from kivy.core.window import Window

from kivy.config import Config

from strategies import *
from utils import *
from stratmap import *
from visualElement import *
from Side import *
from mapType import *


# imported so it can be used in the kv file
from widget.selection import Selection
from widget.mouseBorderScroll import MouseBorderScroll


nb_element_on_screen = Pos(30, 30)


class FPSCalculatorSimple(object):

    def __init__(self, responseEvery = 10):
        self.currentResults = []
        self.responseEvery = responseEvery

    def addValue(self, dt):
        self.currentResults.append(dt)

    def haveToCalculate(self):
        return len(self.currentResults) >= self.responseEvery

    def calculate(self):
        sumTot = 0
        for v in self.currentResults:
            sumTot += v
        res = sumTot / len(self.currentResults)
        self.currentResults = []
        return res


class FPSCalculatorBetter(object):

    def __init__(self, responseEverySeconds = 1):
        self.currentSum = 0
        self.totalResponse = 0
        self.responseEverySeconds = responseEverySeconds

    def addValue(self, dt):
        self.totalResponse += 1
        self.currentSum += dt

    def haveToCalculate(self):
        return self.currentSum >= self.responseEverySeconds

    def calculate(self):
        res = self.totalResponse / self.currentSum
        self.currentSum = 0
        self.totalResponse = 0
        return res




class StratGame(Widget):

    transform = ObjectProperty(Matrix())

    def __init__(self, **kargs):
        super(StratGame, self).__init__(**kargs)

        # map generation
        self.mapTypeInst = Squared()
        self._map = generateMap(mapTypeInst = Squared())
        self._map.playmap = self

        self.cellx, self.celly = self._map.size
        self._graphics = None # violet rectangle in background

        # create the map with 2 sides
        userSide = Side(color = named_colors.green, game = self)
        userSide.createMotherShip(self._map.starts[0], speed = 3)

        computerSide = Side(color = named_colors.red, game = self)
        computerSide.createMotherShip(self._map.starts[1])

        self.userSide = userSide
        self.computerSide = computerSide
        self.fps = FPSCalculatorBetter()

        # size relative datas
        self._quanta = None

    def on_parent(self, self_bis, parent):
        if parent:
            parent.bind(size = self.resize)
            self.resize(parent, parent.size)
            # once we have parent, we can launch the game
            Clock.schedule_interval(self.update, 1.0/15.0)
        else:
            parent.unbind(size = self.resize)

    def resize(self, parent, size):
        # recalculate base size => quanta
        quantumx = self.parent.width / nb_element_on_screen.x
        quantumy = self.parent.height / nb_element_on_screen.y

        self._quanta = Pos(quantumx, quantumy)


    def id2pos(self, x, y):
        """left 10 percent on each side"""
        quantumx, quantumy = self._quanta

        xres, yres = self.mapTypeInst.pos2pixel(Pos(x, y), quantumx, quantumy)

        return (xres, yres, quantumx, quantumy)


    def pos2id(self, x, y):
        """return the position to which the id is in (x, y)"""

        quantumx, quantumy = self._quanta

        pos = Pos(x, y)
        return self.mapTypeInst.pixel2pos(pos, quantumx, quantumy)

    def update(self, dt):

        sizeX, sizeY = self._quanta

        oldSize = tuple(self.size)
        calculatedSize = (sizeX * self.cellx, sizeY * self.celly)
        if oldSize != calculatedSize:
            self.size = calculatedSize

        self.fps.addValue(dt)
        if self.fps.haveToCalculate():
            print('fps : ' + str(self.fps.calculate()))

        # (len(self.canvas.get_group(None)))
        with self.canvas:

            if self._graphics is None:
                named_colors.black()
                self._graphics = Rectangle(pos = (0, 0), size = (self.width, self.height))
            else :
                self._graphics.pos = (0, 0)
                self._graphics.size = (self.width, self.height)

            self._map.updateElements(dt)
            self.userSide.updateMap(dt)

    def _selection(self, position1, position2):
        #TODO do the selection working again
        #TODO and set the selection class just as parent of this one
        # ( instead of 2 classes parents => position handling )
        idEl1 = self.pos2id(position1.x, position1.y)
        idEl2 = self.pos2id(position2.x, position2.y)

        xStart = min(idEl1.x, idEl2.x)
        xEnd = max(idEl1.x, idEl2.x)
        yStart = min(idEl1.y, idEl2.y)
        yEnd = max(idEl1.y, idEl2.y)

        positions = []
        for x in range(xStart, xEnd + 1):
            for y in range(yStart, yEnd + 1):
                positions.append(Pos(x, y))

        self.userSide.selection(positions)

    def on_touch_up(self, touch):
        if False:

            if touch.button == 'scrolldown' or touch.button == 'scrollup':
                return False

            if self._selectionEnd is None:
                self._selection_single(self._selectionStart)
            else :
                self._selection_multiples(self._selectionStart, self._selectionEnd)

            self._selectionStart = None
            self._selectionEnd = None
            self._selection.clear()


    def on_touch_move(self, touch):

        #print('<touch button="%s" dpos="%s">' 
            #% (touch.button, touch.dpos))

        if False:
            if touch.button == 'scrolldown' or touch.button == 'scrollup':
                return False

            if self._selectionStart is None:
                self._selectionStart = Pos(*touch.pos)

            self._selectionEnd = Pos(*touch.pos)

            self._selection_zone_update()

        #assert len(touch.dpos) == 2

        #deltaX, deltaY = touch.dpos[0], touch.dpos[1]

        #print('moving (%s, %s)' % (deltaX, deltaY))
        #self.transform = self.transform.translate(x = deltaX, y = deltaY, z = 0)

        # touch have values : 
        # pos (x, y)
        # button (left, right, middle, scrollup, scrooldown)

        # dpos <= delta between this and the last event
        # ppos <= previous position
        # 

        # touch.distance(other event) <= good


        # For a map moving movement, calculate the delta
        #if touch.dista

        #print('on_touch_move')
        #print(touch)
        #print('button : ' + repr(touch.button))

        #"""Blacken the cases when the mouse touch a case"""
        #with self.canvas:
        #    named_colors.violet()
        #    pos = self.pos2id(*touch.pos)
        #    if pos is None : return

        #    idx, idy = pos
        #    posX, posY, sizeX, sizeY = self.id2pos(idx, idy)
        #    Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

    def on_touch_down(self, touch):
        print('touch down under it')
        return True
        if False:

            self._touchStatus = 'simple'
            self._selectionStart = Pos(*touch.pos)

            print('touch down')
            #print('touch down')
            #print(touch.x)
            #print(touch.y)

            #if touch.button == 'scrolldown':
            #    self.zoom = min(self.zoom * 1.05, zoom_max)
            #    return

            #if touch.button == 'scrollup':
            #    self.zoom = max(self.zoom / 1.05, 1)
            #    return

            pos = self.pos2id(*touch.pos)
            if pos is None: return
            self.userSide.command_touch(pos)



class StratApp(App):
    pass

    #    return result


if __name__ == '__main__':

    #Config.set('kivy', 'show_fps', True)

    # adding asset path into kivy resources
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets'))
    for (dirpath, dirnames, filenames) in os.walk(assets_dir):
        kivy.resources.resource_add_path(dirpath)

    #cProfile.run('StratApp().run()')
    StratApp().run()
