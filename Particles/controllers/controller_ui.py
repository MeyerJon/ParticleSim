import pyglet
from Particles.utils import Shapes, Transform
from Particles.controllers import controls


class CUI_object:

    def __init__(self, anchor):

        self.anchor = anchor
        self.parent = None
        self.children = list()
        self.shape = None
    
    def draw(self):

        for child in self.children:
            child.draw()

    def rescale(self, s):

        for c in self.children:
            c.rescale(s)

    def on_click(self):
        raise NotImplementedError

    def is_clicked(self, pos):
        """ Returns True if pos is within the boundaries of this object. """
        raise NotImplementedError


class CUI_canvas(CUI_object):

    def __init__(self, anchor, w, h, color=(100, 100, 100)):

        super().__init__(anchor)

        self.w = w
        self.h = h
        self.color = color
        self.shape = Shapes.make_rect(self.anchor, self.w, self.h, color=self.color, as_vertexlist = True)

    def draw(self):
        verts, colors = Shapes.make_rect(self.anchor, self.w, self.h, color=self.color)
        self.shape.vertices = verts[1]
        self.shape.draw(pyglet.gl.GL_POLYGON)

        super().draw()

    def is_clicked(self, pos):

        if pos[0] > self.anchor[0] and pos[0] < self.anchor[0] + self.w \
           and pos[1] < self.anchor[1] and pos[1] > self.anchor[1] - self.h:

            # Click is inside rect
            return True
        
        return False

    def on_click(self, controller, pos, btn):

        # Pass event through children to determine 'actual' target & execute on_click of that target

        for c in self.children:
            if c.is_clicked(pos):
                c.on_click(controller, pos, btn)


class CUI_label(CUI_object):

    def __init__(self, anchor, size, text):

        super().__init__(anchor)

        self.text = text
        self.size = size
        self.label = Shapes.make_label(self.text, self.anchor, self.size, anchor_x='left', anchor_y='top')

    def draw(self):
        # Resize if parent exists
        if self.parent is not None:
            self.label.size = (self.parent.w / self.parent.h)
        self.label.draw()

        super().draw()

    def is_clicked(self, pos):
        return False # Labels aren't clickable


class ControllerUI:

    def __init__(self):

        self.visible = False
        self.anchor = (0.6, 1) #(1.05, 1)
        self.elements = list()

        # Setup background
        self.bg = CUI_canvas(self.anchor, w=0.4, h=2)
        self.elements.append(self.bg)

        setup_UI(self)

    # Adding elements
    
    def add_element(self, e, parent=None):
        """ Adds an element to to UI. """
        if parent is not None:
            parent.children.append(e)
        else:
            self.elements.append(e)

    def add_button(self, anchor, w, h, color=(220, 220, 220), parent=None, on_click=None):
        """ Adds a button. """

        btn_anchor = (anchor[0], anchor[1])
        btn = CUI_canvas(btn_anchor, w, h, color=color)
        if on_click is not None:
            btn.on_click = on_click
        
        self.add_element(btn, parent)


    # Event handling
    def on_click(self, controller, pos, btn):
        """ Takes (World) position of click from Controller and passes it to elements. """
        
        if not self.visible or abs(pos[0]) < self.anchor[0]:
            return False

        for e in self.elements:
            if e.is_clicked(pos):
                e.on_click(controller, pos, btn)
        
        return True


    # Drawing the UI
    def draw(self):

        if not self.visible:
            return

        self.bg.draw()
    

def setup_UI(c):
    """ Sets up a controller's UI. """

    calc_anchor_x = lambda p_x, p_w, w: (p_x + ((p_w - w) / 2))

    # Simulation pause button
    pause_btn_w = c.bg.w * 0.5
    pause_btn_h = 0.1
    pause_btn_anchor = (c.bg.anchor[0] + (pause_btn_w / 2.0), c.bg.anchor[1] - 0.1)
    pause_btn_func = lambda c, p, btn: controls.toggle_pause(c.sim)
    c.add_button(pause_btn_anchor, pause_btn_w, pause_btn_h, 
                 color=(180, 10, 5), parent=c.bg, on_click=pause_btn_func)

    # Particle control panel
    pc_panel_w = c.bg.w * 0.9
    pc_panel_h = 0.5
    pc_panel_anchor = (calc_anchor_x(c.bg.anchor[0], c.bg.w, pc_panel_w), c.bg.anchor[1] - 1.475)
    pc_panel = CUI_canvas(pc_panel_anchor, pc_panel_w, pc_panel_h, color=(180, 180, 180))
    c.add_element(pc_panel, c.bg)

    pc_panel_label = CUI_label(pc_panel_anchor, 11, "Particle control")
    #c.add_element(pc_panel_label, pc_panel)
    
    # Particle trail density controllers
    ptc_d_w = pc_panel_w * 0.275
    ptc_d_h = ptc_d_w * 0.85
    ptc_d_gap = 0.03
    ptc_d_color = (90, 90, 150)
    ptc_d_decr_anchor = (calc_anchor_x(pc_panel_anchor[0], pc_panel_w, (2*ptc_d_w + ptc_d_gap)), pc_panel_anchor[1] - 0.075)
    ptc_d_inc_anchor = (ptc_d_decr_anchor[0] + ptc_d_w + ptc_d_gap, ptc_d_decr_anchor[1])
    ptc_d_decr_f = lambda c, p, btn: controls.cycle_trail_density(c._cur_selected, increase=False)
    ptc_d_inc_f = lambda c, p, btn: controls.cycle_trail_density(c._cur_selected, increase=True)
    c.add_button(ptc_d_decr_anchor, ptc_d_w, ptc_d_h, color=ptc_d_color, parent=pc_panel, on_click=ptc_d_decr_f)
    c.add_button(ptc_d_inc_anchor, ptc_d_w, ptc_d_h, color=ptc_d_color, parent=pc_panel, on_click=ptc_d_inc_f)

    # Particle trail length controllers
    ptc_l_w = pc_panel_w * 0.275
    ptc_l_h = ptc_l_w * 0.85
    ptc_l_gap = 0.03
    ptc_l_color = (90, 150, 90)
    ptc_l_decr_anchor = (calc_anchor_x(pc_panel_anchor[0], pc_panel_w, (2*ptc_l_w + ptc_l_gap)), pc_panel_anchor[1] - ptc_l_h - 0.12)
    ptc_l_inc_anchor = (ptc_l_decr_anchor[0] + ptc_l_w + ptc_l_gap, ptc_l_decr_anchor[1])
    ptc_l_decr_f = lambda c, p, btn: controls.cycle_trail_length(c._cur_selected, increase=False)
    ptc_l_inc_f = lambda c, p, btn: controls.cycle_trail_length(c._cur_selected, increase=True)
    c.add_button(ptc_l_decr_anchor, ptc_l_w, ptc_l_h, color=ptc_l_color, parent=pc_panel, on_click=ptc_l_decr_f)
    c.add_button(ptc_l_inc_anchor, ptc_l_w, ptc_l_h, color=ptc_l_color, parent=pc_panel, on_click=ptc_l_inc_f)
    