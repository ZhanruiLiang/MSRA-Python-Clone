from vec2d import Vec2d
import config
import pygame
from pygame import Color
Transparent = (0, 0, 0, 0)

class ResourceInfo:
    def __init__(self, resource):
        self.resource = resource

    def to_rawstr(self):
        r = self.resource
        attrs = {
                'ID': r.id,
                'Faction': r.faction,
                'PositinX': r.position.x,
                'PositinY': r.position.y
                }
        info = 'ResourceInfo{} %d\n%s' %(len(attrs), 
                '\n'.join('%s %s' % (k, v) for k, v in attrs.iteritems()))

class Resource(pygame.sprite.Sprite):
    IslandColor = Color(0, 0x55, 0, 0xff)
    BoundingColor = Color(0, 0x88, 0xff, 0x73)

    def __init__(self, id, pos):
        self.faction = 0
        self.id = id
        self.position = Vec2d(pos)
        self.hitRadius = config.IslandBoundingRadius

        self.rect = pygame.Rect((0, 0), (2*config.ResourceRadius,)*2)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill(Transparent)
        self.rect.center = self.position
        self._lastScale = 1.

    def update(self, viewBox):
        r1 = int(viewBox.lenWorld2screen(config.ResourceRadius))
        r2 = int(viewBox.lenWorld2screen(config.IslandBoundingRadius))
        dr = int(viewBox.lenWorld2screen(24)) + 1
        pos = viewBox.posWorld2screen(self.position)
        if self._lastScale != viewBox.scale:
            self.rect = pygame.Rect((0, 0), (r1*2,)*2)
            self.image = pygame.Surface(self.rect.size).convert_alpha()
            self.image.fill(Transparent)
            self._lastScale = viewBox.scale
        self.rect.center = pos
        pygame.draw.circle(self.image, self.IslandColor, (r1, r1), r2)
        pygame.draw.circle(self.image, self.BoundingColor, (r1, r1), r1, dr)

    def test_world_size(self):
        return (config.IslandBoundingRadius*2,)*2

    def __repr__(self):
        return 'Resource(%s, %s)' %(self.id, self.position)
