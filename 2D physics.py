import math
import pygame
import random

pygame.display.init()
pygame.font.init()

RADIUS = 10
WHITE = (255, 255, 255)

class Particle:

    def __init__(self, x, y, radius, colour, mass, charge, Tc = 273, Pc = 1) -> None:
        self.x = x # pixels
        self.y = y # pixels
        self.radius = radius * Physics.UNITS_DISTANCE #units
        self.colour = colour 
        self.mass = mass * Physics.UNITS_MASS #units
        self.charge = charge * Physics.UNITS_CHARGE #units
        self.critical_temperature = Tc #kelvin
        self.critical_pressure = Pc #pa

        self.vx = 0 #m/s
        self.vy = 0 #m/s

        Physics.add_particle(self)
        Window.add_particle(self)

    @property
    def area(self):
        return math.pi * math.pow(self.radius, 2)

    @property
    def speed_squared(self):
        return math.pow(self.vy, 2) + math.pow(self.vx, 2)

    def collide_point(self, position):
        x = self.x - position[0]
        y = self.y - position[1]
        distance_2 = (math.pow(x, 2) + math.pow(y, 2)) * math.pow(Physics.UNITS_DISTANCE, 2)
        if math.pow(self.radius, 2) > distance_2:
            return True
        
        return False

    def __repr__(self) -> str:
        return f"Mass: {self.mass}, Charge: {self.charge}"
    
    def __str__(self) -> str:
        return f"Mass: {self.mass}, Charge: {self.charge}"
    
    def draw(self):
        pygame.draw.circle(Window.window, self.colour, (self.x, self.y), (self.radius / Physics.UNITS_DISTANCE), 5)

    def check_collisions(self):
        for particle in Physics.particles:
            if particle == self: continue
            px, py, pr = particle.x, particle.y, particle.radius
            distance_2 = (math.pow(px - self.x, 2) + math.pow(py - self.y, 2)) * math.pow(Physics.UNITS_DISTANCE, 2)
            if math.pow(self.radius + pr, 2) > distance_2:
                Physics.collision(self, particle)
    
    def update(self):
        pixel_radius = self.radius / Physics.UNITS_DISTANCE
        ax, ay = self.calculate_acceleration()
        self.vx += ax * Window.delta_time
        self.vy += ay * Window.delta_time

        self.x += self.vx * Window.delta_time / Physics.UNITS_DISTANCE
        self.y += self.vy * Window.delta_time / Physics.UNITS_DISTANCE

        if self.x < pixel_radius or self.x > Physics.width - pixel_radius:
            self.vx *= -Physics.ENERGY_LOSS
            self.x = pixel_radius if self.x < pixel_radius else Physics.width - pixel_radius

        if self.y < pixel_radius or self.y > Physics.height - pixel_radius:
            self.vy *= -Physics.ENERGY_LOSS
            self.y = pixel_radius if self.y < pixel_radius else Physics.height - pixel_radius

        self.check_collisions()
    
    def calculate_force_gravitation(self):
        total_f_y = 0
        total_f_x = 0
        for particle in Physics.particles:
            if particle == self: continue
            distance_2 = (math.pow(self.x - particle.x, 2) + math.pow(self.y - particle.y, 2)) * math.pow(Physics.UNITS_DISTANCE, 2)
            angle = math.atan2(particle.y - self.y, particle.x - self.x)
            force = Physics.G * particle.mass * self.mass / distance_2 if distance_2 > 0 else 0
            force_y = math.sin(angle) * force
            force_x = math.cos(angle) * force
            total_f_y += force_y
            total_f_x += force_x

        return (total_f_x, total_f_y) 

    def calculate_force_electrostatic(self):
        total_f_y = 0
        total_f_x = 0
        for particle in Physics.particles:
            if particle == self: continue
            distance_2 = (math.pow(self.x - particle.x, 2) + math.pow(self.y - particle.y, 2)) * math.pow(Physics.UNITS_DISTANCE, 2)
            angle = math.atan2(particle.y - self.y, particle.x - self.x)
            force = -Physics.k * particle.charge * self.charge / distance_2 if distance_2 > 0 else 0
            force_y = math.sin(angle) * force
            force_x = math.cos(angle) * force
            total_f_y += force_y
            total_f_x += force_x
        
        return (total_f_x, total_f_y)

    def calculate_acceleration(self):
        fgx, fgy = self.calculate_force_gravitation()
        fex, fey = self.calculate_force_electrostatic()
        fx = fgx + fex
        fy = fgy + fey

        ax = fx / self.mass
        ay = fy / self.mass

        return (ax, ay)
    
