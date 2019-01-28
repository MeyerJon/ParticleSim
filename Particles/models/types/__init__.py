from Particles.models import particle
from Particles.utils import Transform


class PType1(particle.Particle):

    def __init__(self, x=0, y=0, size=0.008, mass=0.1):

        super().__init__(x, y, size, mass)
        self.interacting_types = {
                                  PType1: -0.8,
                                  PType2: 1.5, 
                                  PType3: -1.5
                                 }
       

    # Graphics

    def determine_color(self):
        return (255, 0, 0)


class PType2(particle.Particle):

    def __init__(self, x=0, y=0, size=0.007, mass=0.085):

        super().__init__(x, y, size, mass)
        self.interacting_types = {
                                  PType1: -1.2,
                                  PType2: 1.5, 
                                  PType3: 1.25
                                 }


    # Graphics

    def determine_color(self):
        return (0, 255, 0)


class PType3(particle.Particle):

    def __init__(self, x=0, y=0, size=0.0055, mass=0.06):

        super().__init__(x, y, size, mass)
        self.interacting_types = {
                                  PType1: -0.75,
                                  PType2: -0.8, 
                                  PType3: 1.2
                                 }


    # Graphics

    def determine_color(self):
        return (0, 0, 255)


class PType4(particle.Particle):

    def __init__(self, x=0, y=0, size=0.0035, mass=0.03):

        super().__init__(x, y, size, mass)
        self.interacting_types = {
                                  PType1: 0.125,
                                  PType2: -0.3, 
                                  PType3: -0.05,
                                  PType4: 0.15
                                 }


    # Graphics

    def determine_color(self):
        return (220, 160, 10)


class PType5(particle.Particle):

    def __init__(self, x=0, y=0, size=0.004, mass=0.005):
        
        super().__init__(x, y, size, mass)
        self.interacting_types = {
                                  PType4: 1, 
                                  PType5: -0.25
                                 }


    # Graphics

    def determine_color(self):
        return (200, 20, 120)
