"""
    Utility methods related to creating shapes in pyglet.
    Since the GL primitives require points, these methods provide 
    the right data to pass to pyglet.graphics.draw()
"""
import math
import pyglet
from Particles.utils import Transform

def make_label(text, pos = (0, 0), size=16, anchor_x='center', anchor_y='center', batch=None):

    screenpos = Transform.world_to_screen(pos)
    label = pyglet.text.Label(text, font_name='Arial', font_size=size,
                                            x=screenpos[0], y=screenpos[1],
                                            anchor_x=anchor_x, anchor_y=anchor_y, batch=batch)
    return label

def make_point(pos, color = (255, 255, 255)):
    pos = Transform.world_to_screen(pos)
    point = pyglet.graphics.vertex_list(1, ('v2f', [pos[0], pos[1]]), ('c3B', [color[0], color[1], color[2]]))
    return point

def make_points(points, color = (255, 255, 255), as_vertexlist = False):
    verts = list()
    colors = list()
    for p in points:
        pos = Transform.world_to_screen(p)
        verts += [pos[0], pos[1]]
        colors += [color[0], color[1], color[2]]
    points = (('v2f', verts), ('c3B', colors))
    if as_vertexlist:
        points = pyglet.graphics.vertex_list(len(points), ('v2f', verts), ('c3B', colors))
    return points

def make_circle(n_points = 100, center = (0, 0), radius = 1, color = (255, 255, 255), as_vertexlist = False):
    c = Transform.world_to_screen(center)
    r = (Transform.WIN_WIDTH * radius, Transform.WIN_HEIGHT * radius)
    # Add degenerated vertex in front
    verts = [c[0], c[1]]
    colors = [color[0], color[1], color[2]]
    # Make main circle
    for i in range(n_points):
        angle = math.radians(float(i)/n_points * 360.0)
        x = r[0]*math.cos(angle) + c[0]
        y = r[1]*math.sin(angle) + c[1]
        verts += [x,y]
        colors += [color[0], color[1], color[2]]
    # Add final degenerated vertex
    verts += [r[0]*math.cos(0) + c[0], r[1]*math.sin(0) + c[1]]
    colors += [color[0], color[1], color[2]]

    # Create indices
    indices = list()
    for side in range(1, n_points+1):
        indices.append(0)
        indices.append(side)
        indices.append(side+1)
    
    circle = (indices, ('v2f', verts), ('c3B', colors))
    if as_vertexlist:
        circle = pyglet.graphics.vertex_list(int(len(verts) / 2), ('v2f', verts), ('c3B', colors))
    return circle

def make_line(a, b, n_points = 2, thickness = 1, color = (255, 255, 255)):
    a = Transform.world_to_screen(a)
    b = Transform.world_to_screen(b)
    thickness = max(thickness, 0.1)
    verts = [a[0], a[1], b[0], b[1]]
    colors = list()
    for v in verts:
        colors += [color[0], color[1], color[2]]
    pyglet.gl.glLineWidth(thickness)
    line = pyglet.graphics.vertex_list(n_points, ('v2f', verts))
    return line

def make_rect(top_left, w, h, color=(255, 255, 255), as_vertexlist = False):

    #top_left = Transform.world_to_screen(top_left)
    #size = Transform.world_to_screen((w, h))
    #w = size[0]
    #h = size[1]
    verts = list()
    colors = list()

    # Add corners to rectangle
    P_top_left = Transform.world_to_screen(top_left)
    verts += [P_top_left[0], P_top_left[1]]
    P_top_right = Transform.world_to_screen((top_left[0]+ w, top_left[1]))
    verts += [P_top_right[0], P_top_right[1]]
    P_bot_right = Transform.world_to_screen((top_left[0] + w, top_left[1] - h))
    verts += [P_bot_right[0], P_bot_right[1]]
    P_bot_left = Transform.world_to_screen((top_left[0], top_left[1] - h))
    verts += [P_bot_left[0], P_bot_left[1]]

    for _ in range(4):
        colors += [color[0], color[1], color[2]]

    rect = (('v2f', verts), ('c3B', colors))
    if as_vertexlist:
        rect = pyglet.graphics.vertex_list(4, ('v2f', verts), ('c3B', colors))
    return rect