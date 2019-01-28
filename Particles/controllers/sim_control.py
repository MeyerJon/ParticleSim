import pyglet, time
from pyglet.window import key, mouse
from enum import Enum
from Particles.models import simulation
from Particles.controllers import controller_ui, controls
from Particles.utils import Transform, Shapes, Logger, Profiler


class ModeEnum(Enum):

    SELECT = 0
    CREATE = 1
    DESTROY = 2


class SimController:

    def __init__(self, sim, keyboard=None):
        self.sim = sim
        self.keyboard = keyboard

        # Controller parameters
        self.mode = ModeEnum.SELECT
        self.ticks_per_secs = 50.0
        self.creatable_types = get_creatable_types()
        self.cur_creation_index = 0

        self._cur_selected = None
        self._ui = controller_ui.ControllerUI()

        # Graphics
        self._selection_ring = Shapes.make_circle(as_vertexlist=True)


    # Handle events
    def on_mouse_press(self, x, y, btn, modifiers):
        # Handle mouse click
        
        if self.mode == ModeEnum.SELECT:

            if btn == mouse.LEFT:
                # Select entity under mouse
                pos = Transform.screen_to_world((x, y))

                # First check if the click should be handled by the UI
                if self._ui.on_click(self, pos, btn):
                    return

                r = 0.1
                self._cur_selected = controls.find_closest_entity(pos, self.sim.entities, r)                    
            elif btn == mouse.RIGHT:
                # Deselect current entity
                self._cur_selected = None

        if self.mode == ModeEnum.CREATE:

            if btn == mouse.LEFT:
                # Create particle under mouse
                pos = Transform.screen_to_world((x, y))
                data = {"type": self.creatable_types[self.cur_creation_index],
                        "pos": pos
                       }
                controls.spawn_particle(self.sim, data)

    
    def on_key_press(self, symbol, modifiers):
        # Handle key press
        
        # Mode switch
        if symbol in [key.M]:
            self.mode = ModeEnum((self.mode.value + 1) % len(list(ModeEnum)))
            Logger.log_custom("control", "Changed mode to {}.".format(self.mode))

        if self.mode == ModeEnum.SELECT:
            
            if symbol == key.P:
                if self._cur_selected is None:
                    controls.toggle_pause(self.sim)
                else:
                    controls.toggle_pause(self._cur_selected)

            if symbol in [key.UP, key.DOWN] and modifiers == 18: # 16 (base) + 2 (ctrl)
                controls.set_tick_speed(self, symbol)

            if symbol == key.H:
                if self._cur_selected is None:
                    self._ui.visible = not self._ui.visible
                else:
                    controls.toggle_debug_view(self._cur_selected)

            if symbol == key.T:
                if self._cur_selected is not None:
                    controls.toggle_trail(self._cur_selected)

            if symbol == key.SPACE:
                if self._cur_selected is not None:
                    controls.toggle_particle_movable(self._cur_selected)

        if self.mode == ModeEnum.DESTROY:

            if symbol == key.BACKSPACE:
                controls.delete_particle(self._cur_selected)
                self._cur_selected = None

    # Simulation control

    def tick(self, dt=1):

        starttime = time.time()

        # Handle relevant keys being held
        if self.mode == ModeEnum.SELECT:
            # Particle movement
            for s in [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.W, key.C, key.X]:
                if self.keyboard[s]:
                    controls.change_particle_velocity(s, self._cur_selected)


        self.sim.tick()

        Profiler.add_profiler_data("tick_times", time.time() - starttime)


    # Graphics

    def draw(self):

        # Draw selection circle around selected entity
        if self._cur_selected is not None:
            r = (self._cur_selected.size * 1.2) + 0.005
            indices, verts, colors = Shapes.make_circle(center=self._cur_selected.pos, radius=r)
            # Overwrite degenerate first point
            verts = verts[1]
            verts[0:1] = verts[-2:-1]
            self._selection_ring.vertices = verts
            self._selection_ring.colors = colors[1]
            pyglet.gl.glLineWidth(1)
            self._selection_ring.draw(pyglet.gl.GL_LINE_LOOP)

        # Draw UI
        self._ui.draw()


# Helper methods
def get_creatable_types():

    from Particles.models import types

    l = [types.PType1, types.PType2, types.PType3]

    return l