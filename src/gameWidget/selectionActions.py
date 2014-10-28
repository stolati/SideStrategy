
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


class SelectionActions(StackLayout):

    sub_element_size_hint = ObjectProperty((.5, .05))
    action = ObjectProperty(None, allownone = True)

    def __init__(self, **kargs):
        super(SelectionActions, self).__init__(**kargs)
        self.button_hash = {}
        self.last_action = None #keep action even if list change

    def change_selection(self, stratGame, elements):

        self.last_action = self.action

        new_actions = set()
        for element in elements:
            #for action in element.getActions():
            for action in ['move', 'attack', 'createUnit']:
                new_actions.add(action)

        self.clear_widgets()
        self.button_hash = {}
        for action in sorted(new_actions):
            self.createActionButton(action)

        if self.last_action in new_actions:
            self.action = self.last_action
        else:
            self.action = None


    def createActionButton(self, action):
        b = Button(text = action, size_hint = self.sub_element_size_hint)
        def on_press(btt): self.action = action
        b.bind(on_press = on_press)

        self.button_hash[action] = b
        self.add_widget(b)

    def on_action(self, self_again, action):
        btt_object = self.button_hash.get(action)

        for child in self.children:
            if child == btt_object:
                child.background_color = [1, .5, .5, 1]
            else:
                child.background_color = [1, 1, 1, 1]

