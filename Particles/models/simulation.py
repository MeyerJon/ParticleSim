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
            try:
                e.finish_tick()
            except AttributeError:
                pass

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
    sim.paused = True

    # Primordial particles
    """
    for _ in range(1000):
        x = (random.randint(10, 190) - 100) / 100.0
        y = (random.randint(10, 190) - 100) / 100.0
        size = 0.007
        radius = 0.6 #0.155
        velocity = 0.0175 #0.013
        alpha = 180 #math.radians(180)
        beta = 17 #math.radians(17)
        p = particle.PrimordialParticle(x, y, vel=velocity, alpha_d=alpha, beta_d=beta, radius=radius)
        p.size = size
        sim.add_entity(p)
    
    """

    # Particle Automaton
    for _ in range(50):
        x = (random.randint(15, 185) - 100) / 100.0
        y = (random.randint(15, 185) - 100) / 100.0
        radius = 0.05
        phase = 2
        p = particle.AutomatonParticle(x, y, radius=radius, state_phase=phase)
        sim.add_entity(p)

    return sim
