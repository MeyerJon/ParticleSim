from Particles.utils import Transform

class Entity:

    def __init__(self, x=0, y=0):

        self.pos = (x, y)
        self.paused = False
        self.mfd = False

        # Graphics
        self.debug_view = False

    
    def tick(self, dt):
        """ One tick in the simulation. To be overridden in derived classes. """
        raise NotImplementedError

    def mark_for_delete(self):
        """ Returns boolean to indicate if entity should be deleted. """
        return self.mfd

    def draw(self, batch=None):
        """ (Abstract) Returns the vertex list to be drawn, as well as the mode """
        raise NotImplementedError