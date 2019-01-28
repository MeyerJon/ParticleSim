from Particles.utils import Logger, Transform
from Particles.models import particle_factory
from pyglet.window import key, mouse
import pyglet, math


# Control methods
# Particle model methods
def find_closest_entity(pos, entities, r):

    closest = (None, None)
    for e in entities:
        d = Transform.dist(pos, e.pos) - e.size
        if d <= r:
            if closest[1] is None:
                closest = (e, d)
            elif closest[1] > d:
                closest = (e, d)
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

    v_old = particle._velocity
    particle._velocity = ((v_old[0] * mod) + speed_incr[0], (v_old[1] * mod) + speed_incr[1])

def delete_particle(particle):
    
    if particle is None:
        return
    
    particle.mfd = True
    Logger.log_custom("control", "Deleting particle.")

def toggle_particle_movable(particle):

    try:
        particle._can_move = not particle._can_move
    except NameError:
        Logger.log_warning("Can't toggle movability of '{}.'".format(particle))


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

    if symbol == key.UP:
        new_tps = min(old_tps * 2.0, 400)
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
    particle.debug_view = not particle.debug_view

def toggle_trail(particle):
    if particle is None:
        return
    particle.draw_trail_points = not particle.draw_trail_points
    if particle.draw_trail_points:
        # Clear previous trail if turning it back on
        particle.trail_points.clear()

def cycle_trail_density(particle, increase=False):
    if particle is None:
        return

    inc = -1
    if increase:
        inc = 1

    new = particle.trail_points_interval + inc
    if new > 0:
        particle.trail_points_interval = new

def cycle_trail_length(particle, increase=False):

    if particle is None:
        return

    old = particle.trail_points.limit
    inc = -1 * (int(math.log10(old)) + 1)
    if increase:
        inc *= -1 # Make increment positive
    
    try:
        particle.trail_points.set_limit(old + inc)
    except:
        Logger.log_warning("Cannot change trail length.")
