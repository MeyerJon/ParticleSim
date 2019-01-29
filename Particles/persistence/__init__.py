"""
    Module that handles data persistence.
    Provides functionality for saving and loading simulation states.
"""
import os, json
from Particles.models import particle, types
from Particles.utils import Logger

DATA_FOLDER = "./data"

# Utilities
def get_file_path(fname, ext):
    return DATA_FOLDER + "/" + fname + "." + ext

def create_data_folder():
    """ Creates the data folder if it doesn't exist. """
    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
        Logger.log_system("Created data directory.")

def get_particle_type(name):
    """ Extracts particle type from saved name. Name looks like:
        <class 'Particles.models.types.PType1'>
    """

    if name is None:
        return None

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
                try:
                    p_data = dict()
                    p_data["type"] = str(type(e))
                    p_data["pos"] = e.pos
                    p_data["velocity"] = e._velocity
                    p_data["mass"] = e.mass
                    p_data["size"] = e.size
                    p_data["can_move"] = e._can_move
                    p_data["paused"] = e.paused
                    data["particles"].append(p_data)
                except AttributeError as e:
                    Logger.log_warning("Corrupt particle. Can't save particle.")
                    Logger.log_exception(e)
                    continue

        # Dump data to json
        json.dump(data, savefile)


def load_from_json(sim, fname="sim"):
    """ Loads a simulation state. """

    fname = get_file_path(fname, "json")

    if not os.path.exists(fname):
        Logger.log_error("File not found: '{}'. Can't load.".format(fname))
        return

    data = dict()
    with open(fname, 'r') as savefile:
        data = json.load(savefile)

    # Clear previous state
    sim.entities.clear()
    
    # Construct sim state
    sim.lifetime = data["lifetime"]
    for e in data["particles"]:

        # Get particle type
        type_raw = None
        try:
            type_raw = e["type"]
        except KeyError as ke:
            Logger.log_warning("No particle type data. This save is corrupt or incompatible.")
            Logger.log_exception(ke)
            continue
        
        t = get_particle_type(type_raw)
        if t is None:
            Logger.log_warning("Unrecognized particle type. Can't load particle.")
            continue

        # Construct particle
        p = None
        try:
            pos = e["pos"]
            mass = e["mass"]
            size = e["size"]
            p = t(pos[0], pos[1], size=size, mass=mass)
        except KeyError as ke:
            Logger.log_warning("Incomplete particle data. Can't load particle.")
            Logger.log_exception(ke)
            continue
        
        # Set particle attributes
        try:
            p._velocity = e["velocity"]
            p._can_move = e["can_move"]
            p.paused = e["paused"]
        except KeyError as ke:
            Logger.log_info("Missing particle data. Perhaps this is an old save?")
            Logger.log_exception(ke)

        sim.add_entity(p)