#!/usr/bin/kivy
import kivy
# sartup with http://stackoverflow.com/questions/20625312/can-i-run-a-kivy-program-from-within-pyscripter

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *

from random import random

colors = {
    'red':(1,0,0),
    'blue':(0,1,0),
    'yellow':(1,1,0),
    'black':(0,0,0),
    'white':(1,1,1),
}

mapSize = (20, 20)

class StratGame(Widget):

    def id2pos(self, x, y):
        """return the box of position (startx, starty, sizex, sizey)"""
        quantumy = self.height / self.celly
        quantumx = self.width / self.cellx

        return (x * quantumx, y * quantumy, quantumx, quantumy)

    def pos2id(self, x, y):
        """return the position to which the id is in (x, y)"""
        quantumy = self.height / self.celly
        quantumx = self.width / self.cellx
        return (x // quantumx, y // quantumy)

    def __init__(self, size, **kargs):
        super(StratGame, self).__init__(**kargs)
        self.cellx, self.celly = size
        Clock.schedule_once(lambda dt: self.drawstuff(), 1.0/60.0)

    def drawstuff(self):
        with self.canvas:
            for x in range(self.cellx):
                for y in range(self.celly):
                    Color(random(), random(), random())
                    posX, posY, sizeX, sizeY = self.id2pos(x, y)
                    Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

    def update(self, dt):
        #self.drawstuff()
        pass

    def on_touch_move(self, touch):
        """Blacken the cases when the mouse touch a case"""
        with self.canvas:
            Color(*colors['black'])
            idx, idy = self.pos2id(*touch.pos)
            posX, posY, sizeX, sizeY = self.id2pos(idx, idy)
            Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*colors['black'])
            idx, idy = self.pos2id(*touch.pos)
            posX, posY, sizeX, sizeY = self.id2pos(idx, idy)
            Rectangle(pos=(posX, posY), size=(sizeX, sizeY))

class StratApp(App):
    def build(self):
        game = StratGame(mapSize)
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game

if __name__ == '__main__':
    StratApp().run()
