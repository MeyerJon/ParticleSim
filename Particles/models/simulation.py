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
            if issubclass(type(e), particle.Particle):
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

    p2 = types.PType4(0.85, 0, 0.015, mass=0.0025)
    p2.draw_trail_points = True
    p2.trail_points_interval = 1
    p2.trail_points.set_limit(160)
    p2._velocity = [0, 0.035 + 0.00049]

    sim.add_entity(p1)
    sim.add_entity(p2)
    sim.paused = True

    for i in range(0):
        t = random.choice(active_types)
        #t = types.PType1
        s = (random.randint(130, 130) / 10000.0)
        x = (random.randint(40, 160) - 100) / 100.0
        y = (random.randint(40, 160) - 100) / 100.0
        p = t(x=x, y=y, size=s)
        sim.add_entity(p)

    for i in range(0):
        c = p2.pos
        r = random.randint(8, 10) / 100.0
        ad = random.randint(0, 360)
        ar = math.radians(ad)
        x = r * math.cos(ar) + c[0]
        y = r * math.sin(ar) + c[1]
        s = 0.004
        p = types.PType5(x, y, size=s, mass=0.0000075)
        s_ratio = (p.mass) / (p2.mass)
        vx = -s_ratio * math.cos(math.radians(ad + 90)) * 1.2
        vy = -s_ratio * math.sin(math.radians(ad + 90)) * 1.2
        p._velocity = [vx, vy]
        sim.add_entity(p)

    from Particles.models.types import generator
    # Create generators
    g1 = generator.Generator(x=0.3, y=-0.3, size=0.01, force=-2)
    g1.set_fluct_func(Transform.get_oscillator(3, 0.5))    
    #sim.add_entity(g1)

    f1 = generator.FieldGenerator(0, -1, force=(0, -0.00025), range=0.5)
    sim.add_entity(f1)

    f2 = generator.FieldGenerator(0, 1, force=(0, 0.00025), range=0.5)
    sim.add_entity(f2)

    # Create emitters
    from Particles.models.types import emitter
    e1 = emitter.Emitter(x=0, y=0, size=0.01, sim=sim, PType=types.PType1, freq=0.5)
    e1.PLimit = 100
    e1.F_push = -5
    e1.PSize = 0.01
    e1.range = 0.05
    #sim.add_entity(e1)

    return sim
