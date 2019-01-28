from Particles.models import particle
from Particles.utils import Transform
import random, math

"""
    Class that creates some type of particle & pushes it away
"""
class Emitter(particle.Particle):

    def __init__(self, x=0, y=0, size=0.005, sim=None, PType=None, freq=0.5, PSize=0.005):

        super().__init__(x, y, size)

        self._has_emitted = False
        self._particles_emitted = 0

        # Emitter properties
        self.sim = sim
        self.PType = PType
        self.freq = freq
        self.PSize = PSize
        self.range = self.size * 2.1
        self.PLifespan = None
        self.PLimit = None

        # Force parameters
        self.F_push = 0.0005

    
    def emit(self):

        if self.sim is None or self.PType is None:
            return

        angle = math.radians(random.randint(0, 360))
        x = (self.range * math.cos(angle)) + self.pos[0]
        y = (self.range * math.sin(angle)) + self.pos[1]
        p = self.PType(x=x, y=y, size=self.PSize)
        p.lifespan = self.PLifespan
        self.sim.add_entity(p)


    # Simulation

    def tick(self, entities=[]):

        self.lifetime += 1

        # Limit check
        if self.PLimit is None or (self._particles_emitted >= self.PLimit):
            return

        # Timer oscillates 
        em_timer = Transform.get_oscillator(1, period=self.freq)(self.lifetime)

        # Emission
        if not self._has_emitted and (em_timer <= -0.9 or em_timer >= 0.9):
            self.emit()
            self._particles_emitted += 1
            self._has_emitted = True
        elif self._has_emitted and (em_timer >= -0.6 and em_timer <= 0.6):
            self._has_emitted = False

    
    def calculate_reflect_force(self, e):

        if type(e) is self.PType:
            return -self.F_push
        else:
            return 0.0

    
    # Graphics

    def determine_color(self):
        return (200, 200, 240)