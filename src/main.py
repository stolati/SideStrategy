#!/usr/bin/kivy
import kivy
# sartup with http://stackoverflow.com/questions/20625312/can-i-run-a-kivy-program-from-within-pyscripter

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *

from strategies import *
from utils import *

mapSize = (40, 20)


class StratMap:

    def __init__(self, size):
        self._map = [[None for y in range(size[0])] for y in range(size[1])]
        self.elements = []

    def get(x, y):
        return self._map[x][y]

    def set(x, y, v):
        self._map[x][y] = v

    def update(self, dt):
        for e in self.elements:
            e.update(dt)


class VisualElement:

    def __init__(self, playmap, startPos = Pos(0, 0),
            color = named_colors.white, strategy = GoEastStrategy):
        self.playmap, self.pos, self.color = playmap, startPos, color
        self.strategy = strategy(self)

        self._graphics = None

    def update(self, dt):
        self.strategy.action()

        posX, posY, sizeX, sizeY = self.playmap.id2pos(*self.pos)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        if self._graphics is None:
            self.color()
            self._graphics = Rectangle(pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size


class StratGame(Widget):

    def __init__(self, size, **kargs):
        super(StratGame, self).__init__(**kargs)
        self.cellx, self.celly = size
        
        self._map = StratMap(size)
        self._map.elements.append(VisualElement(self, color = named_colors.green))
        self._map.elements.append(VisualElement(self, strategy = RandomStrategy))
        self._map.elements.append(VisualElement(self, strategy = BounceStrategy, color = named_colors.yellow))
        
        #Clock.schedule_once(lambda dt: self.drawCells(), 1.0/60.0)



    def id2pos(self, x, y):
        """return the box of position (startx, starty, sizex, sizey)"""
        quantumy = self.height / self.celly
        quantumx = self.width / self.cellx

        return (x * quantumx, y * quantumy, quantumx, quantumy)

    def pos2id(self, x, y):
        """return the position to which the id is in (x, y)"""
        quantumy = self.height / self.celly
        quantumx = self.width / self.cellx
        return (x // quantumx, y // quantumy)


    def drawCells(self):
        with self.canvas:
            for x in range(self.cellx):
                for y in range(self.celly):
                    Color(random(), random(), random())
                    posX, posY, sizeX, sizeY = self.id2pos(x, y)
                    Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

    def update(self, dt):
        print(len(self.canvas.get_group(None)))
        with self.canvas:
            self._map.update(dt)

    def on_touch_move(self, touch):
        """Blacken the cases when the mouse touch a case"""
        with self.canvas:
            Color(*colors['black'])
            idx, idy = self.pos2id(*touch.pos)
            posX, posY, sizeX, sizeY = self.id2pos(idx, idy)
            Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*colors['black'])
            idx, idy = self.pos2id(*touch.pos)
            posX, posY, sizeX, sizeY = self.id2pos(idx, idy)
            Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

class StratApp(App):

    def build(self):
        self._game = StratGame(mapSize)
        #Clock.schedule_interval(self._game.update, 1.0/60.0)
        Clock.schedule_interval(self._game.update, 1.0/15.0)
        return self._game


if __name__ == '__main__':
    StratApp().run()
