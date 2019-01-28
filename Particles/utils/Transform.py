import math

WIN_WIDTH = 300
WIN_HEIGHT = 400

def set_win_size(w, h):
    global WIN_WIDTH 
    WIN_WIDTH= w
    global WIN_HEIGHT 
    WIN_HEIGHT = h

def world_to_screen(pos):
    global WIN_WIDTH
    global WIN_HEIGHT
    ratio_x = WIN_WIDTH / 2.0
    ratio_y = WIN_HEIGHT / 2.0
    x = (pos[0] * ratio_x) + ratio_x
    y = (pos[1] * ratio_y) + ratio_y
    return (x, y)

def screen_to_world(pos):
    global WIN_WIDTH
    global WIN_HEIGHT
    ratio_x = WIN_WIDTH / 2.0
    ratio_y = WIN_HEIGHT / 2.0
    x = (pos[0] - ratio_x) / ratio_x
    y = (pos[1] - ratio_y) / ratio_y
    return (x, y)

def dist(pos1, pos2):
    d_x = (pos1[0] - pos2[0])
    d_y = (pos1[1] - pos2[1])

    return math.sqrt((d_x * d_x) + (d_y * d_y))


def dist_squared(pos1, pos2):
    d_x = (pos1[0] - pos2[0])
    d_y = (pos1[1] - pos2[1])

    return (d_x * d_x) + (d_y * d_y)


def get_oscillator(amp=1, period=1, shift=0):
    return lambda x: (amp * math.sin(period * x)) + shift