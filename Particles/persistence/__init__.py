"""
    Module that handles data persistence.
    Provides functionality for saving and loading simulation states.
"""
import json
from Particles.models import particle, types

DATA_FOLDER = "./data"

# Utilities
def get_file_path(fname, ext):
    return DATA_FOLDER + "/" + fname + "." + ext

def get_particle_type(name):
    """ Extracts particle type from saved name. Name looks like:
        <class 'Particles.models.types.PType1'>
    """

    name = name[7:-2] #Strip all but actual class reference
    parts = name.split('.')
    result = None

    # Here comes the *big if*
    if parts[-2] == "types":
        # It's one of the 'standard' types
        t = parts[-1]
        if t == "PType1":
            result = types.PType1
        elif t == "PType2":
            result = types.PType2
        elif t == "PType3":
            result = types.PType3
        elif t == "PType4":
            result = types.PType4
        elif t == "PType5":
            result = types.PType5

    return result



def save_to_json(sim, fname="sim"):
    """ Saves a simulation's state as a .json file. """

    fname = get_file_path(fname, "json")

    with open(fname, 'w') as savefile:

        # Collect all data to be saved
        data = {
                "lifetime": sim.lifetime,
                "particles": list()
               }

        # Go over each entity and save its properties
        for e in sim.entities:

            if issubclass(type(e), particle.Particle):
                p_data = dict()
                p_data["type"] = str(type(e))
                p_data["pos"] = e.pos
                p_data["velocity"] = e._velocity
                p_data["mass"] = e.mass
                p_data["size"] = e.size
                data["particles"].append(p_data)

        # Dump data to json
        json.dump(data, savefile)


def load_from_json(sim, fname="sim"):
    """ Loads a simulation state. """

    fname = get_file_path(fname, "json")

    data = dict()
    with open(fname, 'r') as savefile:
        data = json.load(savefile)

    # Clear previous state
    sim.entities.clear()
    
    # Construct sim state
    sim.lifetime = data["lifetime"]
    for e in data["particles"]:
        t = get_particle_type(e["type"])
        pos = e["pos"]
        mass = e["mass"]
        size = e["size"]
        p = t(pos[0], pos[1], size=size, mass=mass)
        p._velocity = e["velocity"]
        sim.add_entity(p)