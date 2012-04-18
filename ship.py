from vec2d import Vec2d
from pygame.sprite import Sprite
import pygame
import config

Transparent = (0, 0, 0, 0)

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
    color = (0, 0, 0x50, 0xff)
    FanColor = (0, 0, 0, 0xff)
    def __init__(self, id, faction, pos, **args):
        self.faction = faction
        self.id = id
        self.position = Vec2d(pos)
        self.velocity = Vec2d(0, 0)
        self.direction = Vec2d(1, 0)
        self.armor = config.MaxArmor
        self.hitRadius = config.ShipBoundingRadius
        self.moving = 0
        self.blocked = 0

        for arg in args:
            setattr(self, arg, args[arg])

        self.cooldowns = [0., 0.]

        self.moveTarget = None
        self.attackTarget = None

        self.rect = pygame.Rect((0, 0), (2*config.ShipBoundingRadius,)*2)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.rect.center = self.position

        self._lastScale = None
        self._lastAngle = self.direction.angle

    def __repr__(self):
        return 'Ship(id=%s, %s)' % (self.id, self.position)

    def draw_body(self, viewBox):
        R = viewBox.lenWorld2screen(self.hitRadius)
        p0x, p0y = (R, R)
        downPart = [(-R+2, R/8), (-R/4, R/4), (R/3, R/3), (R - 2, R/6)]
        upPart = [(x, -y) for x, y in downPart][::-1]
        poly = [(p0x + x, p0y + y) for x, y in downPart + upPart]
        pygame.draw.polygon(self.image, self.color, poly)
        pygame.draw.rect(self.image, self.FanColor, pygame.Rect((R, 0), (viewBox.lenWorld2screen(5), R*2)))
        pygame.draw.circle(self.image, (0xff, 0, 0, 0xff), (int(R), int(R)), int(R), 1)

    @property
    def isMoving(self):
        return self.moving

    @property
    def isBlocked(self):
        return self.moving and self.blocked

    @property
    def isRotating(self):
        return False

    @property
    def cooldownRemain(self):
        return self.cooldowns

    def update(self, viewBox):
        if self._lastScale != viewBox.scale:
            r = viewBox.lenWorld2screen(self.hitRadius)
            self.rect = pygame.Rect((0, 0), (r*2,)*2)
            self.image = pygame.Surface(self.rect.size).convert_alpha()
            self.image.fill(Transparent)
            self.draw_body(viewBox)
            self._lastScale = viewBox.scale
            self._lastAngle = 0
        self.rect.center = viewBox.posWorld2screen(self.position)
        angle = self.direction.angle
        if self._lastAngle != angle:
            self.image = pygame.transform.rotate(self.image, angle - self._lastAngle)
            self._lastAngle = angle

    def test_world_size(self):
        return (self.hitRadius*2,)*2

    def step(self, dt):
        a = config.Acceleration
        if dt > 0:
            self.position += self.velocity * dt
            if self.moving and not self.blocked and self.velocity.length < config.MaxSpeed:
                self.velocity += self.direction * a * dt
        else:
            self.position += self.velocity * dt
            if self.moving and not self.blocked and self.velocity.length < config.MaxSpeed:
                self.velocity += self.direction * a * dt

