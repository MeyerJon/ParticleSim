from Particles.utils import Logger, Transform
from Particles.models import particle_factory
from Particles.app import CONFIG
from pyglet.window import key, mouse
import pyglet, math


# Control methods
# Particle model methods
def find_closest_entity(pos, entities, r):

    closest = (None, None)
    for e in entities:
        try:
            d = Transform.dist(pos, e.pos) - e.size
            if d <= r:
                if closest[1] is None:
                    closest = (e, d)
                elif closest[1] > d:
                    closest = (e, d)
        except AttributeError:
            # Not a selectable entity
            continue
    return closest[0]

def change_particle_velocity(symbol, particle):
    # Changes a particle's velocity based on the key pressed

    if particle is None:
        return

    speedmod = 0.1
    mod = 1
    if symbol == key.W:
        # Slow down, fella
        mod = (1 - speedmod) 
    elif symbol == key.C:
        # Hurry up, buster
        mod = (1 + speedmod)
    elif symbol == key.X:
        # It's time to stop
        mod = 0
    
    speed_incr = (0, 0)
    step = 0.0001
    if symbol == key.LEFT:
        speed_incr = (-step, 0)
    elif symbol == key.RIGHT:
        speed_incr = (step, 0)
    elif symbol == key.UP:
        speed_incr = (0, step)
    elif symbol == key.DOWN:
        speed_incr = (0, -step)

    try:
        v_old = particle.velocity
        particle.velocity = ((v_old[0] * mod) + speed_incr[0], (v_old[1] * mod) + speed_incr[1])
    except AttributeError:
        Logger.log_warning("Selected entity is not a particle. Can't change velocity.")

def delete_particle(particle):
    
    if particle is None:
        return
    
    particle.mfd = True
    Logger.log_custom("control", "Deleting particle.")

def toggle_particle_movable(particle):

    try:
        particle._can_move = not particle._can_move
    except AttributeError:
        Logger.log_warning("Can't toggle movability of '{}.'".format(particle))


# Primordial Particle attributes
def set_global_particle_radius(sim, r):
    """ Sets all PrimordialParticle's radii. Note: This is rather costly """

    for e in sim.entities:
        try:
            e.radius = r
        except AttributeError:
            Logger.log_warning("Can't set radius of entity: {}".format(e))
    Logger.log_custom("control", "Set global particle radius to {}.".format(r))

def set_global_particle_velocity(sim, v):

    for e in sim.entities:
        try:
            e.velocity = [v, v]
        except AttributeError:
            Logger.log_warning("Can't set velocity of entity {}".format(e))
    Logger.log_custom("control", "Set global particle velocity to {}.".format(v))


# Simulation model methods
def toggle_pause(target):

    target.paused = (not target.paused)
    
    log_msg = str(type(target))
    if target.paused:
        log_msg += " paused."
    else:
        log_msg += " unpaused."
    Logger.log_custom("control", log_msg)

def set_tick_speed(controller, symbol):

    old_tps = controller.ticks_per_secs
    max_tps = 400
    try:
        max_tps = CONFIG["max_TPS"]
    except KeyError:
        pass

    if symbol == key.UP:
        new_tps = min(old_tps * 2.0, max_tps)
    else:
        new_tps = max(1, old_tps / 2.0)

    pyglet.clock.unschedule(controller.tick)
    pyglet.clock.schedule_interval(controller.tick, 1.0/new_tps)
    controller.ticks_per_secs = new_tps
    Logger.log_system("Set TPS to {}.".format(controller.ticks_per_secs))

def spawn_particle(sim, data):
    p = particle_factory.create_particle(data)
    sim.add_entity(p)

# Particle graphics methods
def toggle_debug_view(particle):
    if particle is None:
        return
    try:
        particle.debug_view = not particle.debug_view
    except:
        Logger.log_warning("Can't toggle debug view of selected entity.")

def toggle_trail(particle):
    if particle is None:
        return
    try:
        particle.draw_trail_points = not particle.draw_trail_points
        if particle.draw_trail_points:
            # Clear previous trail if turning it back on
            particle.trail_points.clear()
    except AttributeError:
        Logger.log_warning("Can't draw trail of selected entity.")

def cycle_trail_density(particle, increase=False):
    if particle is None:
        return

    inc = -1
    if increase:
        inc = 1

    try:
        new = particle.trail_points_interval + inc
        if new > 0:
            particle.trail_points_interval = new
    except:
        Logger.log_warning("Can't adjust trail density of selected entity.")

def cycle_trail_length(particle, increase=False):

    if particle is None:
        return

    try:
        old = particle.trail_points.limit
        inc = -1 * (int(math.log10(old)) + 1)
        if increase:
            inc *= -1 # Make increment positive
            particle.trail_points.set_limit(old + inc)
    except AttributeError:
        Logger.log_warning("Cannot change trail length of selected entity.")
