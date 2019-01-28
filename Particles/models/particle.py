from Particles.models import entity
from Particles.utils import Shapes, Transform, DataStructures, Logger, Profiler
import pyglet, random, math


# Border wrapping functions

def border_stop(pos):
    wrapped_x = pos[0]
    wrapped_y = pos[1]
    border = 0.975
    if pos[0] < -border:
        wrapped_x = -border
    elif pos[0] > border:
        wrapped_x = border
    if pos[1] < -border:
        wrapped_y = -border
    elif pos[1] > border:
        wrapped_y = border
    return (wrapped_x, wrapped_y)

def border_push(pos, vel):
    # Border pushes back on particle (reflection)
    F_border = 0.000 # 0.0001
    border = 1.1
    # Get corners of closest border
    b1 = (0, 0)
    b2 = (0, 0)
    if abs(vel[0]) > abs(vel[1]):
        # Particle is moving towards left or right wall
        if vel[0] > 0:
            b1 = (border, border)
            b2 = (border, -border) 
        else:
            b1 = (-border, border)
            b2 = (-border, -border)
    else:
        # Particle is moving towards upper or lower wall
        b1 = (-border, border)
        b2 = (border, border)
        if vel[1] < 0:
            b1 = (-border, -border)
            b2 = (border, -border)

    def line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return A, B, -C

    def intersection(L1, L2):
        D  = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return x,y
    

    next_pos = (pos[0] + vel[0], pos[1] + vel[1])
    b_point = intersection(line(pos, next_pos), line(b1, b2))
    if b_point is None:
        return vel

    # Vector from wall to particle
    vec = (b_point[0] - pos[0], b_point[1] - pos[1])
    dist_sq = (vec[0] * vec[0]) + (vec[1] * vec[1])

    # Reflect vector along right axis
    if abs(vec[0]) > abs(vec[1]):
        # Swap y axis (left or right wall)
        vec = (vec[0], -vec[1])
    else:
        vec = (-vec[0], vec[1])

    # Calculate force
    F_mag = -(F_border / (dist_sq))
    F = (F_mag * vec[0], F_mag * vec[1])
    
    # Apply force & return
    return (F[0] + vel[0], F[1] + vel[1])


