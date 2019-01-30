from Particles.models import entity, particle
from Particles.utils import Shapes, Transform
from pyglet import graphics, gl


"""
    Particle that applies force to others, but isn't acted upon
"""
class Generator(particle.Particle):

    def __init__(self, x=0, y=0, size=0, force=0):

        super().__init__(x, y, size)

        self.F_generated = force
        self.fluct_func = None


    # Simulation

    def tick(self, entities=[]):
        # All this guy does is get older & fluctuate its output
        self.lifetime += 1

        if self.fluct_func is not None:
            self.F_generated = self.fluct_func(self.lifetime)

    def calculate_force(self, e):
        # A generator isn't acted upon
        return (0, 0)

    def calculate_reflect_force(self, e):
        return self.F_generated

    def set_fluct_func(self, f):
        self.fluct_func = f


    # Graphics

    def determine_color(self):
        c = lambda x: int(abs(self.F_generated) * x)
        return (c(200), c(200), c(200))


"""
    Generates a homogeneous, uni-directional field that moves particles around.
    Field has a spherical shape with a specified range.
"""
class FieldGenerator(entity.Entity):

    def __init__(self, x, y, force, range=0.5):

        super().__init__(x, y)

        self.F = force
        self.range = range

        self.size = 0.02
        self.debug_view = False

    
    # Simulation
    def tick(self, entities):

        if self.paused or self.mfd:
            return

        for e in entities:

            try:
                # Add force to particle velocity
                if Transform.dist(self.pos, e.pos) <= self.range:
                    e._velocity = (e._velocity[0] + self.F[0], e._velocity[1] + self.F[1])
            except AttributeError:
                # Not a particle, ignore
                continue

    
    # Graphics
    def draw(self, batch=None):
        # Fields are invisible, but debug is possible

        if self.debug_view:
            n_points = 40
            anchor = (self.pos[0] - (self.range / 2.0), self.pos[1] + (self.range / 2.0))
            indices, verts, colors = Shapes.make_circle(n_points=n_points, center=self.pos, radius=(self.range / 2.0))

            if batch is None:
                # Draw directly
                graphics.draw(n_points+2, gl.GL_LINE_LOOP, verts, colors)
            else:
                batch.add_indexed(n_points+2, gl.GL_LINE_LOOP, None, indices, verts, colors)

        return
