
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
    def __init__(self, element = None):
        self.element = element

    @classmethod
    def buildForElement(klass, **kargs):
        return lambda e:klass(element = e, **kargs)

    def update(self, dt): raise NotImplemented()


class ColorVisual(Visual):

    def __init__(self, color = named_colors.white, **kargs):
        super(ColorVisual, self).__init__(**kargs)
        self._graphics = None
        self.color = color

    def update(self, dt):

        posX, posY, sizeX, sizeY = self.element.playmap.id2pos(*self.element.pos)
        pos = (posX, posY)
        size = (sizeX, sizeY)

        if self._graphics is None:
            self.color()
            self._graphics = Rectangle(pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size


class Element:

    def __init__(self, playmap, startPos = Pos(0, 0),
            visual = ColorVisual.buildForElement(),
            strategy = PoopFloorStrategy):

        self.playmap, self.pos = playmap, startPos
        self.strategy = strategy(self)
        self.visual = visual(self)

    def update(self, dt):
        self.visual.update(dt)
