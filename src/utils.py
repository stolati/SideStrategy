
from kivy.graphics import Color

from collections import namedtuple


class Pos(namedtuple('Pos', 'x y')):
    """Immutable position as named tuple"""

    right = None
    left  = None
    up    = None
    down  = None

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def __mul__(self, i):
        return Pos(self.x * i, self.y * i)

    def __div__(self, i):
        return Pos(self.x // i, self.y // i)

    def addX(self, x):
        return Pos(self.x + x, self.y)

    def addY(self, y):
        return Pos(self.x, self.y + y)


Pos.right = Pos(+1, 0)
Pos.left  = Pos(-1, 0)
Pos.up    = Pos(0, +1)
Pos.down  = Pos(0, -1)


class NamedColor(object):

	def __init__(self, r, g, b, t = 1):
		self.r, self.g, self.b, self.t = r, g, b, t
		self.rgb = (r, g, b)

	def __call__(self):
		return Color(self.r, self.g, self.b, self.t)

class NamedColors(object):
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
        'none':(1, 1, 1, 0),
        'violet':(.5, 0, 1),
        'brown':(.5, .25, .25),
    }

    def __getattr__(self, name):
        return NamedColor(*NamedColors.colors[name])

named_colors = NamedColors()


