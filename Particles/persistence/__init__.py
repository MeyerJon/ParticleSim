"""
    Module that handles data persistence.
    Provides functionality for saving and loading simulation states.
"""
import os, json
from Particles.app import CONFIG
from Particles.models import particle, types, particle_factory
from Particles.utils import Logger

# Utilities
def get_file_path(fname, ext):
    dir = "./data" # default
    try:
        dir = CONFIG["data_folder"]
    except KeyError:
        pass
    return dir + "/" + fname + "." + ext

def create_data_folder():
    """ Creates the data folder if it doesn't exist. """
    path = "./data" # default folder
    try:
        path = CONFIG["data_folder"]
    except KeyError:
        pass

    if not os.path.exists(path):
        os.mkdir(path)
        Logger.log_system("Created data directory.")

def set_data_folder(path):
    CONFIG["data_folder"] = path


# Saving and loading
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

            if issubclass(type(e), particle.ForceParticle):
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

        p = particle_factory.create_particle(e)
        if p is not None:
            sim.add_entity(p)
        else:
            Logger.log_warning("Loading particle failed.")
