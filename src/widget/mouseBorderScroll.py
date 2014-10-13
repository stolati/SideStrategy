

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
#TODO maybe acceleration based on proximity with border ?
class MouseBorderScroll(ScrollView):

    border = VariableListProperty([10, 10, 10, 10])
    move_step = NumericProperty(10)

    # TODO remove when updated to last version
    def convert_distance_to_scroll(self, dx, dy):
        '''Convert a distance in pixels to a scroll distance, depending on the
        content size and the scrollview size.
        The result will be a tuple of scroll distance that can be added to
        :data:`scroll_x` and :data:`scroll_y`
        '''
        if not self._viewport:
            return 0, 0
        vp = self._viewport
        if vp.width > self.width:
            sw = vp.width - self.width
            sx = dx / float(sw)
        else:
            sx = 0
        if vp.height > self.height:
            sh = vp.height - self.height
            sy = dy / float(sh)
        else:
            sy = 1
        return sx, sy 



    def __init__(self, **kargs):
        super(MouseBorderScroll, self).__init__(**kargs)

        Window.bind(mouse_pos = self.on_mouse_pos)
        Window.bind(on_key_down = self.on_key_down)

        # TODO the whole stuff http://kivy.org/docs/api-kivy.core.window.html# 

        self.do_scroll_x = True
        self.do_scroll_y = True

    #pass the event to sub elements
    def on_touch_down(self, touch):
        self.dispatch_children_transform('on_touch_down', touch)

    def on_touch_up(self, touch):
        self.dispatch_children_transform('on_touch_up', touch)

    def on_touch_move(self, touch):
        self.dispatch_children_transform('on_touch_move', touch)

    #TODO when updated, a dispatch_children is created
    def dispatch_children_transform(self, event, touch):
        touch.push()
        touch.apply_transform_2d(self.to_local)
        for child in self.children[:]:
            if child.dispatch(event, touch):
                return True
        touch.pop



    def move(self, deltaX, deltaY):
        deltaX *= self.move_step
        deltaY *= self.move_step
        deltaX, deltaY = self.convert_distance_to_scroll(deltaX, deltaY)

        if deltaX != 0:
            self.scroll_x += deltaX
        if deltaY != 0:
            self.scroll_y += deltaY

        if deltaX != 0 or deltaY != 0:
            self._update_effect_bounds()

    def on_key_down(self, keyboard, keycode, keycode2, text, modifier):
        print('on_key_down')
        deltaX, deltaY = 0, 0
        print(keycode)
        print(keycode2)
        if keycode2 == 72: # up
            self.move(0, +1)
        if keycode2 == 80: # down
            self.move(0, -1)
        if keycode2 == 75: # left
            self.move(-1, 0)
        if keycode2 == 77: # right
            self.move(+1, 0)

        self.move(deltaX, deltaY)

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
            self.move(-1, 0)

        if x > (self.size[0] - border_x_size):
            self.move(+1, 0)

        if y < border_y_size:
            self.move(0, -1)

        if y > (self.size[1] - border_y_size):
            self.move(0, +1)

        #TODO change that by an event (so we can have a fixed speed)
        #TODO have a border (so we can't go too far)
        #TODO have properties for border and moving speed