class Overlay:

    font = pygame.sysfont.SysFont("Roman", 20)

    @classmethod
    def draw(cls):
        temperature = Physics.calculate_temperature()
        pressure = Physics.calculate_pressure()
        fps_render = cls.font.render(f"FPS: {Window.get_fps()}", False, (255, 0, 0))
        temp_render = cls.font.render(f"Temperature: {round(temperature, 1000)}K", False, (0, 0, 0))
        pressure_render = cls.font.render(f"Pressure: {round(pressure, 1000)}Pa", False, (0, 0, 0))
        distance_render = cls.font.render(f"1 Pixel: {Physics.UNITS_DISTANCE}m", False, (0, 0, 0))

        ui_elements = [fps_render, temp_render, pressure_render, distance_render]
        for i, ui in enumerate(ui_elements):
            Window.window.blit(ui, (0, i*(temp_render.get_size()[1] + 5)))

class Window:

    particles = []
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True
    physics = True

    width, height = window.get_size()
    delta_time = 1

    @classmethod
    def get_fps(cls):
        return round(cls.clock.get_fps())

    @classmethod
    def add_particle(cls, particle):
        cls.particles.append(particle)

    @classmethod
    def mainloop(cls):
        particle_track = None
        while cls.running:

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        cls.running = False

                    if event.key == pygame.K_SPACE:
                        cls.physics = not cls.physics

                if event.type == pygame.MOUSEBUTTONDOWN:
                    collided = False
                    for particle in cls.particles:
                        if particle.collide_point(event.pos): 
                            print(particle)
                            particle_track = particle
                            collided = True
                    
                    if not collided:
                        particle_track = None

            cls.window.fill(WHITE)

            if cls.physics:

                for particle in cls.particles:
                    particle.update()

                Physics.handle_collisions()

            for particle in cls.particles:
                particle.draw()

            Overlay.draw()

            pygame.display.flip()
            cls.clock.tick(0)

class Physics:

    particles = []
    collisions = []

    G = 6.67 * math.pow(10, -11)
    k = 8.99 * math.pow(10, 9)
    R = 8.314
    boltzmann = 1.38 * math.pow(10, -23)
    avagadro = 6.02 * math.pow(10, 23)

    UNITS_MASS = 1 * math.pow(10, -26) #kg
    UNITS_CHARGE = 1.6 * math.pow(10, -19) #C
    UNITS_DISTANCE = math.pow(10, 0) #m
    ENERGY_LOSS = 1

    width, height = Window.width, Window.height

    @classmethod
    def calculate_temperature(cls):
        total_mass = 0
        total_speed_squared = 0
        num_particles = len(cls.particles)
        for particle in cls.particles:
            total_mass += particle.mass
            total_speed_squared += particle.speed_squared

        mean_mass = total_mass / num_particles
        mean_speed_squared = total_speed_squared / num_particles
        return mean_mass * mean_speed_squared / (3 * Physics.k)
    
    @classmethod
    def calculate_pressure(cls):
        total_mass = 0
        total_speed_squared = 0
        num_particles = len(cls.particles)
        area = cls.width * cls.height * math.pow(Physics.UNITS_DISTANCE, 2)
        for particle in cls.particles:
            total_mass += particle.mass
            total_speed_squared += particle.speed_squared

        mean_mass = total_mass / num_particles
        mean_speed_squared = total_speed_squared / num_particles
        return (1/3) * num_particles * mean_mass * mean_speed_squared * (1/area)

    @classmethod
    def collision(cls, p1, p2):
        if not ((p1, p2) in cls.collisions or (p2, p1) in cls.collisions):
            cls.collisions.append((p1, p2))

    @classmethod
    def handle_collisions(cls):
        for p1, p2 in cls.collisions:
            distance = math.dist((p1.x, p1.y), (p2.x, p2.y)) * Physics.UNITS_DISTANCE
            overlap = p1.radius + p2.radius - distance
            angle = math.atan2(p1.y - p2.y, p1.x - p2.x)
            vx1, vy1 = p1.vx, p1.vy
            vx2, vy2 = p2.vx, p2.vy

            #OVERLAP
            p2.y -= overlap * math.sin(angle) / (2*Physics.UNITS_DISTANCE)
            p2.x -= overlap * math.cos(angle) / (2*Physics.UNITS_DISTANCE)
            p1.y -= overlap * math.cos(angle) / (2*Physics.UNITS_DISTANCE)
            p1.x -= overlap * math.sin(angle) / (2*Physics.UNITS_DISTANCE)

            #VELOCITY
            y = (p2.y - p1.y + 0.00000001) / abs(p2.y - p1.y + 0.00000001)
            x = (p2.x - p1.x + 0.00000001) / abs(p2.x - p1.x + 0.00000001)

            p2.vy = y * abs(vy2)
            p2.vx = x * abs(vx2)

            p1.vy = -y * abs(vy1)
            p1.vx = -x * abs(vx1)

        cls.collisions.clear()

    @classmethod
    def add_particle(cls, particle: Particle):
        cls.particles.append(particle)                 

for i in range(100):
    x = random.randint(0, 1500)
    y = random.randint(0, 1500)
    mass = random.randint(1, 100)
    charge = random.randint(1, 100)
    p = Particle(x, y, RADIUS, (mass * 255/100, abs(charge) * 255/100, random.randint(0, 255)), mass, charge)

#ADD TEMP

Window.mainloop()