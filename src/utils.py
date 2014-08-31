
from kivy.graphics import Color

from collections import namedtuple


class Pos(namedtuple('Pos', 'x y')):
    """Immutable position as named tuple"""

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def addX(self, x):
        return Pos(self.x + x, self.y)

    def addY(self, y):
        return Pos(self.x, self.y + y)


class NamedColor:

	def __init__(self, r, g, b):
		self.r, self.g, self.b = r, g, b
		self.rgb = (r, g, b)

	def __call__(self):
		return Color(self.r, self.g, self.b)

class NamedColors:
    colors = {
        'red':(1,0,0),
        'green':(0,1,0),
        'blue':(0,0,1),

        'cyan':(0,1,1),
        'purple':(1,0,1),
        'yellow':(1,1,0),

        'black':(0,0,0),
        'white':(1,1,1),

        'gray':(.5, .5, .5),
    }

    def __getattr__(self, name):
        return NamedColor(*NamedColors.colors[name])

named_colors = NamedColors()


