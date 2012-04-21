import config
import pygame
import dashboard
import visual
from events import *
from pygame.locals import *
from player import Player, HumanPlayer
from ship import Ship, ShipInfo
from resource import Resource, ResourceInfo
from vec2d import Vec2d
from viewBox import ViewBox
from viewControl import ViewControl
from heapq import heappush, heappop


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
    W = config.W
    H = config.H
    FPS = 40
    LFPS = 60 # logic frame per sec
    SeaColor = (0, 0x55, 0xff, 0xff)
    BoardSize = (270, H-4)
    BoardPos = (W - 270 - 2, 2)
    SubBoardSize = (260, 200)
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.DOUBLEBUF, 32)
        pygame.display.set_caption('MSRA2012 Python version')
        self.viewBox = ViewBox((self.W, self.H))
        self.reset()


    def reset(self):
        self.players = []
        self.ships = []
        self.resources = []
        self.dashBoard = dashboard.DashBoard(self.BoardPos, self.BoardSize)
        self.events = []
        self.UISprites = []
        self.visualSprites = []

        self.needQuit = 0
        self.currentSec = 0
        self.running = False

        self.blockings = []
        self.accuCallbacks = []

        self.pyeventHandlers = []
        self.ViewControl = None

    def add_player(self, player):
        dash = dashboard.ShipStatus(self.SubBoardSize, player)
        self.dashBoard.add_board(dash)
        self.players.append(player)

    def apply_instruction(self, inst):
        # apply an instruction
        print 'apply', inst
        cmd = inst.cmd
        args = inst.args
        if cmd == 'MoveTo':
            self.ins_move_to(inst.faction, int(args[0]), float(args[1]), float(args[2]))
        elif cmd == 'Attack':
            self.ins_attack(inst.faction, int(args[0]), int(args[1]))
        elif cmd == 'StartRotating':
            self.ins_start_rotating(inst.faction, int(args[0]), float(args[1]))
        elif cmd == 'StartMoving':
            self.ins_start_moving(inst.faction, int(args[0]))
        elif cmd == 'StopRotating':
            self.ins_stop_rotating(inst.faction, int(args[0]))
        elif cmd == 'Stop':
            self.ins_stop(inst.faction, int(args[0]))
        elif cmd == 'StartRotatingTo':
            self.ins_start_rotating_to(inst.faction, int(args[0]), float(args[1]), float(args[2]))
        else:
            # invalid command
            print 'Unknown instruction %s' % inst

    def to_rawstr(self, faction):
        # generate the info to player specified by playerId
        shipInfos = []
        resourceInfos = []
        for resource in self.resources:
            resourceInfos.append(ResourceInfo(resource))
        myships = [ship for ship in self.ships if ship.faction == faction]
        for ship in self.ships:
            if ship.faction != faction:
                for ship0 in myships:
                    if (ship0.position - ship.position).length <= config.RangeOfView:
                        shipInfos.append(ShipInfo(ship))
                        break
            else:
                shipInfos.append(ShipInfo(ship))
        lines = []
        lines.append("OSInterface %d" % (2 + len(shipInfos) + len(resourceInfos)))
        lines.append("Faction %d" %(faction,))
        lines.append("Running %s" %(self.running,))
        lines.append("Resource %d" %(len(resourceInfos),))
        for info in resourceInfos:
            lines.append("%s" % info.to_rawstr())
        lines.append("  Ship %d" %(len(shipInfos),))
        for info in shipInfos:
            lines.append("%s" % info.to_rawstr())
        lines.append("")
        return '\n'.join(lines)

    def get_ship_by_id(self, shipId):
        for ship in self.ships:
            if ship.id == shipId:
                return ship
        return None

    def ins_move_to(self, faction, shipId, x, y):
        print 'ins_move_to', shipId, x, y
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moveTarget = Vec2d(x, y)
        ship.moving = True
        ship.rotating = True
        return True

    def ins_attack(self, faction, shipId1, shipId2):
        ship1 = self.get_ship_by_id(shipId1)
        if ship1 is None or ship1.faction != faction:
            return False
        ship2 = self.get_ship_by_id(shipId2)
        # attack
        ship1.attackTarget = ship2
        return True

    def ins_start_rotating(self, faction, shipId, angle):
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.rotating = True
        ship.moveTarget = None
        ship.rotateTarget = angle
        return True

    def ins_stop_rotating(self, faction, shipId):
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.rotating = False
        ship.rotateTarget = None
        ship.moveTarget = None
        return True

    def ins_start_moving(self, faction, shipId):
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moveTarget = None
        ship.moving = True
        return True

    def ins_stop(self, faction, shipId):
        # stop both moving and rotating
        print 'ins_stop', shipId
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moving = False
        ship.rotating = False
        ship.moveTarget = None
        ship.rotateTarget = None
        return True

    def ins_start_rotating_to(self, faction, shipId, x, y):
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moveTarget = None
        ship.rotating = True
        ship.rotateTarget = (x, y)
        return True

    def render(self):
        screen = self.screen
        viewBox = self.viewBox
        # draw the sea
        screen.fill((0, 0, 0, 0xff))
        self.background.update(viewBox)
        screen.blit(self.background.image, self.background.rect)

        # draw the white border
        w, h = (config.MapWidth, config.MapHeight)
        rect = pygame.Rect((0, 0), (viewBox.lenWorld2screen(w), viewBox.lenWorld2screen(h)))
        rect.topleft = viewBox.posWorld2screen(rect.topleft)
        pygame.draw.rect(screen, (0xff,)*4, rect, 1)
        
        # update sprites
        # draw visual effects
        for sp in self.visualSprites:
            if viewBox.inside(sp):
                sp.update(viewBox)
                screen.blit(sp.image, sp.rect)
        self.visualSprites = [effect for effect in self.visualSprites if not effect._kill]
        # draw the resources
        # draw the ships
        sprites = self.resources + self.ships
        for sp in sprites:
            if viewBox.inside(sp):
                sp.update(viewBox)
                screen.blit(sp.image, sp.rect)
        # draw dashBoard
        dash = self.dashBoard
        dash.update()
        screen.blit(dash.image, dash.rect)

        # draw UI sprites
        for sp in self.UISprites:
            if sp.visible:
                sp.update()
                self.screen.blit(sp.image, sp.rect)

        pygame.display.flip()

    def quit(self):
        self.needQuit = 1

    def inform(self, msg):
        print msg

    def wait_connect(self):
        player1 = Player(1, config.Port + 1)
        player2 = HumanPlayer(2)
        self.pyeventHandlers.append(player2)
        players = [player1, player2, None]

        timer = pygame.time.Clock()
        # wait until connected 2 players
        finished = 0
        player = players[finished]
        while finished < 2:
            self.inform('waiting for AI to connect...')
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                    break
            if self.needQuit: break
            if player.connect():
                self.add_player(player)
                self.inform('AI %s connected' % (player.name))
                finished += 1
                player = players[finished]
            # self.render()
            timer.tick(self.FPS)

    def setup_level(self, level=0):
        self.background = visual.Background('sea.jpg')

        p0 = Vec2d(250, 900)
        p1 = Vec2d(config.MapWidth - p0.x, p0.y)
        p2 = Vec2d(600, 600)
        p3 = Vec2d(config.MapWidth - p2.x, config.MapHeight - p2.y)

        level0 = {'rPoss':[(p2.x, p2.y), (p2.x, p3.y), (p3.x, p2.y), (p3.x, p3.y), (p2+p3)/2],
                'sPoss1':[p0 + (0, i * 80) for i in xrange(5)],
                'sPoss2':[p1 + (0, i * 80) for i in xrange(5)],
                }
        id = 1
        for pos in level0['rPoss']:
            resource = Resource(id, pos)
            id += 1
            self.resources.append(resource)
        # add ship for player 1
        id = 1
        player = self.players[0]
        for pos in level0['sPoss1']:
            ship = Ship(id, 1, pos)
            ship.moving = 1
            ship.color = player.color
            player.ships.append(ship)
            self.ships.append(ship)
            id += 1
        # add ship for player 2
        player = self.players[1]
        for pos in level0['sPoss2']:
            ship = Ship(id, 2, pos)
            ship.direction.rotate(180)
            ship.color = player.color
            player.ships.append(ship)
            self.ships.append(ship)
            id += 1

        # add ship detail board
        self.detailBoard = dashboard.ShipDetailStatus()
        self.dashBoard.add_board(self.detailBoard)

        # add view controller
        self.viewControl = ViewControl(self)
        self.pyeventHandlers.append(self.viewControl)

        self.viewBox.zoom((self.W/2, self.H/2), -0.4)

    def handle_pyevents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
                break
            for handler in self.pyeventHandlers:
                handler.handle(event)
        # make handler alive
        for handler in self.pyeventHandlers:
            handler.step()

    def accept_insts(self):
        # accept instructions
        for player in self.players:
            done = False
            while not done:
                inst = player.fetch_instruction()
                if inst is None: 
                    break
                if inst.sec != self.currentSec:
                    continue
                # apply the instruction, maybe not success
                self.apply_instruction(inst)
                done = True
        for player in self.players:
            player.iteration(self)

    def mainloop(self):
        # start game
        self.t = 0.
        self.running = True

        renderDt = 1.0/self.FPS
        instDt = 1.0/config.MaxInstPerSec 
        eventDt = 1.0/self.FPS
        logicDt = 1.0/self.LFPS

        timer = pygame.time.Clock()
        timer1 = pygame.time.Clock()
        self.currentSec = 0
        # accuCallbacks, add by order
        self.register_accumulate_callback(eventDt, self.handle_pyevents)
        self.register_accumulate_callback(instDt, self.accept_insts)
        self.register_accumulate_callback(renderDt, self.render)
        # add visual effect
        def add_visual_effect():
            for ship in self.ships:
                speed = ship.velocity.length
                if speed > 1:
                    effect = visual.WaterEffect(ship.position, speed)
                    self.visualSprites.append(effect)
        self.register_accumulate_callback(0.1, add_visual_effect)

        def clear_instructions():
            for player in self.players:
                player.clear()
        self.register_accumulate_callback(1.0, clear_instructions)

        while not self.needQuit:
            self.currentSec = int(self.t)
            timer1.tick()
            # try activate accumulate callbacks
            for acb in self.accuCallbacks:
                at, adt, callback = acb
                if at >= adt:
                    acb[0] -= adt
                    callback()
            if self.needQuit: break
            # game logic
            # dt = logicDt - timer1.tick()/1000
            dt = logicDt
            self.step(dt)
            dt = timer.tick(self.LFPS) / 1000.0
            for acb in self.accuCallbacks:
                acb[0] += dt
            self.t += dt 
            # print 'FPS:', timer.get_fps()

    def register_accumulate_callback(self, dt, callback):
        self.accuCallbacks.append([0, dt, callback])

    def add_event(self, e):
        heappush(self.events, e)

    def phy_step(self, dt0):
        dtl, dtr = 0.005, dt0
        t = 0
        for ship in self.ships:
            ship.short_step(dtl - t)
        t = dtl

        while dtr - dtl > 1e-4:
            dtm = (dtl + dtr) / 2
            for ship in self.ships:
                ship.short_step(dtm - t)
            t = dtm
            if self.exist_hit():
                dtr = dtm
            else:
                dtl = dtm
        return t

    def ship_attack(self, ship, cannon, targetID):
        """cannon = 0 or 1, target maybe None or other shipId"""
        # TODO
        pass

    def handle_event(self, event):
        if isinstance(event, ObjHit):
            obj1 = event.obj1
            obj1.velocity *= 0
            obj1.blocked = 1
        elif isinstance(event, ShipDamage):
            ship = event.ship
            damage = event.damage
            ship.armor -= damage
            if ship.armor <= 0:
                self.add_event(ShipDie(event.time, ship))
        elif isinstance(event, ShipRecover):
            ship = event.ship
            ship.armor += event.val
            if ship.armor > config.MaxArmor:
                ship.armor = config.MaxArmor
        # elif isinstance(event, ShipAttack):
        #     ship = event.ships
        #     self.ship_attack(ship, event.cannon, event.target)
        elif isinstance(event, ShipDie):
            ship = event.ship
            self.ships.remove(ship)
            self.players[ship.faction-1].ships.remove(ship)

    def hittest(self, obj1, obj2):
        dp = obj2.position - obj1.position
        R = obj1.hitRadius + obj2.hitRadius
        if dp.length <= R:
            v1 = obj1.velocity
            if v1.dot(dp.normalized()) >= 0:
                return True
        return False

    def exist_hit(self):
        n = len(self.ships)
        ss = self.ships
        for i in xrange(n):
            for j in xrange(n):
                if i != j:
                    if (ss[i], ss[j]) not in self.blockings:
                        if self.hittest(ss[i], ss[j]):
                            return True
            for r in self.resources:
                if (ss[i], r) not in self.blockings:
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
            for ship in self.ships:
                ship.short_step(-dtr)
                ship.step(dtr)
            t += dtr
            if self.exist_hit():
                for ship in self.ships:
                    for ship1 in self.ships:
                        if ship != ship1 and (ship, ship1) not in self.blockings:
                            if self.hittest(ship, ship1):
                                hitEvent = ObjHit(self.t + t, ship, ship1)
                                self.blockings.append((ship, ship1))
                                self.add_event(hitEvent)
                    for resource in self.resources:
                        if self.hittest(ship, resource) and (ship, resource) not in self.blockings:
                            hitEvent = ObjHit(self.t + t, ship, resource)
                            self.blockings.append((ship, resource))
                            self.add_event(hitEvent)
                #exist hit
                # print 'exist hit', self.events
            # print events

            while events:
                if events[0].time > self.t + t:
                    break
                e = heappop(events)
                self.handle_event(e)

            blockings = []
            for obj1, obj2 in self.blockings:
                if self.hittest(obj1, obj2):
                    obj1.velocity *= 0
                    blockings.append((obj1, obj2))
                else:
                    obj1.blocked = False
            self.blockings = blockings
            # print 'Blocking', self.blockings
        for sp in self.visualSprites:
            sp.step(dt0)
