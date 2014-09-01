
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

class Visual:
    def __init__(self, parent = None):
        self.parent = parent

    def update(self, dt): raise NotImplemented()

    def remove(self): raise NotImplemented()


class ColorVisual(Visual):

    def __init__(self, color = named_colors.white, **kargs):
        super(ColorVisual, self).__init__(**kargs)
        self._graphics = None
        self.color = color

    def update(self, dt):

        posX, posY, sizeX, sizeY = self.parent.playmap.id2pos(*self.parent.pos)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        if self._graphics is None:
            self.color()
            self._graphics = Rectangle(pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size

    def remove(self):
        self.parent.playmap.canvas.remove(self._graphics)


class Element:

    def __init__(self, playmap, startPos, visual, strategy):

        self.playmap, self.pos = playmap, startPos
        self.strategy = strategy
        self.visual = visual
        self.strategy.parent = self
        self.visual.parent = self

    def deleteMe(self):
        #deleting from the map
        try: #TODO do a better handling of deleting elements
            self.playmap._map.elements.remove(self)
            self.visual.remove()
        except:
            pass 




