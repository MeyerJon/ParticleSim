from Particles.utils import Logger
"""
    Abstract factory for Particles
    Implemented as a module, instead of a class. This omits extra objects for simple spawning
"""


def create_particle(data):
    """ Accepts data and creates particle according to it. """

    ptype, pos = None, None
    try:
        ptype = data["type"]
        pos = data["pos"]
    except KeyError:
        Logger.log_warning("Incomplete particle data; cannot spawn.")
        return None
    
    p = ptype(pos[0], pos[1])

    return p

    
    



