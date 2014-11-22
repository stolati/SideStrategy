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
        print('adding widget %s' % widget.name)

        assert type(widget) == Element

        side_id = id(widget.side)
        side_set = self.by_side.get(side_id, set())
        side_set.add(widget)
        self.by_side[side_id] = side_set

    def remove_widget(self, widget):
        super(UnitsWidget, self).remove_widget(widget)
        print('removing widget : ' + widget.name)

        side_id = id(widget.side)

       	side_set = self.by_side[side_id]
       	assert widget in side_set
       	side_set.remove(widget) 


    def get_side(self, side):
        return self.by_side.get(id(side), [])

    def get_other_than_side(self, side):
        for cur_side, elems in self.by_side.items():
            if cur_side == id(side): continue
            for elem in elems: yield elem

    def on_size(self, *args):
    	print('!!!!!!!!!!')
    	print('!!!!!!!!!!')
    	print('!!!!!!!!!!')
    	print('!!!!!!!!!!')
    	print('!!!!!!!!!!')
    	print('!!!!!!!!!!')

#__EOF__