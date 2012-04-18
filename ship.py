from vec2d import Vec2d
from pygame.sprite import Sprite
import pygame
import config

class ShipInfo:
    def __init__(self, ship):
        self.ship = ship

    def to_rawstr(self):
        s = self.ship
        attrs = {
                'ID': s.id,
                'Faction': s.faction,
                'Armor': s.armor,
                'PositinX': s.position.x,
                'PositinY': s.position.y,
                'VelocityX': s.velocity.x,
                'VelocityY': s.velocity.y,
                'CurrentSpeed': s.velocity.length,
                'DirectionX': s.direction.x,
                'DirectionY': s.direction.y,
                'Rotation': s.direction.angle,
                'IsMoving': s.isMoving,
                'IsBlocked': s.isBlocked,
                'IsRotating': s.isRotating,
                'CooldownRemain': ' '.join(str(i) for i in s.cooldownRemain)
                }
        info = 'ShipInfo{} %d\n%s' %(len(attrs), 
                '\n'.join('%s %s' % (k, v) for k, v in attrs.iteritems()))
        return info

class Ship(Sprite):
    def __init__(self, id, faction):
        self.faction = faction
        self.id = id
        self.position = Vec2d(0, 0)
        self.velocity = Vec2d(0, 0)
        self.direction = Vec2d(1, 0)
        self.armor = config.MaxArmor
        self.hitRadius = config.ShipBoundingRadius

        self.cooldowns = [0., 0.]

        self.moveTarget = None
        self.attackTarget = None

        self.rect = pygame.Rect((0, 0), (2*config.ShipBoundingRadius,)*2)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.rect.center = self.position

    @property
    def isMoving(self):
        pass

    @property
    def isBlocked(self):
        pass

    @property
    def isRotating(self):
        pass

    @property
    def cooldownRemain(self):
        pass

    def update(self, viewBox):
        pass

    def step(self, dt):
        a = config.Acceleration
        if dt > 0:
            self.position += self.velocity * dt
            self.velocity += self.direction * a * dt
        else:
            self.position += self.velocity * dt
            self.velocity += self.direction * a * dt

