
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import *
from kivy.graphics import *


class Selection(RelativeLayout):

    selection = ObjectProperty(None, allownone = True)
    color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kargs):
        super(Selection, self).__init__(**kargs)

        self._grabbing = False
        self._start_pos = None

    def on_touch_down(self, touch):

        if getattr(touch, 'device', None) != 'mouse' \
                or getattr(touch, 'button', None) != 'left' \
                or getattr(touch, 'is_double_tap', None) != False \
                or getattr(touch, 'is_triple_tap', None) != False:
            return False

        self._grabbing = True
        self._start_pos = touch.pos

        return True 

    def on_touch_move(self, touch):

        #TODO make sure that the move/up are from the initial touch down
        #(we can have a multi touch down/move/up at the same time)

        if not self._grabbing:
            return False

        xStart, yStart = self._start_pos
        xEnd, yEnd = touch.pos

        self.canvas.after.clear()
        with self.canvas.after:
            Color(1, 1, 1, 1)
            Line(points = (
                xStart, yStart, 
                xEnd, yStart,
                xEnd, yEnd,
                xStart, yEnd,
                xStart, yStart, 
            ))

        return True

    def on_touch_up(self, touch):

        if not self._grabbing:
            return False

        self.canvas.after.clear()

        x1, y1 = self._start_pos
        x2, y2 = touch.pos

        xStart, xEnd = min(x1, x2), max(x1, x2)
        yStart, yEnd = min(y1, y2), max(y1, y2)

        self.selection = (xStart, yStart, xEnd, yEnd)

        # initialize anew
        self._start_pos = None
        self._grabbing = False

        return True

