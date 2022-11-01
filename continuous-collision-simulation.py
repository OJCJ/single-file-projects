import pygame as pg
from random import randint, uniform
from math import sin, cos

# Configurations
win_width = 600
win_height = 600
box_top = (100, 100)
box_bottom = (win_width - 100, win_height - 100)
particle_radii = 1
particle_count = 10
particle_speed = 8.0
trail_length = 200

#Particle class
class Particle():
	""" This class has no methods and is used for storing the state of a given particle. The class
	could technically be replaces by a list, but accessing the values is a lot more readable 
	with attribute names rather than indexing.
	"""
	def __init__(self, x: int, y: int, radius: int, deg: int, speed: float):
		self.x = x
		self.y = y
		self.radius = radius
		self.vec = [sin(deg), cos(deg)]
		self.speed = speed
		self.trails = []

def collision_handling(p: Particle, collision_line: int, axis: int, oldx: int, oldy: int, negative: bool):
	""" Handles the length and angle of the trail depending on distance and direction to the wall.

	A line is created from the initial position (oldx/oldy), to the point at which it would meet
	the wall (mid_x/mid_y), and then in turn from the wall to the position of the particle in the
	next frame (p.x/p.y).
	"""
	coor = p.x if axis == 0 else p.y

	if negative:
		time_of_collision = ((collision_line - p.radius - (coor + p.vec[axis])) / (p.vec[axis])) / p.speed
	else:
		time_of_collision = ((collision_line + p.radius - (coor + p.vec[axis])) / (p.vec[axis])) / p.speed

	mid_x = p.x + p.vec[0] * p.speed * time_of_collision
	mid_y = p.y + p.vec[1] * p.speed * time_of_collision

	p.trails.append((screen, (255, 0, 0), (oldx, oldy), (mid_x, mid_y)))
	
	p.vec[axis] = -p.vec[axis]

	p.x = mid_x + p.vec[0] * p.speed * (1 - time_of_collision)
	p.y = mid_y + p.vec[1] * p.speed * (1 - time_of_collision)

	p.trails.append((screen, (255, 0, 0), (mid_x, mid_y), (p.x, p.y)))

# Particle data structure: (int, int, int, int, float) representing (x, y, radius, direction degree, speed)
# Creating particles
particles = [
			Particle(
				randint(box_top[0] + particle_radii, box_bottom[0] - particle_radii), #x
				randint(box_top[1] + particle_radii, box_bottom[1] - particle_radii), #y
				particle_radii,
				randint(1, 360),
				particle_speed
			)
		for i in range(particle_count)
	]

# Window and engine configuration
pg.init()
clock = pg.time.Clock()
pg.display.set_caption("Continuous Collision Simulation")
screen = pg.display.set_mode((win_width, win_height))

#Program loop
running = True
while running:
	# Draw background colour and box
	screen.fill((255,255,255))

	pg.draw.line(screen, (0, 0, 0), box_top, (box_top[0], box_bottom[1]))
	pg.draw.line(screen, (0, 0, 0), box_top, (box_bottom[0], box_top[1]))
	pg.draw.line(screen, (0, 0, 0), box_bottom, (box_top[0], box_bottom[1]))
	pg.draw.line(screen, (0, 0, 0), box_bottom, (box_bottom[0], box_top[1]))

	for e in pg.event.get():
		if e.type == pg.QUIT:
			running = False

	for p in particles:
		old_x, old_y = p.x, p.y
		x_clean, y_clean = False, False

		# Collision with left wall
		if p.x + p.vec[0]*p.speed < box_top[0] + particle_radii:
			collision_handling(p, box_top[0], 0, old_x, old_y, False)

		# Collision with right wall
		elif p.x + p.vec[0]*p.speed > box_bottom[0] - particle_radii:
			collision_handling(p, box_bottom[0], 0, old_x, old_y, True)

		else:
			x_clean = True

		# Collision with upper wall
		if p.y + p.vec[1]*p.speed < box_top[1] + particle_radii:
			collision_handling(p, box_top[1], 1, old_x, old_y, False)

		# Collision with lower wall
		elif p.y + p.vec[1]*p.speed > box_bottom[1] - particle_radii:
			collision_handling(p, box_bottom[1], 1, old_x, old_y, True)

		else:
			y_clean = True

		# In case of no collisions
		if x_clean & y_clean:
			p.x += p.vec[0] * p.speed
			p.y += p.vec[1] * p.speed
			p.trails.append((screen, (255, 0, 0), (old_x, old_y),(p.x, p.y)))

		# Adjusting trail to not go past the given length
		if len(p.trails) * p.speed > trail_length:
			p.trails = p.trails[-int(trail_length/p.speed):]

	# Draw particles and trails
	for p in particles:
		pg.draw.circle(screen, (255, 0, 0), (p.x, p.y), p.radius)
		for t in p.trails:
			pg.draw.aaline(*t)
	

	clock.tick(60)
	pg.display.flip()