import pyglet, os, json
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

# Initialise config
def setup_config(fname):

    CONFIG = dict()
    if os.path.exists(fname):
        with open(fname, 'r') as cfile:
            CONFIG = json.load(cfile)
    else:
        print("Config file not found: '{}'".format(fname))
    return CONFIG

CONFIG = setup_config("./config.json")

