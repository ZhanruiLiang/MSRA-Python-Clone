from vec2d import Vec2d
from pygame.sprite import Sprite
import pygame
import config
import math
from button import Button

Transparent = (0, 0, 0, 0)

def rotate_chop(image, angle):
    # import pdb; pdb.set_trace()
    rect1 = image.get_rect()
    image1 = pygame.transform.rotate(image, angle)
    rect1.center = image1.get_rect().center
    image.fill(Transparent)
    image.blit(image1, (0, 0), rect1)
    return image

class ShipInfo:
    def __init__(self, ship):
        self.ship = ship

    def to_rawstr(self):
        s = self.ship
        attrs = {
                'ID': s.id,
                'Faction': s.faction,
                'Armor': s.armor,
                'PositionX': s.position.x,
                'PositionY': s.position.y,
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
        info = 'ShipInfo %d\n%s' %(len(attrs), 
                '\n'.join('%s %s' % (k, v) for k, v in attrs.iteritems()))
        return info

class Ship(Sprite):
    color = (0, 0, 0x50, 0xff)
    FanColor = (0, 0, 0, 0xff)
    ImgRadius = config.ShipBoundingRadius * 2.4
    Img = None
    def __init__(self, id, faction, pos, **args):
        self.layer = 10
        self.faction = faction
        self.id = id
        self.position = Vec2d(pos)
        self.velocity = Vec2d(0, 0)
        self.direction = Vec2d(1, 0)
        self.armor = config.MaxArmor
        self.hitRadius = config.ShipBoundingRadius
        self._show_debug = 0

        for arg in args:
            setattr(self, arg, args[arg])

        self.cooldowns = [0., 0.]

        self.moving = 0
        self.rotating = 0
        self.blocked = 0
        self.moveTarget = None
        self.attackTarget = None
        # rotateTarget is a float or a tuple (float, float)
        self.rotateTarget = None

        self._lastScale = None
        self._lastAngle = self.direction.angle

        # add button
        self.button = Button(pygame.Rect((0,0), (1,1)), '', 0)
        if Ship.Img is None:
            Ship.Img = pygame.image.load('ship1short.png').convert_alpha()

    def __hash__(self):
        return self.id

    def __repr__(self):
        return 'Ship(id=%s, %s)' % (self.id, self.position)

    def draw_body(self, viewBox):
        r = viewBox.lenWorld2screen(self.ImgRadius)
        imgSize = (r*2, )*2
        self.rect = pygame.Rect((0, 0), imgSize)
        png = self.Img
        self.image = pygame.transform.smoothscale(png , self.rect.size)
        self.image.fill(self.color, None, pygame.BLEND_RGBA_MULT)
        self.rect.center = viewBox.posWorld2screen(self.position)

        # R = viewBox.lenWorld2screen(self.ImgRadius)
        # p0x, p0y = (R, R)
        # downPart = [(-R+2, R/8), (-R/4, R/4), (R/3, R/3), (R - 2, R/6)]
        # upPart = [(x, -y) for x, y in downPart][::-1]
        # poly = [(p0x + x, p0y + y) for x, y in downPart + upPart]
        # R = int(R)
        # r0 = int(config.ShipBoundingRadius)
        # self.image.fill(Transparent)
        # # pygame.draw.circle(self.image, (0x0, 0, 0xff, 0xff), (R, R), int(viewBox.lenWorld2screen(r0)), 
        # #         max(int(viewBox.lenWorld2screen(3)), 1))
        # pygame.draw.circle(self.image, (0x0, 0, 0xff, 0x8f), (R, R), int(viewBox.lenWorld2screen(r0)))
        # pygame.draw.polygon(self.image, self.color, poly)
        # pygame.draw.rect(self.image, self.FanColor, pygame.Rect((R, 0), (viewBox.lenWorld2screen(5), R*2)))

    @property
    def isMoving(self):
        return self.moving

    @property
    def isBlocked(self):
        return self.moving and self.blocked

    @property
    def isRotating(self):
        return self.rotating

    @property
    def cooldownRemain(self):
        return self.cooldowns

    def update(self, viewBox):
        # if scale change then redraw
        redrawwed = 0
        if self._lastScale != viewBox.scale:
            self.draw_body(viewBox)
            self._lastScale = viewBox.scale
            self._lastAngle = 0
            redrawwed = 1
        self.rect.center = viewBox.posWorld2screen(self.position)
        angle = self.direction.angle
        # if rotated then transform
        if abs(self._lastAngle - angle) >= 3.5:
            if not redrawwed:
                self.draw_body(viewBox)
                redrawwed = 1
            self.image = rotate_chop(self.image, -angle)
            self._lastAngle = angle

        # update button
        self.button.rect.center = self.rect.center
        w = max(viewBox.lenWorld2screen(self.hitRadius+5)*2, 10)
        self.button.rect.size = (w, w);

    def test_world_size(self):
        return (self.hitRadius*2,)*2

    def step(self, dt):
        assert dt > 0
        a = config.Acceleration
        v0 = self.velocity + (0, 0)
        if self.moveTarget:
            dp = self.moveTarget - self.position
            if dp.length < config.StopRange:
                self.moveTarget = None
                self.moving = False
        if self.rotateTarget:
            myAngle = self.direction.angle
            if isinstance(self.rotateTarget, float):
                da = self.rotateTarget - myAngle
            else:
                da = Vec2d(self.rotateTarget - self.position).angle - myAngle
            if da > 180: da -= 360
            elif da < -180: da += 360
            if abs(da) <= dt * config.AngularRate:
                self.direction.rotate(da)
                self.velocity.rotate(da)
                self.rotating = False
                self.rotateTarget = None
            elif da:
                da = da/abs(da) * config.AngularRate * dt
                self.direction.rotate(da)
                self.velocity.rotate(da)

        if self.moving :
            vnew = self.velocity + self.direction * a * dt
            if vnew.length < config.MaxSpeed:
                self.velocity = vnew
            else:
                self.velocity = vnew.normalized() * config.MaxSpeed
        elif self.velocity.length != 0:
            dv = -self.velocity.normalized() * config.StopDeccelarate * dt
            if dv.length >= self.velocity.length:
                self.velocity *= 0
            else:
                self.velocity += dv
        # if not self.blocked:
        self.position += (self.velocity + v0) * dt

        for i in (0, 1):
            self.cooldowns[i] = max((self.cooldowns[i] - dt), 0)

    def in_cannon_range(self, cannon, ship):
        # R = config.CannonRange + ship.hitRadius
        R = config.CannonRange - 0.1
        A = config.CannonAngle
        a0 = self.direction.angle
        if cannon == 0:
            p1 = Vec2d(R, 0).rotated(a0 + (180 - A)/2)
        else:
            p1 = Vec2d(R, 0).rotated(a0 - 180  + (180 - A)/2)
        p2 = p1.rotated(A)
        dp = ship.position - self.position
        if dp.length <= R and p1.cross(dp) >= 0 and  p2.cross(dp) <= 0:
            return True
        else:
            return False

