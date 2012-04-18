from pygame.sprite import Sprite
import config
import pygame

pygame.font.init()
font = pygame.font.SysFont('monospace', 14)

class SubBoard:
    def __init__(self, size, data):
        self.rect = pygame.Rect((0, 0), size)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.data = data
        self.size = size

    def update(self):
        # update using the data
        pass

class ShipStatus(SubBoard):
    margin = 5
    titleWidth = 80
    titleHeight = 18
    barWidth = 40
    barHeight = 100
    barMargin = 10
    dotR = 10
    bgColor = (0, 0, 0, 0x88)
    marginColor = (0x22, 0x22, 0x22, 0x55)
    barColor0 = bgColor
    barColor1 = (0x88, 0, 0, 0xff)
    dotColor0 = (0x55, 0x55, 0x55, 0xff)
    dotColor1 = (0x00, 0xff, 0x00, 0xff)
    fontColor = (0xff, 0xff, 0xff, 0xff)
    def __init__(self, data):
        size = (300, 200)
        SubBoard.__init__(self, size, data)
        player = data
        self.image.fill(self.marginColor)
        # draw bg and margin
        margin = self.margin
        self.clearRect = pygame.Rect((margin, margin), 
                (self.size[0]-2*margin, self.size[1]-2*margin))
        print self.clearRect
        pygame.draw.rect(self.image, self.bgColor, self.clearRect)

        self.write((self.margin, self.margin), player.name)
        self.p0x, self.p0y = self.titleWidth, 20 + self.margin
        self.p1x, self.p1y = self.titleWidth, self.p0y + self.barHeight

        self.write((margin, self.p1y), 'moving:')
        self.write((margin, self.p1y + self.titleHeight), 'blocked:')
        self.write((margin, self.p1y + self.titleHeight * 2), 'rotating:')

        self.clearRect = pygame.Rect((self.p0x, self.p0y),
                (size[0] - self.p0x - 2*margin, size[1] - self.p0y - 2* margin))
                # ((self.barWidth + self.barMargin)*5 + 2, self.barHeight + self.titleHeight * 3 + 2))
        print self.clearRect


    def write(self, pos, s):
        self.image.blit(font.render(s, 1, self.fontColor), pos)

    def update(self):
        player = self.data
        ships = player.ships
        # clear
        pygame.draw.rect(self.image, self.bgColor, self.clearRect)
        x, y = self.p0x, self.p0y
        draw = pygame.draw
        barWidth, barHeight = self.barWidth, self.barHeight

        for ship in ships:
            draw.rect(self.barColor0, pygame.Rect((x, y), (barWidth, barHeight)))
            h1 = barHeight * ship.armor / config.MaxArmor
            draw.rect(self.barColor1, 
                    pygame.Rect((x, y + barHeight - h1), (barWidth, h1)))
            x, y = (x + self.barMargin, y)
        # draw dots
        # TODO

class DashBoard:
    def __init__(self, xy, size):
        self.rect = pygame.Rect(xy, size)
        self.image = pygame.Surface(self.rect.size).convert_alpha()

    def update(self):
        pass
