from vec2d import Vec2d
from socket import socket as Socket
from instruction import Instruction
from collections import deque
import socket
import threading
import config
import pygame
import visual
from button import Button
from pygame.locals import *
from time import sleep

class Player:
    def __init__(self, faction, server):
        self.name = None
        self.color = pygame.Color(0, 0, 0x8f, 0xff)
        self.id = self.faction = faction
        self.ships = []
        self.resources = []
        self.instructions = []
        self._quit = 0

        self.server = server
        self.connected = False
        self.reciever = None
        self.rfile = self.wfile = None
        self.instLock = threading.Lock()

    def clear(self):
        self.instructions = []

    def fetch_instruction(self):
        # fetch one instruction in the instruction queue
        self.instLock.acquire()
        instruction = None
        if self.instructions:
            instruction = Instruction(self, self.instructions.pop(0))
        self.instLock.release()
        return instruction

    def recieve_instructions(self, lock):
        # recieve all instructions sent by the AI
        # while not self._quit:
        while 1:
            inst = self.rfile.readline()
            # print '%s recv:[%s]'%(self.name, inst)
            if inst is None:
                # connection lost
                self.close()
                break
            elif inst:
                lock.acquire()
                self.instructions.append(inst.rstrip())
                lock.release()
            sleep(0.05)

    def close(self):
        # print 'Connection lost with %s' % str(self.client.getpeername())
        self.connected = False
        self.client.close()

    def connect(self):
        # try to connect, return True if success
        # DUMMY
        # return True
        try:
            client, addr = self.server.accept()
            # client.settimeout(0.0)
            self.client = client
            self.addr = addr
            self.rfile = self.client.makefile('r')
            self.wfile = self.client.makefile('w')
            print 'Connected to %s' % str(self.client.getpeername())
            self.connected = True
            self.reciever = threading.Thread(target=self.recieve_instructions, 
                    args=(self.instLock,))
            self.reciever.daemon = 1
            self.reciever.start()

        except socket.error:
            return False

        # get AI info
        while 1:
            inst = self.fetch_instruction()
            if inst and inst.cmd == 'Info':
                name, rgb = inst.args
                r, g, b = rgb.split('.')
                self.color = pygame.Color(*map(int, (r, g, b, 0xff)))
                self.name = name
                break
            sleep(0.05)
        return True

    def send_data(self, shippo):
        # call the AI's iteration
        data = '%s\n' % shippo.to_rawstr(self.faction);
        # print 'sent:','-'*80
        # print data
        # print '<'*80
        try:
            self.wfile.write(data)
            self.wfile.flush()
        except socket.error:
            print 'Connection to AI %s lost' % (self.name,)
            self.close()

class HumanPlayer(Player):
    def __init__(self, faction):
        Player.__init__(self, faction, 0)
        self.name = 'HumanPlayer'
        self.color = pygame.Color(0, 0x8f, 0, 0xff)
        self.shippo = None
        self.selected = set()
        self.bindedShips =  set()

        self.connected = False

    def selector(self, ship):
        def select_callback(event):
            if event.button == 1:
                add = pygame.key.get_mods() & pygame.KMOD_SHIFT
                if ship.faction == self.faction:
                    self.select(ship, add)
        return select_callback

    def mark_attack_er(self, target):
        def mark_attack(event):
            for ship, sp in self.selected:
                self.instructions.append('Attack %d %d %d' % (self.shippo.t, ship.id, target.id))
                self.marked = 1
            return True
        return mark_attack

    def connect(self):
        self.connected = True
        self.instructions.append('Data 0')
        return True

    def send_data(self, shippo):
        self.shippo = shippo
        for ship in shippo.ships:
            if ship not in self.bindedShips:
                if ship.faction == self.faction:
                    ship.button.bind(Button.Press, self.selector(ship))
                else:
                    ship.button.bind(Button.Press, self.mark_attack_er(ship))
                self.bindedShips.add(ship)

    def step(self):
        if not self.shippo: return
        viewBox = self.shippo.viewBox

    def select(self, ship, add=0):
        if self.shippo:
            sp = visual.SelectedShip(ship)
            if not add:
                visualSprites = self.shippo.visualSprites
                for ship1, sp1 in self.selected:
                    if sp1 in visualSprites:
                        visualSprites.remove(sp1)
                self.selected.clear()
            self.selected.add((ship, sp))
            self.shippo.visualSprites.append(sp)
            self.shippo.detailBoard.update_target(ship)
            self.shippo.viewBox.follow(ship)

    def handle(self, event):
        et = event.type
        if et == pygame.MOUSEBUTTONDOWN:
            worldX, worldY = self.shippo.viewBox.posScreen2world(event.pos)
            if event.button == 3: # RClick
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # print 'C-Rclick'
                    for ship,sp in self.selected:
                        # self.instructions.append(
                        #         'StartRotatingTo %d %d %.2f %.2f' % (self.shippo.t, ship.id, worldX, worldY))
                        epos = self.shippo.viewBox.posScreen2world(event.pos)

                        for target in self.shippo.ships:
                            target.rect.collidepoint(event.pos)
                            if (target.position - epos).length < target.hitRadius * 2:
                                self.instructions.append(
                                        'Attack %d %d %d' % (self.shippo.t, ship.id, target.id))
                                break
                        else:
                                self.instructions.append(
                                        'Attack %d %d %d' % (self.shippo.t, ship.id, 0))
                else:
                    # print 'Rclick'
                    for ship,sp in self.selected:
                        self.instructions.append(
                                'MoveTo %d %d %.2f %.2f' % (self.shippo.t, ship.id, worldX, worldY))
        elif et == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if event.mod & pygame.KMOD_SHIFT:
                    for ship, sp in self.selected:
                        self.instructions.append(
                                'StopRotating %d %d' % (self.shippo.t, ship.id))
                else:
                    for ship, sp in self.selected:
                        self.instructions.append(
                                'Stop %d %d' % (self.shippo.t, ship.id))
            elif event.key in (K_1, K_2, K_3, K_4, K_5):
                id = event.key - K_1 + 6
                add = event.mod & KMOD_SHIFT
                for ship in self.ships:
                    if ship.id == id:
                        self.select(ship, add)
            elif event.key == K_c:
                for ship,sp in self.selected:
                    ship._show_debug = not ship._show_debug
            elif event.key == K_a and event.mod & KMOD_CTRL:
                for ship in self.ships:
                    self.select(ship, 1)

    def fetch_instruction(self):
        if self.instructions:
            instruction = Instruction(self, self.instructions.pop(0))
        else:
            instruction = None
        return instruction
