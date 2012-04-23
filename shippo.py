import config
import pygame
import dashboard
import visual
import math
import socket
from socket import socket as Socket
from events import *
from pygame.locals import *
from player import Player, HumanPlayer
from ship import Ship, ShipInfo
from resource import Resource, ResourceInfo
from vec2d import Vec2d
from viewBox import ViewBox
from viewControl import ViewControl
from heapq import heappush, heappop
from win import WinScreen


class Instruction:
    """Every """
    def __init__(self, rawstr):
        args = rawstr.split()
        cmd, sec = args[:2]
        args = args[2:]
        self.cmd = cmd
        self.sec = sec
        self.args = args

def sprite_cmp(s1, s2):
    return cmp(s1.layer, s2.layer)

class Shippo:
    W = config.W
    H = config.H
    SpeedUp = 2
    FPS = 30
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
        self.statusBoard = dashboard.StatsBoard()
        self.events = []
        self.UISprites = []
        self.visualSprites = []

        self.needQuit = 0
        self.running = False
        self.renderCnt = 0

        self.blockings = []
        self.accuCallbacks = []

        self.pyeventHandlers = []
        self.ViewControl = None
        self.winScreen = None


    def add_player(self, player):
        self.players.append(player)

    def apply_instruction(self, inst):
        # apply an instruction
        cmd = inst.cmd
        args = inst.args
        if cmd == 'MoveTo':
            self.ins_move_to(inst.faction, int(args[0]), float(args[1]), float(args[2]))
        elif cmd == 'Data':
            self.ins_data(inst.faction)
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
            self.inform('Unknown instruction %s' % inst)

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
        lines.append("OSInterface %d" % (4))
        lines.append("Faction %d" %(faction,))
        lines.append("Running %s" %(self.running,))
        lines.append("Resource %d" %(len(resourceInfos),))
        for info in resourceInfos:
            lines.append("%s" % info.to_rawstr())
        lines.append("Ship %d" %(len(shipInfos),))
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
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moveTarget = Vec2d(x, y)
        ship.moving = True
        ship.rotating = True
        return True

    def ins_data(self, faction):
        data = self.to_rawstr(faction)
        player = self.players[faction - 1]
        player.send_data(self)

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

    def ins_stop_moving(self, faction, shipId):
        # stop both moving and rotating
        ship = self.get_ship_by_id(shipId)
        if ship is None or ship.faction != faction:
            return False
        ship.moving = False
        ship.moveTarget = None
        return True

    def ins_stop(self, faction, shipId):
        # stop both moving and rotating
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
        self.renderTimer.tick()
        screen = self.screen
        viewBox = self.viewBox
        # draw the sea
        screen.fill((0, 0, 0, 0xff))
        self.background.update(viewBox)
        screen.blit(self.background.image, self.background.rect)

        # draw the white border
        w, h = (config.MapWidth, config.MapHeight)
        rect = pygame.Rect((0, 0), (viewBox.lenWorld2screen(w), viewBox.lenWorld2screen(h)))
        rect.center = viewBox.posWorld2screen((0, 0))
        pygame.draw.rect(screen, (0x7f, 0x7f, 0x7f, 0x30), rect, 1)

        # update sprites
        # draw visual effects
        # draw the resources
        # draw the ships
        sprites = self.resources + self.ships + self.visualSprites
        sprites.sort(sprite_cmp)
        for sp in sprites:
            if viewBox.inside(sp):
                sp.update(viewBox)
                screen.blit(sp.image, sp.rect)

        # draw ship moving targets, attacking target, if exist
        attackR = viewBox.lenWorld2screen(config.CannonRange) 
        attackRect = pygame.Rect((0, 0), (attackR * 2, )*2)
        for ship in self.ships:
            target = ship.moveTarget
            center = map(int, viewBox.posWorld2screen(ship.position))
            if target:
                pygame.draw.aaline(screen, pygame.Color("yellow"), center,
                        map(int, viewBox.posWorld2screen(target)))
            if ship.attackTarget:
                pygame.draw.aaline(screen, pygame.Color("red"), center,
                        map(int, viewBox.posWorld2screen(ship.attackTarget.position)))

            if ship._show_debug:
                # draw range of view
                pygame.draw.circle(screen, pygame.Color("green"), center, 
                        int(viewBox.lenWorld2screen(config.RangeOfView)), 1)
                # draw range of attack
                # DOC: pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width=1): return Rect
                angle = ship.direction.angle
                attackRect.center = center
                a0 = (180 - config.CannonAngle)/2
                # pygame.draw.arc(screen, Color("red"), attackRect, math.radians(angle + a0), math.radians(angle + 180))
                pygame.draw.arc(screen, Color("red"), attackRect, -math.radians(angle + 180 - a0), -math.radians(angle + a0))
                pygame.draw.arc(screen, Color("red"), attackRect, -math.radians(angle - a0), -math.radians(angle - 180 + a0))
                pygame.draw.circle(screen, pygame.Color("green"), center, 
                        int(viewBox.lenWorld2screen(config.RangeOfView)), 1)
        # draw dashBoard
        dash = self.dashBoard
        self.renderCnt += 1
        if self.renderCnt % 3 == 0:
            dash.update()
        screen.blit(dash.image, dash.rect)

        self.statusBoard.update()
        screen.blit(self.statusBoard.image, self.statusBoard.rect)

        # draw UI sprites
        for sp in self.UISprites:
            if sp.visible:
                sp.update()
                self.screen.blit(sp.image, sp.rect)

        # draw winScreen
        if self.winScreen:
            self.winScreen.update()
            screen.blit(self.winScreen.image, self.winScreen.rect)

        pygame.display.flip()

    def quit(self):
        self.needQuit = 1

    def inform(self, msg):
        print msg

    def wait_connect(self):
        server = Socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind(('', config.Port))
        except socket.error as e:
            print e
            sleep(1)
        server.listen(2)
        server.settimeout(0.0)

        player1 = Player(1, server)
        player2 = HumanPlayer(2)
        self.pyeventHandlers.append(player2)
        players = [player1, player2, None]

        timer = pygame.time.Clock()
        # wait until connected 2 players
        finished = 0
        player = players[finished]
        try:
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
                timer.tick(20)
        except KeyboardInterrupt:
            server.close()
            return False
        return True

    def setup_level(self, level=0):
        self.background = visual.Background('sea_wrap.png')

        p0 = Vec2d(250, 900)
        p1 = Vec2d(config.MapWidth - p0.x, p0.y)
        p2 = Vec2d(600, 600)
        p3 = Vec2d(config.MapWidth - p2.x, config.MapHeight - p2.y)
        p0 = Vec2d(-750, -100)
        p1 = Vec2d(750 , p0.y)
        p2 = Vec2d(-400, -400)
        p3 = Vec2d(400, 400)

        dh = 40
        level0 = {'rPoss':[(p2.x, p2.y), (p2.x, p3.y), (p3.x, p2.y), (p3.x, p3.y), (p2+p3)/2],
                'sPoss1':[p0 + (0, i * dh) for i in xrange(5)],
                'sPoss2':[p1 + (0, i * dh) for i in xrange(5)],
                }
        self.timeLimit = 60 * 5
        id = 1
        for pos in level0['rPoss']:
            resource = Resource(id, pos)
            id += 1
            self.resources.append(resource)
            self.pyeventHandlers.append(resource.button)
        # add ship for player 1
        id = 1
        player = self.players[0]
        for pos in level0['sPoss1']:
            ship = Ship(id, 1, pos)
            # ship.moving = 1
            ship.color = player.color
            player.ships.append(ship)
            self.ships.append(ship)
            self.pyeventHandlers.append(ship.button)
            id += 1

        # add ship for player 2
        player = self.players[1]
        for pos in level0['sPoss2']:
            ship = Ship(id, 2, pos)
            ship.direction.rotate(180)
            ship.color = player.color
            player.ships.append(ship)
            self.ships.append(ship)
            self.pyeventHandlers.append(ship.button)
            id += 1

        # add dahsboard for player
        for player in self.players:
            dash = dashboard.ShipStatus(self.SubBoardSize, player)
            self.dashBoard.add_board(dash)

        # add ship detail board
        self.detailBoard = dashboard.ShipDetailStatus()
        self.dashBoard.add_board(self.detailBoard)

        # add view controller
        self.viewControl = ViewControl(self)
        self.pyeventHandlers.append(self.viewControl)

        self.viewBox.zoom((0, 0), -0.4)
        self.viewBox.move_to((0, 0))

        # add render timer
        self.renderTimer = pygame.time.Clock()

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
                # apply the instruction, maybe not success
                self.apply_instruction(inst)
                done = True

    def mainloop(self):
        # start game
        self.t = 0.
        self.running = True

        renderDt = 1.0/self.FPS*self.SpeedUp
        instDt = 1.0/config.MaxInstPerSec
        eventDt = 1.0/self.FPS
        logicDt = 1.0/self.LFPS

        timer = pygame.time.Clock()
        timer1 = pygame.time.Clock()
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

        def update_status():
            sec = max(int(self.timeLimit - self.t), 0)
            self.statusBoard.update_info('FPS %.1f PFPS: %.1f TIME LEFT: %02d:%02d' %(self.renderTimer.get_fps(), timer.get_fps(), sec/60, sec % 60))
        self.register_accumulate_callback(1.0, update_status)

        while not self.needQuit:
            timer1.tick()
            # try activate accumulate callbacks
            for acb in self.accuCallbacks:
                at, adt, callback = acb
                if at >= adt:
                    acb[0] -= adt
                    callback()
            if self.needQuit: break
            # game logic
            # dt = (logicDt - timer1.tick()/1000) * self.SpeedUp
            dt = logicDt * self.SpeedUp
            self.step(dt)
            if self.needQuit: break
            for acb in self.accuCallbacks:
                acb[0] += dt
                # acb[0] += logicDt
            timer.tick(self.LFPS)
            # print 'LFPS:', timer.get_fps()

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

    def ship_attack(self, time, ship):
        if ship.attackTarget is None: return
        for cannon in [0, 1]:
            if ship.cooldowns[cannon] == 0 and ship.in_cannon_range(cannon, ship.attackTarget):
                target = ship.attackTarget
                dp = (target.position - ship.position)
                d = dp.length
                R = config.CannonRange
                damage = 200 * (1 - (d/R)**2)**0.5 * (
                        1 - ship.direction.normalized().dot( ship.velocity - target.velocity)/ 100)
                p1 = target.direction.rotated(-30)
                p2 = target.direction.rotated(30)
                if p1.cross(dp) * p2.cross(dp) <= 0:
                    # bonus hit
                    damage *= 2
                self.add_event(ShipDamage(time + d / 150, target, damage))
                self.visualSprites.append(visual.BulletHit(ship.position, target.position, d / 150))
                ship.cooldowns[cannon] = config.CannonSpan
                break

    def handle_event(self, event):
        if isinstance(event, ObjHit):
            # handle ObjHit
            obj1 = event.obj1
            obj2 = event.obj2
            dp = obj2.position - obj1.position
            R = (obj1.hitRadius + obj2.hitRadius)
            dpnor = dp.normalized()
            # hit damage detection
            if isinstance(obj2, Ship) and obj2.faction != obj1.faction:
            # if isinstance(obj2, Ship):
                dv = obj1.velocity - obj2.velocity
                if dv.dot(dpnor) > 7.5 and dpnor.dot(obj1.direction.normalized()) >= 0.8660254037: # sqrt(3)/2
                    hitDamage = obj1.direction.dot(dv) * 14 + 100
                    self.add_event(ShipDamage(event.time, obj2, hitDamage))
                    self.add_event(ShipDamage(event.time, obj1, hitDamage/2))
                    self.visualSprites.append(visual.ExplodeEffect((obj1.position + obj2.position)/2, hitDamage))
                    # print '%d hit %d, damage %s' %(obj1.id, obj2.id, hitDamage)
                obj1.position -= (2 + R - dp.length)/2 * dpnor
                obj2.position += (2 + R - dp.length)/2 * dpnor
            else:
                obj1.position -= (R - dp.length) * dpnor
            v1 = obj1.velocity
            v1 -= dpnor * dpnor.dot(v1)
            # v1 *= 0
            # v1 *= 0.2

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
            if ship not in self.ships: return
            self.ships.remove(ship)
            for ship1 in self.ships:
                if ship1.attackTarget == ship:
                    ship1.attackTarget = None
            self.players[ship.faction-1].ships.remove(ship)

    def hittest(self, obj1, obj2):
        dp = obj2.position - obj1.position
        R = obj1.hitRadius + obj2.hitRadius
        if dp.length <= R:
            if obj1.velocity.dot(dp.normalized()) > 0:
                return True
        return False

    def detect_hit(self):
        for ship in self.ships:
            for ship1 in self.ships:
                if ship != ship1:
                    if self.hittest(ship, ship1):
                        hitEvent = ObjHit(self.t, ship, ship1)
                        # self.blockings.append((ship, ship1))
                        self.add_event(hitEvent)
            for resource in self.resources:
                if self.hittest(ship, resource):
                    hitEvent = ObjHit(self.t, ship, resource)
                    # self.blockings.append((ship, resource))
                    self.add_event(hitEvent)

    def step(self, dt0):
        events = self.events
        t = 0
        for ship in self.ships:
            ship.blocked = 0
        while t < dt0:
            dt = dt0 - t
            if events:
                dt = min(dt, events[0].time - self.t)
            # dtr = self.phy_step(dt)
            # for ship in self.ships:
            #     ship.short_step(-dtr)
            #     ship.step(dtr)
            # t += dtr
            for ship in self.ships:
                ship.step(dt)
            t += dt
            self.t += dt
            self.detect_hit()

            while events and events[0].time <= self.t:
                e = heappop(events)
                self.handle_event(e)

        for sp in self.visualSprites:
            sp.step(dt0)
        self.visualSprites = [effect for effect in self.visualSprites if not effect._kill]

        # ship try attack
        for ship in self.ships:
            if ship.attackTarget is not None:
                # try to attack
                self.ship_attack(self.t, ship)
        # ship recover
        for player in self.players:
            recover = dt * config.ResourceRestoreRate[sum(1 for r in self.resources if r.faction == player.faction)]
            if recover:
                for ship in player.ships:
                    ship.armor = min(ship.armor + recover, config.MaxArmor)
        # out side damage
        w = config.MapWidth/2
        h = config.MapHeight/2
        for ship in self.ships:
            x, y = ship.position
            if x < -w or x > w  or x <-h or x > h:
                self.add_event(ShipDamage(self.t, ship, 25 * dt0))
        # resource distribute
        for res in self.resources:
            del res.ships[:]
            for ship in self.ships:
                if (ship.position - res.position).length <= config.ResourceRadius:
                    res.ships.append(ship)
            res.step(dt0)
            if res.faction:
                col = res.boundingColor
                col1 = self.players[res.faction-1].color
                col.r, col.g, col.b = col1.r, col1.g, col1.b
        # event handle
        while events and events[0].time <= self.t:
            e = heappop(events)
            self.handle_event(e)
        # test gameover
        if self.winScreen is None:
            self.test_gameover()
        elif self.winScreen.finished:
            self.quit()

    def test_gameover(self):
        # test if a player wins
        winner = None
        p1 = self.players[0]
        p2 = self.players[1]
        cnt1 = len(p1.ships)
        cnt2 = len(p2.ships)
        if self.t <= self.timeLimit:
            if cnt2 == 0:
                winner = p1
            elif cnt1 == 0:
                winner = p2
        else:
            if cnt1 != cnt2:
                if cnt1 > cnt2:
                    winner = p1
                elif cnt1 < cnt2:
                    winner = p2
                else:
                    rcnt1 = sum(1 for r in self.resources if r.faction == player1.faction)
                    rcnt2 = sum(1 for r in self.resources if r.faction == player2.faction)
                    if rcnt1 > rcnt2:
                        winner = p1
                    elif rcnt1 < rcnt2:
                        winner = p2
                    else:
                        hp1 = sum(ship.armor for ship in player1.ships)
                        hp2 = sum(ship.armor for ship in player2.ships)
                        if hp1 > hp2:
                            winner = p1
                        else:
                            winner = p2
        if winner is not None:
            win = WinScreen(winner)
            self.winScreen = win
            self.pyeventHandlers.append(win)
            return True
        return False
