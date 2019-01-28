import pyglet
from Particles.utils import Transform
from Particles.models import simulation

# Create pyglet window
WIN_SIZE = (680, 680)
win = pyglet.window.Window(width = WIN_SIZE[0], height = WIN_SIZE[1], resizable=True)
win.set_caption("Particles")
win.set_vsync(False)

# Setup transform
Transform.set_win_size(win.width, win.height)

@win.event
def on_resize(w, h):
    s = min(w, h)
    Transform.set_win_size(s, s)
