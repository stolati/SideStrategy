
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

cell_max_size = (255, 255)


class Visual(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.selected = False

    def update(self, dt, **kargs): raise NotImplemented()

    def remove(self): raise NotImplemented()


class ColorVisual(Visual):

    def __init__(self, color = named_colors.white, **kargs):
        super(ColorVisual, self).__init__(**kargs)
        self._graphics = None
        self._color = color
        self._graphicColor = None

    def _getSizeAndPos(self):
        posX, posY, sizeX, sizeY = self.parent.playmap.id2pos(*self.parent.pos)
        return (Pos(sizeX, sizeY), Pos(posX, posY))

    def update(self, dt, **kargs):

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphicColor = self._color()
            self._graphics = Rectangle(pos = pos, size = size)
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

    def __init__(self, **kargs):
        super(ColorDigger, self).__init__(**kargs)
        self.texture_handler = DiggerTexture()
        self.fbo = Fbo(size=cell_max_size)

    def update(self, dt, direction, **kargs):

        # update the fbo texture
        self.fbo.clear()
        with self.fbo:
            if self.selected:
                named_colors.violet()
            else:
                self._color()

            Rectangle(pos = (0, 0), size = cell_max_size)

            Rectangle(texture = self.texture_handler.getRightTexture(direction),
                pos = (0, 0), size = cell_max_size)

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphics = Rectangle(texture = self.fbo.texture, pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size


class ColorFlyer(ColorVisual):

    def __init__(self, **kargs):
        super(ColorFlyer, self).__init__(**kargs)
        self.texture_handler = FlyerTexture()
        self.fbo = Fbo(size=cell_max_size)

    def update(self, dt, direction, **kargs):

        # update the fbo texture
        self.fbo.clear()
        with self.fbo:
            if self.selected:
                named_colors.violet()
            else:
                self._color()
            Rectangle(texture = self.texture_handler.getRightTexture(direction),
                pos = (0, 0), size = cell_max_size)

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphics = Rectangle(texture = self.fbo.texture, pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size



class ColorWalker(ColorVisual):

    def __init__(self, **kargs):
        super(ColorWalker, self).__init__(**kargs)
        self.texture_handler_walking = WalkerWalkingTexture()
        #self.texture_handler_climbing = FlyerTexture()
        #self.texture_handler_jumping = FlyerTexture()
        self.fbo = Fbo(size=cell_max_size)

    def update(self, dt, direction, **kargs):

        # update the fbo texture
        self.fbo.clear()
        with self.fbo:
            if self.selected:
                named_colors.violet()
            else:
                self._color()

            direction = (self.parent.current_strategy.way, self.parent.current_strategy.status)

            Rectangle(texture = self.texture_handler_walking.getRightTexture(direction),
                pos = (0, 0), size = cell_max_size)

        size, pos = self._getSizeAndPos()

        if self._graphics is None:
            self._graphics = Rectangle(texture = self.fbo.texture, pos = pos, size = size)
        else :
            self._graphics.pos = pos
            self._graphics.size = size



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

    def unselected(self):
        self.visual.selected = False

    def selected(self):
        self.visual.selected = True


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
        self.textures = {
            Pos.right : Image('doodleDigger_right.png').texture,
            Pos.up : Image('doodleDigger_up.png').texture,
            Pos.left : Image('doodleDigger_left.png').texture,
            Pos.down : Image('doodleDigger_down.png').texture,
        }

    def getRightTexture(self, pos):
        return self.textures.get(pos, self.textures[Pos.down])


@singleton
class FlyerTexture(object):

    def __init__(self):
        self.textures = {
            Pos.right : Image('doodleFlyer_right.png').texture,
            Pos.up : Image('doodleFlyer_up.png').texture,
            Pos.left : Image('doodleFlyer_left.png').texture,
            Pos.down : Image('doodleFlyer_down.png').texture,
        }

    def getRightTexture(self, pos):
        return self.textures.get(pos, self.textures[Pos.up])


@singleton
class WalkerWalkingTexture(object):

    def __init__(self):
        self.textures = {
            (Pos.right, RunOnFloorStrategy._status_walking) :
                    Image('doodleWalkerWalking_right.png').texture,
            (Pos.left, RunOnFloorStrategy._status_walking) :
                    Image('doodleWalkerWalking_left.png').texture,

            (Pos.right, RunOnFloorStrategy._status_climbing) :
                    Image('doodleWalkerClimbing_right.png').texture,
            (Pos.left, RunOnFloorStrategy._status_climbing) :
                    Image('doodleWalkerClimbing_left.png').texture,

            (Pos.right, RunOnFloorStrategy._status_jumping) :
                    Image('doodleWalkerJumping.png').texture,
            (Pos.left, RunOnFloorStrategy._status_jumping) :
                    Image('doodleWalkerJumping.png').texture,
        }

    def getRightTexture(self, pos):
        return self.textures.get(pos, (Pos.right, RunOnFloorStrategy._status_walking) )


