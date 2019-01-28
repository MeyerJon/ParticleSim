from Particles import app
from Particles.models import simulation
from Particles.controllers import sim_control
from Particles.utils import Logger, Profiler
import pyglet, time, cProfile


def run_app():

    # Setup model & controller
    sim = simulation.setup()
    keyboard = pyglet.window.key.KeyStateHandler()
    controller = sim_control.SimController(sim, keyboard)

    # Add handlers
    app.win.push_handlers(controller)
    app.win.push_handlers(keyboard)

    # Profiling
    Profiler.make_profiler_category("draw_times")
    Profiler.make_profiler_category("tick_times")
    fps_counter = pyglet.window.FPSDisplay(app.win)

    # Schedule initial simulation speed
    ticks_per_sec = 25.0
    pyglet.clock.schedule_interval(controller.tick, 1 / ticks_per_sec)
    pyglet.clock.set_fps_limit(60)

    # Draw event
    @app.win.event
    def on_draw():
        starttime = time.time()
        app.win.clear()
        sim.draw()
        controller.draw()
        Profiler.add_profiler_data("draw_times", time.time() - starttime)
        fps_counter.draw()
    
    # Main app loop
    pyglet.app.run()


    # Collect & log some stats
    post_run_stats(controller, sim)

    return


def post_run_stats(controller, sim):

    Logger.log("<----------------->")
    Logger.log("> Execution stats")

    Logger.log(">> Simulation lifespan: {} ticks".format(sim.lifetime))

    avg_draw = Profiler.get_numeric_category_avg("draw_times")
    if avg_draw is not None:
        Logger.log(">> Avg. drawing time: {} ms".format(avg_draw * 1000))
    avg_tick = Profiler.get_numeric_category_avg("tick_times")
    if avg_tick is not None:
        Logger.log(">> Avg. tick time: {} ms".format(avg_tick * 1000))

    Logger.log("<----------------->")
