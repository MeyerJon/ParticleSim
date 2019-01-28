from Particles.models import particle


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