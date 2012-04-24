import config
import pygame
from vec2d import Vec2d
Sprite = pygame.sprite.Sprite

Transparent = (0, 0, 0, 0)

class WaterImages:
    images = {}
    SeaColor = (0xaa, 0xaf, 0xe0, 0x8f)
    @staticmethod
    def surface(size, i):
        if (size, i) in WaterImages.images:
            return WaterImages.images[size, i]
        R0 = size / 2
        R = R0 * (1 - i / 5) + 1
        img = pygame.Surface((R * 2, R * 2)).convert_alpha()
        img.fill(Transparent)
        color = WaterImages.SeaColor[:3] + (0x80 * (1 - i/5),)
        pygame.draw.circle(img, color, (R, R), R)
        WaterImages.images[size, i] = img
        return img

class Background(Sprite):
    def __init__(self, textureFile):
        texture = pygame.image.load(textureFile).convert_alpha()
        size = texture.get_size()
        ssize = config.W, config.H
        ssize = ssize[0] + size[0], ssize[1] + size[1]
        image = pygame.Surface(ssize).convert_alpha()
        for x in xrange(0, ssize[0]+1, size[0]):
            for y in xrange(0, ssize[1]+1, size[1]):
                image.blit(texture, (x, y))
        self.image = image
        self.ssize = ssize
        self.tsize = size
        self.rect = pygame.Rect((0, 0), ssize)
        self._pos = (0, 0)

    def update(self, viewBox):
        x, y = viewBox.posWorld2screen(self._pos)
        w0, h0 = self.tsize
        x = x % w0 - w0
        y = y % h0 - h0
        self.rect.topleft = x, y

class VisualEffect(Sprite):
    def __init__(self):
        # Sprite.__init__(self)
        self._kill = 0
        self.rect = pygame.Rect((0, 0), (-1, -1))
        self.layer = 0

    def kill(self):
        self._kill = 1

    def test_world_size(self):
        pass

class WaterEffect(VisualEffect):
    def __init__(self, position, speed):
        VisualEffect.__init__(self)
        self.layer = 8
        self.size = 20 * speed / config.MaxSpeed
        self.position = +position
        self.i = 0
        self.maxT = 0.8
        self.t = 0

    def step(self, dt):
        self.t += dt
        self.i = int(self.t / self.maxT) * 5
        if self.t >= self.maxT:
            self.kill()

    def update(self, viewBox):
        size = int(viewBox.lenWorld2screen(self.size))
        self.rect = pygame.Rect((0, 0), (size, size))
        self.rect.center = viewBox.posWorld2screen(self.position)
        self.image = WaterImages.surface(size, self.i)

    def test_world_size(self):
        return (self.size,)*2

class SelectedShip(VisualEffect):
    def __init__(self, ship):
        VisualEffect.__init__(self)
        self.layer = 9
        self.ship = ship
        self.rect = ship.rect
        self.position = ship.position

    def update(self, viewBox):
        rect = self.ship.rect
        self.image = pygame.Surface(rect.size).convert_alpha()
        self.image.fill(Transparent)
        pygame.draw.circle(self.image, (0xff, 0xff, 0, 0x55),
                (rect.width/2, rect.height/2), rect.width/3, min(5, rect.width/3))
        self.rect = rect

    def step(self, dt):
        if self.ship.armor <= 0:
            self.kill()
        self.position = self.ship.position

    def test_world_size(self):
        return self.ship.test_world_size()

class ExplodeEffect(VisualEffect):
    ExplodeSize = 40
    ExplodeT = 0.8
    def __init__(self, source, damage):
        VisualEffect.__init__(self)
        self.layer = 20
        self.position = Vec2d(source)
        self.t = 0
        self.ExplodeSize = damage / 800 * ExplodeEffect.ExplodeSize

    def update(self, viewBox):
        R = self.ExplodeSize
        tHalf = self.ExplodeT / 2
        r = int(max(1, R * (1 - (self.t/tHalf - 1)**2)))
        rect = pygame.Rect((0, 0), (r*2, r*2))
        rect.center = viewBox.posWorld2screen(self.position)
        self.image = pygame.Surface(rect.size).convert_alpha()
        self.image.fill(Transparent)
        pygame.draw.circle(self.image, (0xd9, 0x79, 0x30, 0x85), (r, r), r)

        self.rect = rect

    def test_world_size(self):
        return self.rect.size

    def step(self, dt):
        self.t += dt
        if self.t >= self.ExplodeT:
            self.kill()

class BulletHit(VisualEffect):
    Size = 15
    ExplodeSize = 30
    ExplodeT = 0.8
    def __init__(self, source, target, time):
        VisualEffect.__init__(self)
        self.layer = 20
        self.source = source
        self.target = target
        self.position = Vec2d(source)
        self.v = (Vec2d(target) - source) / time
        self.time = time
        self.t = 0
        self.exploded = 0

    def update(self, viewBox):
        if not self.exploded:
            w = int(viewBox.lenWorld2screen(self.Size))
            rect = pygame.Rect((0, 0), (w, w))
            rect.center = viewBox.posWorld2screen(self.position)
            self.image = pygame.Surface(rect.size).convert_alpha()
            self.image.fill(Transparent)
            pygame.draw.circle(self.image, (0, 0, 0, 0xff), (w/2, w/2), max(w/2, 1))
        else:
            R = self.ExplodeSize
            tHalf = self.ExplodeT / 2
            r = int(max(1, R * (1 - (self.t/tHalf - 1)**2)))
            rect = pygame.Rect((0, 0), (r*2, r*2))
            rect.center = viewBox.posWorld2screen(self.position)
            self.image = pygame.Surface(rect.size).convert_alpha()
            self.image.fill(Transparent)
            pygame.draw.circle(self.image, (0xd9, 0x79, 0x30, 0x85), (r, r), r)

        self.rect = rect

    def test_world_size(self):
        return self.rect.size

    def step(self, dt):
        self.t += dt
        if not self.exploded:
            self.position += dt * self.v
            if self.t >= self.time:
                self.exploded = 1
                self.time = 0.8
                self.t = 0
        elif self.t >= self.time:
            self.kill()
