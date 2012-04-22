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
    def __init__(self, faction, port):
        self.name = None
        self.color = pygame.Color(0, 0, 0, 0xff)
        self.id = self.faction = faction
        self.ships = []
        self.resources = []
        self.instructions = []

        self.init_server(port)

    def clear(self):
        self.instructions = []

    def init_server(self, port):
        server = Socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', port))
        server.listen(1)
        server.settimeout(0.0)
        self.server = server

        self.connected = False
        self.reciever = None
        self.rfile = self.wfile = None
        self.instLock = threading.Lock()

    def fetch_instruction(self):
        # fetch one instruction in the instruction queue
        self.instLock.acquire()
        if self.instructions:
            instruction = Instruction(self, self.instructions.pop(0))
        else:
            instruction = None
        self.instLock.release()
        return instruction

    def recieve_instructions(self, lock):
        # recieve all instructions sent by the AI
        while 1:
            inst = self.rfile.readline()
            if inst is None:
                # connection lost
                self.close()
                break
            lock.acquire()
            self.instructions.append(inst.rstrip())
            lock.release()

    def close(self):
        print 'Connection lost with %s' % str(self.client.getpeername())
        self.connected = False
        self.client.close()

    def connect(self):
        # try to connect, return True if success
        # DUMMY
        return True
        try:
            client, addr = self.server.accept()
            client.settimeout(0.0)
            self.client = client
            self.addr = addr
            self.rfile = self.client.makefile('r')
            self.wfile = self.client.makefile('w')
            print 'Connected to %s' % str(self.client.getpeername())
            self.connected = True
            self.reciever = threading.Thread(target=self.recieve_instructions, 
                    args=(self.instLock,))
            self.reciever.start()

            # get AI info
            while 1:
                inst = self.fetch_instruction()
                if inst and inst.cmd == 'Info':
                    name, r, g, b = inst.args
                    self.color = pygame.Color(*map(int, (r, g, b, 0xff)))
                    self.name = name
                    break
                sleep(0.05)
        except socket.error:
            return False
        return True

    def iteration(self, shippo):
        data = shippo.to_rawstr(self.faction)
        self.send_instruction('Iteration\n%s' % (data,))

    def send_instruction(self, instruction):
        # call the AI's iteration
        # DUMMY
        return
        try:
            self.wfile.write(instruction)
        except socket.error:
            print 'Connection to AI %s lost' % (self.name,)
            self.close()

class HumanPlayer(Player):
    def __init__(self, faction):
        Player.__init__(self, faction, 0)
        self.name = 'HumanPlayer'
        self.color = pygame.Color(0, 0xff, 0, 0xff)
        self.shippo = None
        self.selected = set()
        self.bindedShips =  set()

    def selector(self, ship):
        def select_callback(event):
            if event.button == 1:
                add = pygame.key.get_mods() & pygame.KMOD_SHIFT
                if ship.faction == self.faction:
                    self.select(ship, add)
        return select_callback

    def mark_attack_er(self, target):
        def mark_attack(event):
            for ship in self.selected:
                self.instructions.append('Attack %d %d %d' % (self.shippo.currentSec, ship.id, target.id))
                self.marked = 1
            return True
        return mark_attack

    def init_server(self, port):
        self.connected = False

    def connect(self):
        self.connected = True
        return True

    def iteration(self, shippo):
        self.shippo = shippo
        for ship in shippo.ships:
            if ship not in self.bindedShips:
                if ship.faction == self.faction:
                    ship.button.bind(Button.Press, self.selector(ship))
                else:
                    ship.button.bind(Button.Press, self.mark_attack_er(ship))
                print 'HumanPlayer bind ', ship
                self.bindedShips.add(ship)

    def step(self):
        if not self.shippo: return
        viewBox = self.shippo.viewBox

    def select(self, ship, add=0):
        if add:
            self.selected.add(ship)
        else:
            for ship1 in self.selected:
                del self.shippo.visualSprites[:]
            self.selected = set([ship])
        if self.shippo:
            self.shippo.visualSprites.append(visual.SelectedShip(ship))
            self.shippo.detailBoard.update_target(ship)
            self.shippo.viewBox.follow(ship)

    def handle(self, event):
        et = event.type
        if et == pygame.MOUSEBUTTONDOWN:
            worldX, worldY = self.shippo.viewBox.posScreen2world(event.pos)
            if event.button == 3: # RClick
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    print 'C-Rclick'
                    for ship in self.selected:
                        # self.instructions.append(
                        #         'StartRotatingTo %d %d %.2f %.2f' % (self.shippo.currentSec, ship.id, worldX, worldY))
                        epos = self.shippo.viewBox.posScreen2world(event.pos)

                        for target in self.shippo.ships:
                            target.rect.collidepoint(event.pos)
                            if (target.position - epos).length < target.hitRadius * 2:
                                self.instructions.append(
                                        'Attack %d %d %d' % (self.shippo.currentSec, ship.id, target.id))
                                break
                        else:
                                self.instructions.append(
                                        'Attack %d %d %d' % (self.shippo.currentSec, ship.id, 0))
                else:
                    print 'Rclick'
                    for ship in self.selected:
                        self.instructions.append(
                                'MoveTo %d %d %.2f %.2f' % (self.shippo.currentSec, ship.id, worldX, worldY))
        elif et == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if event.mod & pygame.KMOD_SHIFT:
                    for ship in self.selected:
                        self.instructions.append(
                                'StopRotating %d %d' % (self.shippo.currentSec, ship.id))
                else:
                    print 'stop'
                    for ship in self.selected:
                        self.instructions.append(
                                'Stop %d %d' % (self.shippo.currentSec, ship.id))
            elif event.key in (K_1, K_2, K_3, K_4, K_5):
                id = event.key - K_1 + 6
                add = event.mod & KMOD_SHIFT
                for ship in self.ships:
                    if ship.id == id:
                        self.select(ship, add)
            elif event.key == K_c:
                for ship in self.selected:
                    ship._show_debug = not ship._show_debug

    def fetch_instruction(self):
        if self.instructions:
            instruction = Instruction(self, self.instructions.pop(0))
            print 'fetch', instruction
        else:
            instruction = None
        return instruction
