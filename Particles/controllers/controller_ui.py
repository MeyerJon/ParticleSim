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

    def on_drag(self):
        raise NotImplementedError

    def child_clicked(self, pos):
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

    def child_clicked(self, pos):

        if pos[0] > self.anchor[0] and pos[0] < self.anchor[0] + self.w \
           and pos[1] < self.anchor[1] and pos[1] > self.anchor[1] - self.h:

            # Click is inside rect, check if any children clicked
            clicked = self
            for c in self.children:
                descendant_clicked = c.child_clicked(pos)
                if descendant_clicked is not None:
                    clicked = descendant_clicked
            return clicked
            
        return None

    def on_click(self, controller, pos, btn):
        return # Default canvas not clickable

    def on_drag(self, controller, pos, diff, btn):
        return # Canvas not (yet?) draggable


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


class CUI_slider(CUI_object):

    def __init__(self, anchor, w, h, min_val=0, max_val=1):

        super().__init__(anchor)

        self.w = w
        self.h = h

        # Values
        self.speed = 7.5
        self.value = min_val
        self.min_val = min_val
        self.max_val = max_val

        # Graphics
        self.bar = CUI_canvas(self.anchor, self.w, self.h, color=(120, 120, 120))
        self.bar.on_click = self.on_click
        self.children.append(self.bar)
        # Slider selector
        slider_w = self.w * 0.13
        slider_h = self.h * 1.85
        slider_anchor = (self.anchor[0] - slider_w / 2.0, self.anchor[1] - ((self.h - slider_h) / 2.0))
        self.slider = CUI_canvas(slider_anchor, slider_w, slider_h, color=(180, 20, 20))
        self.slider.parent = self
        self.slider.on_drag = self.on_drag # Otherwise, the canvas' on_drag is called by the ControllerUI
        self.children.append(self.slider)

    def child_clicked(self, pos):
        slider_clicked = self.slider.child_clicked(pos)
        if slider_clicked is not None:
            return self.slider
        else:
            return self.bar.child_clicked(pos)

    def on_click(self, controller, pos, btn):
        # Set the selector & value according to the click
        self.slider.anchor = (pos[0] - (self.slider.w / 2.0), self.slider.anchor[1])
        ratio = (pos[0] - self.anchor[0]) / self.w
        self.value = ratio * (self.max_val - self.min_val)
        self.on_change(self, controller)

    def on_drag(self, controller, pos, diff, btns):
        # Keep the selector under the mouse & on the bar
        new_x = self.slider.anchor[0] + (self.speed * diff[0])
        if new_x >= (self.anchor[0] - self.slider.w / 2.0) and \
           new_x <= self.anchor[0] + self.w - (self.slider.w / 2.0):
            self.slider.anchor = (new_x, self.slider.anchor[1])

            # Update the associated value
            self.value = (new_x - self.anchor[0]) / self.w
            self.value *= (self.max_val - self.min_val)
            self.on_change(self, controller)

    def on_change(self, controller):
        return # Ignore by default


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
            clicked = e.child_clicked(pos)
            if clicked is not None:
                clicked.on_click(controller, pos, btn)
        
        return True

    def on_drag(self, controller, pos, diff, btns):
        """ Passes drag (world coordinates) from controller to elements of CUI """

        if not self.visible or abs(pos[0]) < self.anchor[0]:
            return False

        for e in self.elements:
            clicked = e.child_clicked(pos)
            if clicked is not None:
                clicked.on_drag(controller, pos, diff, btns)

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

    # Sliders
    # Radius slider
    r_slider_w = c.bg.w * 0.8
    r_slider_h = 0.045
    r_slider_anchor = (calc_anchor_x(c.bg.anchor[0], c.bg.w, r_slider_w), c.bg.anchor[1] - 0.4)
    r_slider = CUI_slider(r_slider_anchor, r_slider_w, r_slider_h, min_val=0.1, max_val=0.5)
    r_slider.on_change = lambda self, c : controls.set_particle_radius(c.sim, self.value)
    c.add_element(r_slider, c.bg)

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
    