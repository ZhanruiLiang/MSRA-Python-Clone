import config
from vec2d import Vec2d
import pygame

class ViewBox:
    MinScale = 0.2
    MaxScale = 2.
    MaxSpeed = 60
    def __init__(self, size):
        self.originSize = size
        self.size = map(float, size)
        self.center = Vec2d(size[0]/2, size[1]/2)
        self.scale = 1.0
        self.target = None

    def move(self, dp):
        self.center += dp

    def move_to(self, pos):
        self.center = Vec2d(pos)

    def follow(self, target):
        self.target = target

    def zoom(self, center, ds):
        s = self.scale

        sr = 1/self.scale
        sr += ds
        sr = max(min(sr, self.MaxScale), self.MinScale)
        self.scale = 1/sr

        s1 = self.scale
        px, py = center[0], center[1]
        w, h = self.size
        self.size = tuple(v*self.scale for v in self.originSize)
        w1, h1 = self.size

        self.center.x += px * (s - s1) + w1/2 - w/2
        self.center.y += py * (s - s1) + h1/2 - h/2

    def step(self):
        if self.target:
            dp = self.target.position - self.center
            if dp.length  < self.MaxSpeed:
                self.center = Vec2d(self.target.position)
                # if dp.length > 3:
                #     w0, h0 = self.originSize
                #     pygame.mouse.set_pos((w0/2, h0/2))
            else:
                self.center += dp.normalized() * self.MaxSpeed

    def inside(self, sprite):
        rect1 = pygame.Rect((0, 0), self.size)
        rect1.center = tuple(self.center)
        rect2 = pygame.Rect((0, 0), sprite.test_world_size())
        rect2.center = sprite.position
        return rect1.colliderect(rect2) or rect1.contains(rect2)

    def posScreen2world(self, p):
        w, h = self.size
        lx, ly = self.center - (w/2, h/2)
        return Vec2d(lx + p[0] * self.scale, ly + p[1] * self.scale)

    def posWorld2screen(self, p):
        # convert a point in the world coordinate to screen coordinate
        w, h = self.size
        pTopleft = self.center - (w/2, h/2)
        return (p - pTopleft)/self.scale

    def lenWorld2screen(self, l):
        return l / self.scale

