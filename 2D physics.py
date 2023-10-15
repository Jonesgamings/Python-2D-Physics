import math
import pygame
import random

PARTICLE_RADIUS = 4
PARTICLE_MASS = 1

class Physics:

    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height

        self.particle_grid = {}
        self.particles = []
        self.grid_size = 2 * PARTICLE_RADIUS
        self.gravity = 0.1
        self.movement_steps = 10

        self.energy_loss = 0.95

        self.count = 0

    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(screen, particle.colour, particle.position, particle.radius)
            #x = particle.x + (math.cos(particle.direction) * particle.velocity)
            #y = particle.y + (math.sin(particle.direction) * particle.velocity)

            #pygame.draw.line(screen, (0, 255, 0), particle.position, (x, y))

    def add_particle(self, particle):
        x, y = particle.position
        gridx, gridy = math.floor(x / self.grid_size), math.floor(y / self.grid_size)

        if particle in self.particles: 
            self.particle_grid[particle.grid_pos].remove(particle)

        if particle not in self.particles:
            self.particles.append(particle)

        particle.set_grid(gridx, gridy)
        if (gridx, gridy) in self.particle_grid.keys(): self.particle_grid[(gridx, gridy)].append(particle)
        else: self.particle_grid[(gridx, gridy)] = [particle]

    def distance_to(self, x1, y1, x2, y2):
        dx = math.pow(x1 - x2, 2)
        dy = math.pow(y1 - y2, 2)
        return math.pow(dy + dx, 0.5)

    def resolve_collision(self, p1, p2):
        if p1 == p2: return
        m1, d1 = p1.momentum, p1.direction
        m2, d2 = p2.momentum, p2.direction

        v1 = m2 * self.energy_loss / p1.mass
        v2 = m1 * self.energy_loss / p2.mass

        p1.set_velocity(v1)
        p1.set_direction(d2)

        p2.set_velocity(v2)
        p2.set_direction(d1)

        overlap = (p1.radius + p2.radius) - self.distance_to(p1.x, p1.y, p2.x, p2.y)
        angle = math.atan2(p1.y - p2.y, p1.x - p2.x)
        if overlap > 0:
            p1.add_position(math.cos(angle) * overlap / 2, math.sin(angle) * overlap / 2)
            p2.add_position(-math.cos(angle) * overlap / 2, -math.sin(angle) * overlap / 2)

    def check_boundry(self, particle):
        x, y = particle.position
        vx, vy = particle.velocity_vector
        vel = particle.velocity

        if y <= particle.radius:
            y = particle.radius
            vy *= -1
            vel *= self.energy_loss

        elif y >= self.height - particle.radius:
            y = self.height - particle.radius
            vy *= -1
            vel *= self.energy_loss

        if x <= particle.radius:
            self.x = particle.radius
            vx *= -1
            vel *= self.energy_loss

        elif x >= self.width - particle.radius:
            self.x = self.width - particle.radius
            vx *= -1
            vel *= self.energy_loss

        particle.set_position(x, y)
        particle.set_velocity_vector(vx, vy)
        particle.set_velocity(vel)

    def check_collisions(self, particle):
        gridx, gridy = particle.grid_pos
        if gridx == None: print(particle)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (gridx + i, gridy + j) not in self.particle_grid: continue
                for other_particle in self.particle_grid[(gridx + i, gridy + j)]:
                    if particle.check_collision(other_particle): 
                        return other_particle
                    
        return False

    def step_movement(self, particle, dt):

        vx, vy = particle.velocity_vector
        stepvx, stepvy = vx / self.movement_steps, vy / self.movement_steps

        for _ in range(self.movement_steps):
            particle.add_position(stepvx * dt, stepvy * dt)
            collided = self.check_collisions(particle)
            if collided:
                self.resolve_collision(particle, collided)
                break
        
        self.check_boundry(particle)
        self.add_particle(particle)

    def update_particles(self, dt):
        self.count += 1
        for particle in self.particles:
            particle.add_velocity_vector(0, self.gravity)
            self.step_movement(particle, dt)


class Particle:

    ID = 0

    def __init__(self, x, y, radius = PARTICLE_RADIUS, mass = PARTICLE_MASS, colour = (255, 0, 0), velocity = 0, direction = 0, ID = None) -> None:
        self.ID = Particle.ID + 1 
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.colour = colour

        self.gridx = math.floor(x / (2 * PARTICLE_RADIUS))
        self.gridy = math.floor(y / (2 * PARTICLE_RADIUS))

        self.velocity = velocity
        self.direction = direction

        Particle.ID += 1

    def __str__(self) -> str:
        return str(self.ID)
    
    def __repr__(self) -> str:
        return str(self.ID)

    def add_position(self, dx, dy):
        self.x += dx
        self.y += dy

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_direction(self, direction):
        self.direction = direction

    def set_velocity_vector(self, vx, vy):
        self.direction = math.atan2(vy, vx)
        self.velocity = math.pow(math.pow(vx, 2) + math.pow(vy, 2), 0.5)

    def add_velocity_vector(self, vx_, vy_):
        vx, vy = self.velocity_vector
        self.direction = math.atan2(vy + vy_, vx + vx_)
        self.velocity = math.pow(math.pow(vx + vx_, 2) + math.pow(vy + vy_, 2), 0.5)

    def set_grid(self, gridx, gridy):
        self.gridx = gridx
        self.gridy = gridy

    @property
    def grid_pos(self):
        return (self.gridx, self.gridy)

    @property
    def momentum(self):
        return self.velocity * self.mass

    @property
    def position(self):
        return (self.x, self.y)
    
    @property
    def velocity_vector(self):
        return (math.cos(self.direction) * self.velocity, math.sin(self.direction) * self.velocity)
    
    def check_collision(self, particle):
        px, py = particle.position
        dx = math.pow(px - self.x, 2)
        dy = math.pow(py - self.y, 2)
        if dy + dx <= math.pow(self.radius + particle.radius, 2):
            return True
        
        return False
    
if __name__ == "__main__":
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    width, height = screen.get_size()
    running = True

    physics = Physics(width, height)
    for _ in range(1000):
        p = Particle(random.randint(0, width), random.randint(0, height), direction = random.uniform(0, 2 * math.pi), velocity = random.uniform(0, 10))
        physics.add_particle(p)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break
        
        screen.fill((0, 0, 0))
        physics.draw(screen)

        physics.update_particles(1)
        
        pygame.display.flip()
        clock.tick(60)