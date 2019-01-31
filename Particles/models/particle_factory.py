from Particles.utils import Logger
from Particles.models import types
"""
    Abstract factory for Particles
    Implemented as a module, instead of a class. This omits extra objects for simple spawning
"""

def get_particle_type(name):
    """ Extracts particle type from saved name. Name looks like:
        <class 'Particles.models.types.PType1'>
    """

    if name is None:
        return None

    name = name[7:-2] # Strip all but actual class reference
    parts = name.split('.')
    result = None

    type_dict = {
                    "PType1": types.PType1,
                    "PType2": types.PType2,
                    "PType3": types.PType3,
                    "PType4": types.PType4,
                    "PType5": types.PType5
                }

    # Here comes the *big if*
    try:
        result = type_dict[parts[-1]]  # Last part of 'name' is actual class name
    except KeyError:
        pass

    return result


def create_particle(data):
    """ Accepts data and creates particle according to it. """

     # Get particle type
    type_raw = None
    try:
        type_raw = data["type"]
    except KeyError as ke:
        Logger.log_warning("No particle type data. Can't spawn particle.")
        Logger.log_exception(ke)
        return None

    t = type_raw
    if type(type_raw) is str:
        # Get actual class reference
        t = get_particle_type(type_raw)
    
    if t is None:
        Logger.log_warning("Unrecognized particle type. Can't spawn particle.")
        return None

    # Construct particle
    p = None
    try:
        pos = data["pos"]
        p = t(pos[0], pos[1])
    except KeyError as ke:
        Logger.log_warning("Incomplete particle data. Can't spawn particle.")
        Logger.log_exception(ke)
        return None
    
    # Set particle attributes
    try:
        p.mass = data["mass"]
        p.velocity = data["velocity"]
        p.size = data["size"]
        p._can_move = data["can_move"]
        p.paused = data["paused"]
    except KeyError as ke:
        Logger.log_info("Missing particle data.")
        Logger.log_exception(ke)

    return p


    
    



