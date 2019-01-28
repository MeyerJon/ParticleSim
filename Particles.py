import Particles
from Particles.utils import Logger

import datetime, cProfile

# Time app
start_time = datetime.datetime.now()

# Initialize logfile
Logger.clear_logfile()
Logger.log("Started at " + str(start_time))

# Start the simulation
Particles.run_app()
#cProfile.run("Particles.run_app()")

# Finish up logfile
end_time = datetime.datetime.now()
Logger.log("Quit at " + str(end_time))
Logger.log("Ran for {}".format(str(end_time - start_time)))
