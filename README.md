# Particle Simulator

This is a small project I'm working on for fun. I realise Python is not the optimal language for this kind of thing, but it does allow quick development. The main goal here is to have fun creating something and learning something doing it.


## Installation

If you have `virtualenv 16.*`, you can just use `setup.sh` to install the app.
Otherwise, the dependencies are:
* Python 3.6
* `pyglet`


## Execution
The program can be executed using the `run.sh` script, or using the command
`python3 Particles.py`


## Controls
The program currently has very little in means of GUI. Therefore, all controls are available using the keyboard. Entities can be selected by clicking them, and deselected by either right-clicking or clicking away.
A complete list of controls follows: \
*note: if not otherwise specified, these controls work in SELECT mode*

**Simulation**
* **p** : Pause or unpause the simulation. If an entity is selected, pauses the entity.
* **ctrl+up**: Increase simulation speed (x2)
* **ctrl+down**: Decrease simulation speed (x0.5)
* **h** : Show/Hide the control panel
* **m** : Cycle through modes (SELECT, CREATE, DESTROY)
* **ctrl+s** : Saves the current state of the simulation to a file (JSON)
* **ctrl+l** : Loads a saved state.

**Selected particle**
* **arrow keys** : Change the particle's velocity in the given direction
* **x** : Sets the particle's velocity to 0
* **w** : Decreases the particle's velocity (scales it up)
* **c** : Increases the particle's velocity (scales it down)
* **h** : Toggle force lines
* **t** : Toggle trail
* **space** : Toggle movable
* **backspace** : If in DESTROY mode, deletes particle
