from pygame.sprite import Sprite
import config
import pygame
from pygame import Rect, Color
from ship import Ship
from resource import Resource

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
        self.target = None
        self.font = pygame.font.SysFont('monospace', 12)
        # self.clearRect = pygame.Rect((x0 - R, y0 - R), (2*R, 2*R))
        margin = self.Margin + 1
        self.clearRect = pygame.Rect((margin-1, margin-1), (self.size[0]-2*margin, self.size[1]-2*margin))

    def update_target(self, target):
        self.target = target

    def update(self):
        draw = pygame.draw
        # clear
        draw.rect(self.image, self.BgColor, self.clearRect)
        if self.target is None: 
            return
        margin = self.Margin
        if isinstance(self.target, Ship):
            ship = self.target

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
        elif isinstance(self.target, Resource):
            res = self.target

            x0, y0 = margin + 2, margin + 2
            dy = self.TitleHeight + 2
            self.write((x0, y0), 'ID:')
            self.write((x0, y0 + dy), 'faction:')
            self.write((x0, y0 + dy * 2), 'position:')

            x1, y1 = x0 + self.TitleWidth, y0
            self.write((x1, y1), str(res.id))
            self.write((x1, y1 + dy), str(res.faction))
            self.write((x1, y1 + dy * 2), str(res.position))

class HPRecorder:
    FPS = 30 / 3
    HPColor = (0x88, 0, 0, 0xff)
    HPColorDamage = (0xff, 0, 0, 0xff)
    HPColorRecover = (0xff, 0, 0, 0xff)
    def __init__(self, ship):
        self.ship = ship
        self.hp1 = ship.armor
        self.hp2 = ship.armor
        self.t = 0
        self.dt = 1.0/self.FPS
        self.maxT1 = 0.7
        self.maxT2 = 1.2
        self.dhp = 0

    def update(self, image, basePos, width, height):
        xb, yb = basePos
        if self.ship.armor != self.hp1:
            if abs(self.ship.armor - self.hp1) > 5:
                # new damage
                self.hp2 = self.hp1
                self.hp1 = self.ship.armor
                self.t = 0
                print 'new damage', self.hp1, self.hp2
            else:
                self.hp1 = self.ship.armor
        if self.t < self.maxT1:
            if self.t + self.dt >= self.maxT1:
                self.dhp = (self.hp1 - self.hp2) / (self.maxT2 - self.maxT1)
        elif self.t < self.maxT2:
            self.hp2 += self.dhp * self.dt
        else:
            self.hp2 = self.hp1
        self.t += self.dt

        hp1, hp2 = self.hp1, self.hp2
        rect = Rect((0, 0), (width, hp1/config.MaxArmor * height))
        rect.bottomleft = (xb, yb)
        pygame.draw.rect(image, self.HPColor, rect)
        if hp1 < hp2:
            rect.size = (width, (hp2 - hp1)/config.MaxArmor * height)
            rect.bottomleft = (xb,1 + yb - hp1/config.MaxArmor * height)
            pygame.draw.rect(image, self.HPColorDamage, rect)



class ShipStatus(SubBoard):
    titleWidth = 80
    titleHeight = 18
    barWidth = 20
    barHeight = 100
    barMargin = 10
    dotR = 10
    barColor0 = SubBoard.BgColor
    barColor1 = (0x88, 0, 0, 0xff)
    barColor2 = (0x56, 0x64, 0x9d, 0xff)
    dotColor0 = (0x55, 0x55, 0x55, 0xff)
    dotColor1 = (0x00, 0xff, 0x00, 0xff)
    def __init__(self, size, data):
        SubBoard.__init__(self, size, data)
        self.player = player = data

        self.write((self.Margin, self.Margin), player.name)
        self.p0x, self.p0y = self.titleWidth, 20 + self.Margin
        self.p1x, self.p1y = self.titleWidth, self.p0y + self.barHeight

        self.write((self.Margin, self.p1y), 'moving:')
        self.write((self.Margin, self.p1y + self.titleHeight), 'blocked:')
        self.write((self.Margin, self.p1y + self.titleHeight * 2), 'rotating:')

        self.clearRect = pygame.Rect((self.p0x-1, self.p0y-1),
                (size[0] - self.p0x - 2*self.Margin, size[1] - self.p0y - 2* self.Margin))
                # ((self.barWidth + self.barMargin)*5 + 2, self.barHeight + self.titleHeight * 3 + 2))
        self.ships = player.ships[:]
        self.hpRecorders = [HPRecorder(ship) for ship in self.ships]

    def update(self):
        ships = self.ships
        # clear
        pygame.draw.rect(self.image, self.BgColor, self.clearRect)
        draw = pygame.draw
        barWidth, barHeight = self.barWidth, self.barHeight

        # draw bar
        x, y = self.p0x, self.p0y
        w1 = 3
        w2 = barWidth - w1 * 2
        for ship, hpRecorder in zip(ships, self.hpRecorders):
            draw.rect(self.image, self.barColor0, pygame.Rect((x, y), (barWidth, barHeight)))
            if ship.armor >= 0:
                h0 = (1 - ship.cooldowns[1]/config.CannonSpan)*barHeight
                # h1 = barHeight * ship.armor / config.MaxArmor
                h2 = (1 - ship.cooldowns[0]/config.CannonSpan)*barHeight

                draw.rect(self.image, self.barColor2, 
                        pygame.Rect((x, y + barHeight - h0), (w1, h0)))
                # draw.rect(self.image, self.barColor1, 
                #         pygame.Rect((x + w1, y + barHeight - h1), (w2, h1)))
                hpRecorder.update(self.image, (x + w1, y + barHeight), w2, barHeight)
                draw.rect(self.image, self.barColor2, 
                        pygame.Rect((x + w1 + w2, y + barHeight - h2), (w1, h2)))
            x, y = (x + self.barWidth + self.barMargin, y)
        # draw dots
        r1 = self.barWidth / 2
        r2 = r1 / 2
        x, y = self.p1x + r1, self.p1y + r1
        colors = (self.dotColor0, self.dotColor1)
        for ship in ships:
            y0, y1, y2 = y, y + r1 * 2, y + r1 * 4
            if ship.armor >= 0:
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
        self.hided = 0

    def add_board(self, board):
        if self.boards:
            y = self.boards[-1].rect.bottom + self.Margin
        else:
            y = self.Margin
        x = (self.size[0] - board.size[0]) / 2
        board.rect.topleft = (x, y)
        self.boards.append(board)

    def update(self):
        if self.hided: return
        self.image.fill(self.BgColor)
        for board in self.boards:
            board.update()
            self.image.blit(board.image, board.rect)

class StatsBoard:
    def __init__(self):
        self.info = None
        self.font = pygame.font.SysFont('monospace', 16, bold=True)
        self.update_info('')

    def update(self):
        pass

    def update_info(self, info):
        if self.info != info:
            self.info = info
            w, h = self.font.size(info)
            self.image = self.font.render(info, 1, Color("white"))
            self.rect = Rect((2, 2), (w, h))
