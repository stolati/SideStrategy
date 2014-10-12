

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
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

from kivy.core.window import Window
from kivy.input.motionevent import MotionEvent

from kivy.uix.scrollview import ScrollView

#TODO maybe use a simplier class (intead of the whole package)
#TODO for selection, get how the events are dispatched
class MouseBorderScroll(ScrollView):

    border = VariableListProperty([10, 10, 10, 10])

    def __init__(self, **kargs):
        super(MouseBorderScroll, self).__init__(**kargs)

        Window.bind(mouse_pos = self.on_mouse_pos)
        self.do_scroll_x = True
        self.do_scroll_y = True

    #def on_touch_down(self, touch): pass # do nothing
    #def on_touch_up(self, touch): pass # do nothing
    #def on_touch_move(self, touch): pass # do nothing

    def on_mouse_pos(self, window, pos):
        x, y = pos
        if not self.collide_point(x, y):
            # only return colliding events
            return False

        wx, wy = self.pos
        x, y = x - wx, y - wy

        # just to be sure
        assert x >= 0
        assert y >= 0
        assert x <= self.size[0]
        assert y <= self.size[1]

        border_x_size = self.size[0] / 10
        border_y_size = self.size[1] / 10

        if x < border_x_size:
            self.scroll_x -= 0.1

        if x > (self.size[0] - border_x_size):
            self.scroll_x += 0.1

        if y < border_y_size:
            self.scroll_y -= 0.1

        if y > (self.size[1] - border_y_size):
            self.scroll_y += 0.1

        #TODO change that by an event (so we can have a fixed speed)
        #TODO have a border (so we can't go too far)
        #TODO have properties for border and moving speed



