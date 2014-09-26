
from pprint import pprint

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *

from kivy.core.image import Image

from strategies import *
from utils import *
from stratmap import *
from visualElement import *

from random import choice

class Visual(object):
    def __init__(self, parent = None):
        self.parent = parent

    def update(self, dt, **kargs): raise NotImplemented()

    def remove(self): raise NotImplemented()


class ColorVisual(Visual):

    def __init__(self, color = named_colors.white, **kargs):
        super(ColorVisual, self).__init__(**kargs)
        self._graphics = None
        self.color = color
        self._graphicColor = None

    def _getSizeAndPos(self):
        posX, posY, sizeX, sizeY = self.parent.playmap.id2pos(*self.parent.pos)
        return (Pos(sizeX, sizeY), Pos(posX, posY))

    def update(self, dt, **kargs):

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphicColor = self.color()
            self._graphics = Rectangle(source='doodleDigger.png', pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size

    def setShowable(self, showable):
        if showable == False:
            self.parent.playmap.canvas.remove(self._graphics)
            self.parent.playmap.canvas.remove(self._graphicColor)
            self._graphics = None
            self._graphicColor = None

    def remove(self):
        canvas = self.parent.playmap.canvas

        if self._graphics is not None:
            canvas.remove(self._graphics)
            self._graphics = None
        if self._graphicColor is not None:
            canvas.remove(self._graphicColor)
            self._graphicColor = None


class ColorDigger(ColorVisual):

    max_size = (256, 256)

    def __init__(self, **kargs):
        super(ColorDigger, self).__init__(**kargs)
        self.texture_handler = DiggerTexture()
        self.fbo = Fbo(size=ColorDigger.max_size)

    def update(self, dt, direction, **kargs):

        # update the fbo texture
        #self.fbo.clear()
        with self.fbo:
            self.color()
            Rectangle(texture = self.texture_handler.getRightTexture(direction),
                pos = (0, 0), size = ColorDigger.max_size)

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphics = Rectangle(texture = self.fbo.texture, pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size



    #def update(self, dt, direction, **kargs):
    #    print('updating digger') 
    #    super(ColorDigger, self).update(dt, **kargs)

    #    self._graphics.source = self.texture_handler.getRightTexture(direction)


class Element(object):

    def __init__(self, category, playmap, startPos, visual, strategy, side, viewfield, speed):

        self.category = category
        self.playmap, self.pos = playmap, startPos
        self.default_strategy, self.current_strategy = strategy, strategy
        self.visual = visual
        self.visual.parent = self
        self.side = side
        self.viewfield = viewfield
        self.speed = speed
        self.direction = Pos(0, 0)

        self.viewfield.parent = self
        self.current_strategy.parent = self

    def deleteMe(self):
        #deleting from the map
        try: #TODO do a better handling of deleting elements
            self.playmap._map.elements.remove(self)
            self.visual.remove()
            self.side.remove(self)
        except:
            pass 

    def setStrategy(self, strategy):
        self.current_strategy = strategy
        self.current_strategy.parent = self

    def endStrategy(self):
        self.current_strategy = self.default_strategy
        self.current_strategy.parent = self

    def tick(self):
        previousPos = self.pos
        self.current_strategy.action()
        if self.pos is None:
            return
        new_direction = Pos(self.pos.x - previousPos.x, self.pos.y - previousPos.y)
        if new_direction.x != 0 or new_direction.y != 0:
            self.direction = new_direction

    def draw(self, dt):
        self.visual.update(dt, direction = self.direction)


# From http://legacy.python.org/dev/peps/pep-0318/#examples
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton #singleton so we load once
class DiggerTexture(object):

    def __init__(self):
        self.right = Image('doodleDigger_right.png').texture
        self.up = Image('doodleDigger_up.png').texture
        self.left = Image('doodleDigger_left.png').texture
        self.down = Image('doodleDigger_down.png').texture

    def getRightTexture(self, pos):
        if pos == Pos(+1, 0):
            return self.right
        if pos == Pos(-1, 0):
            return self.left
        if pos == Pos(0, +1):
            return self.up
        if pos == Pos(0, -1):
            return self.down
        print(pos)
        return self.left


# file names : 
# doodleDigger.png
# doodlePlanner.png
# doodleWalkerClimbing.png
# doodelWalkerJumping.png
# doodleWalkerWalking.png
#
