from Particles.models import particle
import random

"""
    A type that randomly decides its force mods
"""
class RandomType(particle.ForceParticle):
    
    def __init__(self, x=0, y=0, size=0.005):

        super().__init__(x, y, size)

        self.mods = dict()
        self.color_mod = random.randint(40, 100) / 100.0

    
    def setup_mods(self, types):
        
        for t in types:

            m = (100 - random.randint(0, 200)) / 100.0
            self.mods[t] = m

        self.interacting_types = types


    # Simulation

    def calculate_type_mod(self, e):

        result = 0.0
        try:
            result = self.mods[type(e)]
        except KeyError:
            pass
        
        return result

    
    # Graphics

    def determine_color(self):
        c = lambda x: int(self.color_mod * x)
        return (c(200), c(40), c(150))