import config
import pygame
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
        pygame.draw.circle(img, WaterImages.SeaColor, (R, R), R)
        WaterImages.images[size, i] = img
        return img

class Background(Sprite):
    def __init__(self, textureFile):
        texture = pygame.image.load(textureFile).convert_alpha()
        size = texture.get_size()
        ssize = config.W, config.H
        ssize = ssize[0] + size[0], ssize[1] + size[1]
        image = pygame.Surface(ssize).convert_alpha()
        for x in xrange(0, ssize[0], size[0]):
            for y in xrange(0, ssize[1], size[1]):
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
        y = y % w0 - w0
        self.rect.topleft = x, y

class WaterEffect(Sprite):
    def __init__(self, position, speed):
        self.size = 30 * speed / config.MaxSpeed
        self.position = +position 
        self.i = 0
        self.maxT = 0.8
        self.t = 0
        self._kill = 0

    def kill(self):
        self._kill = 1

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

