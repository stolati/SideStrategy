#!/usr/bin/kivy
import kivy

import sys, os, os.path
import random
from pprint import pprint

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
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.properties import *
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *
import kivy.resources
from kivy.graphics.transformation import Matrix

from kivy.config import Config

from strategies import *
from utils import *
from stratmap import *
from visualElement import *
from Side import *
from mapType import *


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


class ScatterPlaneStrat(ScatterPlane):
    """Same as scatter, but the touch modifications are differents"""
    pass


class StratGame(Widget):

    visual_marge = 0.01

    transform = ObjectProperty(Matrix())

    def __init__(self, stratMap, mapTypeInst, **kargs):
        super(StratGame, self).__init__(**kargs)
        self._map = stratMap
        stratMap.playmap = self
        self.mapTypeInst = mapTypeInst

        self.cellx, self.celly = stratMap.size
        self._graphics = None # violet rectangle in background

        # create the map with 2 sides
        userSide = Side(color = named_colors.green, game = self)
        userSide.createMotherShip(self._map.starts[0], speed = 3)

        computerSide = Side(color = named_colors.red, game = self)
        computerSide.createMotherShip(self._map.starts[1])

        self.userSide = userSide
        self.computerSide = computerSide
        self.fps = FPSCalculatorBetter()

    def id2pos(self, x, y):
        """left 10 percent on each side"""
        hMarge, wMarge = self.height * StratGame.visual_marge, self.width * StratGame.visual_marge

        quantumy = (self.height - (2 * hMarge)) / self.celly
        quantumx = (self.width - (2 * wMarge)) / self.cellx

        xres, yres = self.mapTypeInst.pos2pixel(Pos(x, y), quantumx, quantumy)

        return (xres + hMarge, yres + wMarge, quantumx, quantumy)


    def pos2id(self, x, y):
        """return the position to which the id is in (x, y)"""

        hMarge, wMarge = self.height * StratGame.visual_marge, self.width * StratGame.visual_marge

        quantumy = (self.height - (2 * hMarge)) / self.celly
        quantumx = (self.width - (2 * wMarge)) / self.cellx

        pos = Pos(x - hMarge, y - wMarge)
        return self.mapTypeInst.pixel2pos(pos, quantumx, quantumy)

    def update(self, dt):

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
            #self._map.update(dt)

    def on_touch_move(self, touch):

        print('<touch button="%s" dpos="%s">' 
            % (touch.button, touch.dpos))

        assert len(touch.dpos) == 2

        deltaX, deltaY = touch.dpos[0], touch.dpos[1]

        print('moving (%s, %s)' % (deltaX, deltaY))
        self.transform = self.transform.translate(x = deltaX, y = deltaY, z = 0)

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

    def build(self):

        #self._map = loadMapFromFile('map03')

        mapTypeInst = random.choice([Squared()])

        self._map = generateMap(mapTypeInst = mapTypeInst)

        self._game = StratGame(self._map, mapTypeInst)

        xsize, ysize = self._map.size
        self._game.height = ysize * 64
        self._game.width = xsize * 64

        self._scatter = ScatterPlaneStrat()
        self._scatter.add_widget(self._game)

        #Clock.schedule_interval(self._game.update, 1.0/60.0)
        #Clock.schedule_interval(self._game.update, 1.0/15.0)
        Clock.schedule_interval(self._game.update, 1.0/15.0)
        return self._scatter


if __name__ == '__main__':

    #Config.set('kivy', 'show_fps', True)

    # adding asset path into kivy resources
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets'))
    for (dirpath, dirnames, filenames) in os.walk(assets_dir):
        kivy.resources.resource_add_path(dirpath)

    #cProfile.run('StratApp().run()')
    StratApp().run()
