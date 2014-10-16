
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import *
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *
import kivy.resources
from kivy.graphics.transformation import Matrix
from kivy.uix.button import *
from kivy.core.window import Window
from kivy.uix.stacklayout import StackLayout


class SelectionUnits(StackLayout):

    sub_element_size_hint = ObjectProperty((.5, .05))

    def change_selection(self, stratGame, elements):

        self.clear_widgets()

        for element in elements:
            b = UnitSelected(element, size_hint=self.sub_element_size_hint)
            self.add_widget(b)


class UnitSelected(Button, Label):

    def __init__(self, element, **kargs):
        super(UnitSelected, self).__init__(**kargs)
        self._element = element
        self._graphics = None




    def on_pos(self, *args): self._refresh()
    def on_size(self, *args): self._refresh()

    def _refresh(self):

        texture = self._element.visual.fbo.texture

        if self._graphics is None:
            with self.canvas:
                self._graphics = Rectangle(texture = texture,
                    pos = self.pos, size = self.size)
        else:
            self._graphics.size = self.size
            self._graphics.pos = self.pos

