from pygame.sprite import Sprite
import config
import pygame
from pygame import Rect

pygame.font.init()

class SubBoard:
    Margin = 5
    BgColor = (0, 0, 0, 0x88)
    FontColor = (0xff, 0xff, 0xff, 0xff)
    MarginColor = (0x22, 0x22, 0x22, 0x55)
    def __init__(self, size, data):
        self.rect = pygame.Rect((0, 0), size)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.data = data
        self.size = size
        self.font = pygame.font.SysFont('monospace', 14)

        self.image.fill(self.MarginColor)
        # draw bg and margin
        margin = self.Margin
        rect = pygame.Rect((margin, margin), 
                (self.size[0]-2*margin, self.size[1]-2*margin))
        pygame.draw.rect(self.image, self.BgColor, rect)

    def write(self, pos, s):
        self.image.blit(self.font.render(s, 1, self.FontColor), pos)

    def update(self):
        # update using the data
        pass

class ShipDetailStatus(SubBoard):
    TitleWidth = 80
    TitleHeight = 12
    BarWidth = 10
    PanRadius = 60
    PanColor = (0x3f, 0x3f, 0, 0x73)
    VelocityColor = (0xff, 0xff, 0, 0xff)
    DirectionColor = (0x00, 0xff, 0xff, 0xff)

    def __init__(self):
        size = (250, 240)
        SubBoard.__init__(self, size, None)
        self.ship = None
        self.font = pygame.font.SysFont('monospace', 12)
        # self.clearRect = pygame.Rect((x0 - R, y0 - R), (2*R, 2*R))
        margin = self.Margin + 1
        self.clearRect = pygame.Rect((margin, margin), (self.size[0]-2*margin, self.size[1]-2*margin))

    def update_target(self, ship):
        self.ship = ship

    def update(self):
        draw = pygame.draw
        # clear
        draw.rect(self.image, self.BgColor, self.clearRect)
        if self.ship is None: 
            return
        ship = self.ship

        margin = self.Margin
        x0, y0 = margin + 2, margin + 2
        dy = self.TitleHeight + 2
        self.write((x0, y0), 'ID:')
        self.write((x0, y0 + dy), 'faction:')
        self.write((x0, y0 + dy * 2), 'position:')
        self.write((x0, y0 + dy * 3), 'velocity:')
        self.write((x0, y0 + dy * 4), 'direction:')
        x1, y1 = x0 + self.TitleWidth, y0
        self.write((x1, y1), str(ship.id))
        self.write((x1, y1 + dy), str(ship.faction))
        self.write((x1, y1 + dy * 2), str(ship.position))
        self.write((x1, y1 + dy * 3), str(ship.velocity))
        # draw.rect(self.image, self.VelocityColor, Rect((x1, y1 + dy * 3 -1), (self.BarWidth, self.TitleHeight)))
        draw.rect(self.image, self.DirectionColor, Rect((x1, y1 + dy * 4 -1), (self.BarWidth, self.TitleHeight)))

        R = self.PanRadius
        x2, y2 = x0 + self.TitleWidth + R, y1 + dy * 5 + R
        draw.circle(self.image, self.PanColor, (x2, y2), R)
        draw.line(self.image, self.DirectionColor, (x2, y2), 
                (x2 + ship.direction.x * R, y2 + ship.direction.y * R), 2)
        draw.line(self.image, self.VelocityColor, (x2, y2), 
                (x2 + ship.velocity.x / config.MaxSpeed * R, y2 + ship.velocity.y / config.MaxSpeed * R), 1)

class ShipStatus(SubBoard):
    titleWidth = 80
    titleHeight = 18
    barWidth = 20
    barHeight = 100
    barMargin = 10
    dotR = 10
    barColor0 = SubBoard.BgColor
    barColor1 = (0x88, 0, 0, 0xff)
    dotColor0 = (0x55, 0x55, 0x55, 0xff)
    dotColor1 = (0x00, 0xff, 0x00, 0xff)
    def __init__(self, size, data):
        SubBoard.__init__(self, size, data)
        player = data

        self.write((self.Margin, self.Margin), player.name)
        self.p0x, self.p0y = self.titleWidth, 20 + self.Margin
        self.p1x, self.p1y = self.titleWidth, self.p0y + self.barHeight

        self.write((self.Margin, self.p1y), 'moving:')
        self.write((self.Margin, self.p1y + self.titleHeight), 'blocked:')
        self.write((self.Margin, self.p1y + self.titleHeight * 2), 'rotating:')

        self.clearRect = pygame.Rect((self.p0x, self.p0y),
                (size[0] - self.p0x - 2*self.Margin, size[1] - self.p0y - 2* self.Margin))
                # ((self.barWidth + self.barMargin)*5 + 2, self.barHeight + self.titleHeight * 3 + 2))

    def update(self):
        player = self.data
        ships = player.ships
        # clear
        pygame.draw.rect(self.image, self.BgColor, self.clearRect)
        draw = pygame.draw
        barWidth, barHeight = self.barWidth, self.barHeight

        # draw bar
        x, y = self.p0x, self.p0y
        for ship in ships:
            draw.rect(self.image, self.barColor0, pygame.Rect((x, y), (barWidth, barHeight)))
            h1 = barHeight * ship.armor / config.MaxArmor
            draw.rect(self.image, self.barColor1, 
                    pygame.Rect((x, y + barHeight - h1), (barWidth, h1)))
            x, y = (x + self.barWidth + self.barMargin, y)
        # draw dots
        r1 = self.barWidth / 2
        r2 = r1 / 2
        x, y = self.p1x + r1, self.p1y + r1
        colors = (self.dotColor0, self.dotColor1)
        for ship in ships:
            y0, y1, y2 = y, y + r1 * 2, y + r1 * 4
            draw.circle(self.image, colors[int(ship.isMoving)], (x, y0), r2)
            draw.circle(self.image, colors[int(ship.isBlocked)], (x, y1), r2)
            draw.circle(self.image, colors[int(ship.isRotating)], (x, y2), r2)
            x += r1 * 2 + self.barMargin

class DashBoard:
    BgColor = (0, 0, 0, 0x53)
    Margin = 3
    def __init__(self, pos, size):
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.boards = []

    def add_board(self, board):
        if self.boards:
            y = self.boards[-1].rect.bottom + self.Margin
        else:
            y = self.Margin
        x = (self.size[0] - board.size[0]) / 2
        board.rect.topleft = (x, y)
        self.boards.append(board)

    def update(self):
        self.image.fill(self.BgColor)
        for board in self.boards:
            board.update()
            self.image.blit(board.image, board.rect)
