import config
import pygame
import dashboard
from events import *
from pygame.locals import *
from player import Player
from ship import Ship, ShipInfo
from resource import Resource, ResourceInfo
from vec2d import Vec2d
from viewBox import ViewBox
from viewControl import ViewControl


class Instruction:
    """Every """
    def __init__(self, rawstr):
        args = rawstr.split()
        cmd, sec = args[:2]
        args = args[2:]
        self.cmd = cmd
        self.sec = sec
        self.args = args

class Shippo:
    W = 1024
    H = 740
    FPS = 20
    LFPS = 60 # logic frame per sec
    SeaColor = (0, 0x55, 0xff, 0xff)
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.W, self.H), 0, 32)
        pygame.display.set_caption('MSRA2012 Python version')
        self.viewBox = ViewBox((self.W, self.H))
        self.reset()


    def reset(self):
        self.players = []
        self.ships = []
        self.resources = []
        self.dashBoards = []
        self.events = []
        self.otherSprites = []

        self.needQuit = 0
        self.currentSec = 0
        self.running = False

    def add_player(self, player):
        dash = dashboard.ShipStatus(player)
        i = len(self.players)
        dash.rect.topleft = (self.W - 320, 20 + i * 250)
        self.dashBoards.append(dash)
        self.players.append(player)

    def apply(self, inst):
        # apply an instruction
        pass

    def to_rawstr(self, playerId):
        # generate the info to player specified by playerId
        pass

    def ins_move_to(self, shipId, x, y):
        pass

    def ins_attack(self, shipId1, shipId2):
        pass

    #TODO: other instructions


    def render(self):
        screen = self.screen
        # draw the sea
        screen.fill(self.SeaColor)
        
        # update sprites
        # draw the resources
        # draw the ships
        sprites = self.resources + self.ships
        for sp in sprites:
            sp.update(self.viewBox)
            screen.blit(sp.image, sp.rect)
        # for sp in self.resources:
        #     if self.viewBox.inside(sp.position, config.ResourceRadius):
        #         sp
        # draw dashBoards
        for dash in self.dashBoards:
            dash.update()
            screen.blit(dash.image, dash.rect)

        # draw other sprites
        for sp in self.otherSprites:
            if sp.visible:
                sp.update()
                self.screen.blit(sp.image, sp.rect)

        pygame.display.flip()

    def quit(self):
        self.needQuit = 1

    def inform(self, msg):
        print msg

    def wait_connect(self):
        timer = pygame.time.Clock()
        nextFaction = 1
        player = Player(nextFaction, config.Port+nextFaction)
        nextFaction += 1
        # wait until connected 2 players
        while len(self.players) < 2:
            self.inform('waiting for AI to connect...')
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                    break
            if self.needQuit: break
            if player.connect():
                self.add_player(player)
                self.inform('AI %s connected' % (player.name))
            player = Player(nextFaction, config.Port+nextFaction)
            nextFaction += 1
            self.render()
            timer.tick(self.FPS)

    def setup_level(self, level=0):

        p0 = Vec2d(50, 900)
        p1 = Vec2d(config.MapWidth - p0.x, p0.y)
        p2 = Vec2d(600, 600)
        p3 = Vec2d(config.MapWidth - p2.x, config.MapHeight - p2.y)

        level0 = {'rPoss':[(p2.x, p2.y), (p0.x, p3.y), (p3.x, p0.y), (p3.x, p3.y), (p0+p3)/2],
                'sPoss1':[p0 + (0, i * 100) for i in xrange(5)],
                'sPoss2':[p1 + (0, i * 100) for i in xrange(5)],
                }
        id = 1
        for pos in level0['rPoss']:
            resource = Resource(id, pos)
            id += 1
            self.resources.append(resource)
        # TODO add ships
        # for pos in level0['sPoss1'

        # add view controller
        self.viewControl = ViewControl(self)

    def mainloop(self):
        # start game
        t = 0.
        self.t = t
        instTAccu = 0.
        renderTAccu = 0.
        self.running = True

        renderDt = 1.0/self.FPS
        instDt = 1.0/config.MaxInstPerSec 
        timer = pygame.time.Clock()
        timer1 = pygame.time.Clock()
        self.currentSec = 0
        while not self.needQuit:
            self.currentSec = int(t)
            timer1.tick()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                    break
                else:
                    # TODO
                    pass
                self.viewControl.handle(event)
            if self.needQuit: break

            # handle instructions
            if instTAccu >= instDt:
                instTAccu -= instDt
                # accept instructions
                for player in self.players:
                    done = False
                    while not done:
                        inst = player.fetch_instruction()
                        if inst is None: 
                            break
                        if inst.sec != currentSec:
                            continue
                        # apply the instruction, maybe not success
                        self.apply(inst)
                        done = True

            # make view controller alive
            self.viewControl.step()
            # game logic
            dt = timer1.tick()
            self.step(dt)
            # render
            if renderTAccu >= renderDt:
                self.render()
                renderTAccu -= renderDt
            dt = timer.tick(self.LFPS)
            instTAccu += dt
            renderTAccu += dt
            t += dt
            self.t = t

    def add_event(self, e):
        heappush(self.event, e)

    def phy_step(self, dt0):
        dtl, dtr = 0.005, dt0
        t = 0
        for ship in self.ships:
            ship.step(dtl - t)
        t = dtl

        while dtr - dtl > 1e-4:
            dtm = (dtl + dtr) / 2
            for ship in self.ships:
                ship.step(dtm - t)
            t = dtm
            if self.exist_hit():
                dtr = dtm
            else:
                dtl = dtm
        return t

    def handle_event(self, event):
        pass

    def hittest(self, obj1, obj2):
        dp = obj2.position - obj1.position
        R = obj1.hitRadius + obj2.hitRadius
        if dp.length < R:
            return True
        return False

    def exist_hit(self):
        n = len(self.ships)
        ss = self.ships
        for i in xrange(n):
            for j in xrange(i+1, n):
                if self.hittest(ss[i], ss[j]):
                    return True
            for r in self.resources:
                if self.hittest(ss[i], r):
                    return True
        return False

    def step(self, dt0):
        events = self.events
        t = 0
        while t < dt0:
            dt = dt0 - t
            if events:
                dt = min(dt, events[0].time - t - self.t)
            dtr = self.phy_step(dt)
            t += dtr
            if self.exist_hit():
                for ship in self.ships:
                    for ship1 in self.ships:
                        if ship != ship1:
                            if self.hittest(ship, ship1):
                                hitEvent = ObjHit(self.t + t, ship, ship1)
                                self.add_event(hitEvent)
                    for resource in self.resources:
                        if self.hittest(ship, resource):
                            hitEvent = ObjHit(self.t + t, ship, resource)
                            self.add_event(hitEvent)

            while events:
                e = heappop(events)
                self.handle_event(e)
                if events[0].time > self.t + t:
                    break