class Particle(entity.Entity):

    def __init__(self, x=0, y=0, size=0.005, mass=0.005):

        super().__init__(x, y)

        self._can_move = True

        # Particle parameters
        self.lifetime = 0
        self.mass = mass
        self.lifespan = None
        self._velocity = [0, 0]
        
        # Force parameters
        self.F_size_mod = 0.01
        self.F_friction = 1
        self.F_min = 5e-6
        self.interacting_types = dict()

        # Graphics
        self.size = size
        self.force_lines = list()
        self.trail_points = DataStructures.LimitedList(150)
        self.trail_points_interval = 2
        self.draw_trail_points = False

    
    # Simulation

    def tick(self, entities = []):

        if self.paused:
            return

        self.lifetime += 1

        # Check if lifetime exceeded
        if self.lifespan is not None and self.lifetime > self.lifespan:
            self.mfd = True
            return

        # Calculate forces from other particles
        self.force_lines = list()
        # Account for friction
        new_vel_total = (self._velocity[0] * self.F_friction, self._velocity[1] * self.F_friction)
        for e in entities:
            if e == self or e.mfd or e.paused:
                continue

            try:
                f = self.calculate_force(e)
            except NameError:
                continue # Not a particle, we don't care

            # If debug view active, save force line
            if self.debug_view:
                self.force_lines.append((e, f))
            
            # Add velocity to total
            if self._can_move:
                new_vel_total = (new_vel_total[0] + f[0], new_vel_total[1] + f[1])
        
        # Set velocity
        self._velocity = border_push(self.pos, new_vel_total)
        
    def finish_tick(self):
        """ Can be called after Particle.tick to finish operations. """
        if self.paused:
            return
        
        # Handling trail drawing
        if self.draw_trail_points:
            if (self.lifetime % self.trail_points_interval) == 0:
                self.trail_points.push(self.pos)
        elif not self.draw_trail_points and self.trail_points.length() > 0:
            self.trail_points.pop()

        if self._can_move:
            new_pos = (self.pos[0] + self._velocity[0], self.pos[1] + self._velocity[1])
            self.pos = border_stop(new_pos)
    
    def calculate_force(self, e):
            """ Calculates the force 'e' applies to this particle. """

            vec = (e.pos[0] - self.pos[0], e.pos[1] - self.pos[1])
            dist_sq = (vec[0] * vec[0]) + (vec[1] * vec[1]) # Calculate it here to omit function call

            # Repelling force at very close range
            min_dist = (e.size + self.size) * 1.9
            min_dist *= min_dist
            if dist_sq <= min_dist:
                F_mod = 50
                F_sizes = (e.mass * e.F_size_mod)
                F_repelling = -(F_sizes * F_mod) * ((min_dist / (dist_sq + 1e-6)))
                return (F_repelling * vec[0], F_repelling * vec[1])

            E_mass = (e.mass * e.F_size_mod)
            F_type_mod = e.calculate_reflect_force(self)
            F = F_type_mod * ((E_mass) / (dist_sq))
            if abs(F) < self.F_min:
                return (0, 0)
            F_x = F * vec[0]
            F_y = F * vec[1]
            result_force = (F_x, F_y)

            return result_force

    def calculate_type_mod(self, e):

        result = 0
        e_type = type(e)

        try:
            result = self.interacting_types[e_type]
        except KeyError:
            # This shouldn't be reachable, but let's be safe
            Logger.log_warning("Trying to calculate mod for unknown type '{}'.".format(e_type))
            
        return result

    def calculate_reflect_force(self, e):
        try:
            return self.interacting_types[type(e)]
        except KeyError:
            # Add reflection mod / 0 for this new type
            F = 0
            t_self = type(self)
            t_e = type(e)
            if t_self in e.interacting_types:
                F = e.interacting_types[t_self]
            self.interacting_types[t_e] = F
            Logger.log_info("Discovered unknown type {} -> {}".format(t_self, t_e))
            return F


    # Graphics

    def draw(self, batch=None):

        indices, verts, colors = Shapes.make_circle(center=self.pos, radius=self.size, color=self.determine_color())

        if batch is None:
            # Just draw the shape immediately
            n = len(verts[1]) // 2
            pyglet.graphics.draw(n, pyglet.gl.GL_POLYGON, verts, colors)
        else:
            # Add indexed vertices to batch
            n = len(verts[1]) // 2
            batch.add_indexed(n, pyglet.gl.GL_TRIANGLES, None, indices, verts, colors)

        if self.debug_view:
            self.draw_force_lines()
        if self.draw_trail_points:
            self.draw_trail()      

    def determine_color(self):
        raise NotImplementedError

    def draw_force_lines(self):
        """ Draws the a line between particles, thickness depending on the magnitude of the force """

        labels = pyglet.graphics.Batch()
        for fl in self.force_lines:
            f = fl[1]
            e = fl[0]
            if f[0] == 0 and f[1] == 0:
                return # If the force is 0, don't draw a line

            t_mod = 7500
            F = math.sqrt((f[0]*f[0]) + (f[1]*f[1]))
            line = Shapes.make_line(self.pos, e.pos, thickness=F*t_mod)
            line.draw(pyglet.gl.GL_LINES)

            # Put label in batch
            x = (max(e.pos[0], self.pos[0]) + min(e.pos[0], self.pos[0])) / 2.0
            y = (max(e.pos[1], self.pos[1]) + min(e.pos[1], self.pos[1])) / 2.0
            label_pos = (x, y)
            force_text = str(f[0]) + " / " + str(f[1])
            label = Shapes.make_label(force_text, label_pos, size=10, batch=labels)
        
        # Draw batch of labels
        labels.draw()

    def draw_trail(self):
        """ Draws the trail of the particle as points in previous positions. """

        n = self.trail_points.length()
        verts, colors = Shapes.make_points(self.trail_points._list)
        pyglet.graphics.draw(n, pyglet.gl.GL_POINTS, verts, colors)
