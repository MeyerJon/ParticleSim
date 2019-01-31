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


"""
    Base class for particles. Controller should be based on this interface
"""
class Particle(entity.Entity):

    def __init__(self, x, y, size=0):

        super().__init__(x, y)
        
        # Particle parameters
        self.velocity = (0, 0)

        # Graphics
        self.size = size
        self.debug_view = False

        # Other
        self._can_move = True


"""
    Base class for all particles that interact using some (physics-based) force system.
"""
class ForceParticle(Particle):

    def __init__(self, x=0, y=0, size=0.005, mass=0.005):

        super().__init__(x, y, size)

        # Particle parameters
        self.lifetime = 0
        self.mass = mass
        self.lifespan = None
        
        # Force parameters
        self.F_size_mod = 0.01
        self.F_friction = 1
        self.F_min = 5e-6
        self.interacting_types = dict()

        # Graphics
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
        new_vel_total = (self.velocity[0] * self.F_friction, self.velocity[1] * self.F_friction)
        for e in entities:
            if e == self or e.mfd or e.paused:
                continue

            try:
                f = self.calculate_force(e)
            except AttributeError:
                continue # Not a particle, we don't care

            # If debug view active, save force line
            if self.debug_view:
                self.force_lines.append((e, f))
            
            # Add velocity to total
            if self._can_move:
                new_vel_total = (new_vel_total[0] + f[0], new_vel_total[1] + f[1])
        
        # Set velocity
        self.velocity = border_push(self.pos, new_vel_total)
        
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
            new_pos = (self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1])
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


"""
    Particle for emulating primordial particle system
"""
class PrimordialParticle(Particle):

    def __init__(self, x, y, vel=0.005, alpha_d=10, beta_d=7, radius=0.1):

        super().__init__(x, y, size=0.01)

        # Particle attributes
        self.velocity = (vel, vel)
        self.orientation = math.pi / 2.0
        self.alpha = math.radians(alpha_d)
        self.beta = math.radians(beta_d)
        self.radius = radius

        self._neighbourhood_size = 0


    # Simulation
    def tick(self, entities):

        if self.paused or self.mfd:
            return
        
        # Calculate neighbourhood (sign & amount of neighbours)
        N_left = 0
        N_right = 0
        N_total = 0
        for e in entities:

            if e == self or e.paused:
                continue

            vec = (e.pos[0] - self.pos[0], e.pos[1] - self.pos[1])
            dist_sq = (vec[0] * vec[0]) + (vec[1] * vec[1])

            if dist_sq <= (self.radius * self.radius):

                # Calculate angle between vectors
                d_x = math.cos(self.orientation) * self.velocity[0]
                d_y = math.sin(self.orientation) * self.velocity[1]
                own_vec = (self.pos[0] + d_x, self.pos[1] + d_y)
                own_vec = (own_vec[0] - self.pos[0], own_vec[1] - self.pos[1])
                angle = self.calculate_vector_angle(own_vec, vec)

                # Check if left or right
                if 0 < angle and angle < (math.pi / 2.0):
                    N_left += 1
                else:
                    N_right += 1
                N_total += 1 # Count separately because orthogonal matrices still count
        
        sign = 1
        if N_left > N_right:
            sign = -1
        elif N_left == N_right:
            sign = 0
        
        # Calculate change in orientation
        self.orientation += self.alpha + (sign * self.beta * N_total)

        self._neighbourhood_size = N_total

    def finish_tick(self):

        if self.paused or self.mfd or not self._can_move:
            return

        # Update position
        d_x = math.cos(self.orientation) * self.velocity[0]
        d_y = math.sin(self.orientation) * self.velocity[1]
        self.pos = border_stop((self.pos[0] + d_x, self.pos[1] + d_y))

    def calculate_vector_angle(self, v1, v2):
        """ Calculates angle between two vectors. """
        vec_len = lambda v : math.sqrt((v[0] * v[0]) + (v[1] * v[1]))
        l_v1 = vec_len(v1)
        l_v2 = vec_len(v2)
        len_prod = l_v1 * l_v2
        dot_prod = (v1[0] * v2[0]) + (v1[1] * v2[1])
        angle = 0.0
        
        try:
            cos = dot_prod / len_prod
            angle = math.acos(cos)
        except (ValueError, ZeroDivisionError):
            pass # Ignore orthogonal vectors
        return angle


    # Graphics
    def draw(self, batch=None):

        color = self.colors_density()
        indices, verts, colors = Shapes.make_circle(n_points=20, center=self.pos, radius=self.size, color=color)

        if batch is None:
            # Draw directly
            n = len(verts[1]) // 2
            pyglet.graphics.draw(n, pyglet.gl.GL_POLYGON, verts, colors)
        else:
            # Add indexed vertices to batch
            n = len(verts[1]) // 2
            batch.add_indexed(n, pyglet.gl.GL_TRIANGLES, None, indices, verts, colors)

        # Debug view
        if self.debug_view:
            self.draw_debug_view()

    def colors_heatmap(self):
        color = (
                    45 * self._neighbourhood_size,
                    2 * self._neighbourhood_size * self._neighbourhood_size,
                    int(110 / (self._neighbourhood_size + 1))
                )
        color = (min(color[0], 255), min(color[1], 255), min(color[2], 255))
        return color

    def colors_modulo(self):
        color = (
                    50 * (12 % (self._neighbourhood_size + 1)),
                    50 * (8 % (self._neighbourhood_size + 1)),
                    50  * (10 % (self._neighbourhood_size + 1))
                )
        color = (min(color[0], 255), min(color[1], 255), min(color[2], 255))
        return color

    def colors_simple(self):
        color = (
                    20,
                    10 * ((self._neighbourhood_size)**2),
                    int(150  / (self._neighbourhood_size + 1))
                )
        color = (min(color[0], 255), min(color[1], 255), min(color[2], 255))
        return color

    def colors_density(self):
        # Colors have fixed values based on region density

        color = (255, 255, 255)
        if self._neighbourhood_size > 9:
            color = (240, 230, 10)
        elif self._neighbourhood_size >= 7:
            color = (20, 250, 100)
        elif self._neighbourhood_size >= 5:
            color = (10, 140, 180)
        elif self._neighbourhood_size > 3:
            color = (20, 25, 120)
        else:
            color = (10, 10, 190)
        return color

    def draw_debug_view(self):
        # Draw circle indicating range
        indices, verts, colors = Shapes.make_circle(center=self.pos, radius=self.radius / 2.0)
        # Overwrite degenerate first point
        verts[1][0:1] = verts[1][-2:-1]
        n_points = len(verts[1]) // 2
        pyglet.gl.glLineWidth(1)
        pyglet.graphics.draw(n_points, pyglet.gl.GL_LINE_LOOP, verts, colors)

        # Draw label showing # neighbours
        label_pos = (self.pos[0], self.pos[1] + 3*self.size + 0.015)
        n_label = Shapes.make_label(str(self._neighbourhood_size), label_pos, size=14)
        n_label.draw()
