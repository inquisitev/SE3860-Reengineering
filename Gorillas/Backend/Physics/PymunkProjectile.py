# An extension of the projectile class to provide extra data for pymunk

import pymunk

from Backend.Data.Enumerators import ProjectileTravelDirection
from Backend.Data.Gorilla import WIDTH, HEIGHT
from Backend.Data.Projectile import Projectile


class PymunkProjectile(Projectile):
    COLLISION_TYPE = 0
    MASS = 5

    def __init__(self, initial_velocity: float,
                 angle,
                 start_x: float,
                 start_y: float,
                 sender_id: str,
                 sprite: int,
                 direction: ProjectileTravelDirection,
                 key: int = 0,
                 width=WIDTH,
                 height=HEIGHT):
        vs = [(-12, 13), (12, 13), (0, -14)]
        moment = pymunk.moment_for_poly(self.MASS, vs)
        self.body = pymunk.Body(self.MASS, moment)
        self.c_id = self.body._id
        Projectile.__init__(self, initial_velocity,
                            angle,
                            start_x,
                            start_y,
                            sender_id,
                            sprite,
                            direction,
                            key,
                            width,
                            height)

        # https://github.com/viblo/pymunk/blob/master/examples/using_sprites.py
        self.shape = pymunk.Poly(self.body, vs)
        self.shape.filter = pymunk.ShapeFilter(categories=4, mask=pymunk.ShapeFilter.ALL_MASKS() ^ 2)
        self.body.position = (start_x, start_y)
        self.body.angle = self.rotation
        self.body.velocity = initial_velocity
        self.shape.collision_type = self.COLLISION_TYPE

    def get_pos(self):
        return self.body.position.x, self.body.position.y

    def add_to_space(self, space):
        space.add(self.body, self.shape)
