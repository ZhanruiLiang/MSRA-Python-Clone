from vec2d import Vec2d
import config
import pygame
from button import Button
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

    def __init__(self, id, pos):
        self.layer = 5
        self.faction = 0
        self.id = id
        self.position = Vec2d(pos)
        self.hitRadius = config.IslandBoundingRadius

        self.rect = pygame.Rect((0, 0), (2*config.ResourceRadius,)*2)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill(Transparent)
        self.rect.center = self.position
        self.boundingColor = Color(0, 0x88, 0xff, 0x73)
        self.ships = []
        self._lastScale = 1.

        # add button
        self.button = Button(pygame.Rect((0,0), (1,1)), '', 0)

    def __hash__(self):
        return self.id

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
        pygame.draw.circle(self.image, self.boundingColor, (r1, r1), r1, dr)

        # update button
        self.button.rect.center = self.rect.center
        w = max(viewBox.lenWorld2screen(self.hitRadius+5)*2, 10)
        self.button.rect.size = (w, w);

    def test_world_size(self):
        return (config.ResourceRadius*2,)*2

    def step(self, dt):
        f1Cnt = sum(1 for ship in self.ships if ship.faction == 1)
        f2Cnt = sum(1 for ship in self.ships if ship.faction == 2)
        if f1Cnt > f2Cnt:
            self.faction = 1
        elif f1Cnt < f2Cnt:
            self.faction = 2

    def __repr__(self):
        return 'Resource(%s, %s)' %(self.id, self.position)
