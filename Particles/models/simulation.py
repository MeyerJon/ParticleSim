from Particles.utils import Logger, Transform, Shapes
from Particles.models import particle, types
import pyglet, random, math

class Simulation:

    def __init__(self):

        # Simulation parameters
        self.entities = list()
        self.lifetime = 0
        self.paused = False

        # Graphics
        self.ui = SimulationUI(self)

    # Simulation operations
    def tick(self, dt=1):

        if self.paused:
            return

        self.lifetime += 1

        # Keep track of entities to delete
        to_delete = set()

        for e_ix in range(len(self.entities)):
            self.entities[e_ix].tick(self.entities)
            if self.entities[e_ix].mfd:
                to_delete.add(e_ix)
        
        # Cleanup
        deleted = 0 # Use this for adjusting indices
        for ix in to_delete:
            self.entities.pop(ix - deleted)
            deleted += 1

        for e in self.entities:
            if issubclass(type(e), particle.ForceParticle) or issubclass(type(e), particle.PrimordialParticle):
                e.finish_tick()

    # Data management
    def add_entity(self, entity):
        """ Adds an entity to the simulation. """
        self.entities.append(entity)
    
    # Graphics
    def draw(self):
        # Draw entities

        B_entities = pyglet.graphics.Batch()        
        [e.draw(batch=B_entities) for e in self.entities]      
            
        B_entities.draw()        
        
        # Draw UI
        self.ui.draw()


class SimulationUI:

    class UILabel:

        def __init__(self, pos, text, size=18):
            self.pos = pos
            self.text = text
            self.size = size

            screenpos = Transform.world_to_screen(self.pos)
            self.label = pyglet.text.Label(self.text, font_name='Arial', font_size=self.size,
                                            x=screenpos[0], y=screenpos[1],
                                            anchor_x='left', anchor_y='center')

        def draw(self):
            self.label.draw()


    def __init__(self, sim):

        self.sim = sim

        # Elements
        self.time_label = SimulationUI.UILabel((-0.925, -0.8), 'Time', size=14)
        self.entity_count = SimulationUI.UILabel((-0.925, -0.875), 'Entities', size=14)
    

    def draw(self):
        
        self.time_label.label.text = "Time: " + str(self.sim.lifetime)
        self.time_label.draw()

        self.entity_count.label.text = "Entities: " + str(len(self.sim.entities))
        self.entity_count.draw()
    


def setup():

    sim = Simulation()

    # Create particles
    active_types = [types.PType1, types.PType2, types.PType3, types.PType4]

    p1 = types.PType1(0, 0, 0.085, mass=1)
    p1._can_move = False

    #sim.add_entity(p1)
    sim.paused = True

    """
    # Orbitters for p1
    for i in range(0):
        c = p1.pos
        r = random.randint(8, 10) / 100.0
        ad = random.randint(0, 360)
        ar = math.radians(ad)
        x = r * math.cos(ar) + c[0]
        y = r * math.sin(ar) + c[1]
        s = 0.004
        p = types.PType5(x, y, size=s, mass=0.0000075)
        s_ratio = (p.mass) / (p1.mass)
        vx = -s_ratio * math.cos(math.radians(ad + 90)) * 1.2
        vy = -s_ratio * math.sin(math.radians(ad + 90)) * 1.2
        p._velocity = [vx, vy]
        sim.add_entity(p)
    """

    # Primordial particles

    for _ in range(50):
        x = (random.randint(15, 185) - 100) / 100.0
        y = (random.randint(15, 185) - 100) / 100.0
        size = 0.012
        radius = 0.25 #0.155
        velocity = 0.0175 #0.013
        alpha = 180 #math.radians(180)
        beta = 17 #math.radians(17)
        p = particle.PrimordialParticle(x, y, vel=velocity, alpha_d=alpha, beta_d=beta, radius=radius)
        p.size = size
        sim.add_entity(p)
    
    """
    p1 = particle.PrimordialParticle(0, 0)
    p1.radius = 0.25
    p1.alpha = math.radians(180)
    p1.beta = math.radians(17)

    p2 = particle.PrimordialParticle(0.25, 0)
    p2.radius = 0.25
    p2.alpha = math.radians(180)
    p2.beta = math.radians(17)

    p3 = particle.PrimordialParticle(0.5, 0)
    p3.radius = 0.25
    p3.alpha = 0
    p3.beta = 0

    p4 = particle.PrimordialParticle(0.75, 0)
    p4.radius = 0.25

    sim.add_entity(p1)
    sim.add_entity(p2)
    sim.add_entity(p3)
    sim.add_entity(p4)
    """

    return sim
