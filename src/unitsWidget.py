#!/usr/bin/env python3

from kivy.uix.widget import Widget
from visualElement import Element

"""
This class is a container for elements
It sort the element by side and by position
"""

class UnitsWidget(Widget):

    def __init__(self, *args, **kargs):
        super(UnitsWidget, self).__init__(*args, **kargs)

        self.by_side = {}


    def add_widget(self, widget, *args, **kargs):
        super(UnitsWidget, self).add_widget(widget, *args, **kargs)

        assert type(widget) == Element

        side = id(self.by_side)
        self.by_side[side] = self.by_side.get(side, []) + [widget]

    def remove_widget(self, widget):
        super(UnitsWidget, self).remove_widget(widget)

        widget.by_side[widget.side].remove(widget)


    def get_side(self, side):
        return widget.by_side.get(id(side), [])

    def get_other_than_side(self, side):
        for cur_side, elems in self.by_side.items():
            if cur_side == id(side): continue
            for elem in elems: yield elem

#__EOF__