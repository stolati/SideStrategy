#!/usr/bin/kivy
import kivy

# http://stackoverflow.com/questions/20625312/can-i-run-a-kivy-program-from-within-pyscripter

# Things to do after :

# - click handle (left/right) with position
# - link a strategy to the element
# - having a digger (not a gold one)

# - bigger than 1x1 elements (so we can go to )
# - groups of elements in the same clan
# - an interface with mouse to pop elements
# - click to ask an element to go somewhere




from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *

from strategies import *
from utils import *
from stratmap import *
from visualElement import *


visual_marge = 0.01


class StratGame(Widget):

    def __init__(self, stratMap, **kargs):
        super(StratGame, self).__init__(**kargs)
        self._map = stratMap
        stratMap.playmap = self

        self.cellx, self.celly = stratMap.size

        pos1, elem1 = stratMap.findElement(lambda e : e.isStart() and e.getStartNum() == 1)[0]
        pos2, elem2 = stratMap.findElement(lambda e : e.isStart() and e.getStartNum() == 2)[0]


        visualGreen = ColorVisual(color = named_colors.green)
        e1 = Element(self, visual = visualGreen, strategy = MotherShipStrategy(speed = 3), startPos = pos1)

        visualRed = ColorVisual(color = named_colors.red)
        e2 = Element(self, visual = visualRed, strategy = MotherShipStrategy(), startPos = pos2)

        self._map.elements.append(e1)
        self._map.elements.append(e2)

        self._graphics = None # violet rectangle in background
        
        #visualGreen = ColorVisual.buildForElement(color = named_colors.green)
        #visualYellow = ColorVisual.buildForElement(color = named_colors.yellow)

        #self._map.elements.append(Element(self, visual = visualGreen))
        #self._map.elements.append(Element(self, strategy = RandomStrategy))
        #self._map.elements.append(Element(self, strategy = BounceStrategy,
        #    visual = visualYellow, startPos = Pos(2, 2)))
        
        #Clock.schedule_once(lambda dt: self.drawCells(), 1.0/60.0)


    def id2pos(self, x, y):
        """left 10 percent on each side"""
        hStep, wStep = self.height * visual_marge, self.width * visual_marge

        quantumy = (self.height - (2 * hStep)) / self.celly
        quantumx = (self.width - (2 * wStep)) / self.cellx

        if x % 2 == 0:
            return (x * quantumx + wStep, y * quantumy + hStep, quantumx, quantumy)
        else:
            return (x * quantumx + wStep, (y * quantumy) + (quantumy / 2) + hStep, quantumx, quantumy)



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
        # (len(self.canvas.get_group(None)))
        with self.canvas:

            if self._graphics is None:
                Color(0.5, 0, 1)
                #127, 0, 255                
                self._graphics = Rectangle(pos = (0, 0), size = (self.width, self.height))
            else :
                self._graphics.pos = (0, 0)
                self._graphics.size = (self.width, self.height)

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

        #self._map = loadMapFromFile('map03')

        self._map = generateMap()

        self._game = StratGame(self._map)
        Clock.schedule_interval(self._game.update, 1.0/60.0)
        #Clock.schedule_interval(self._game.update, 1.0/15.0)
        return self._game


if __name__ == '__main__':
    StratApp().run()
